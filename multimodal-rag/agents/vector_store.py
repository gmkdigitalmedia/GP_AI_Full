import chromadb
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import logging

class VectorStore:
    """ChromaDB-based vector store for multimodal RAG"""

    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="multimodal_documents",
            metadata={"hnsw:space": "cosine"}
        )

        logging.info(f"Vector store initialized at {self.persist_directory}")

    def add_document(self,
                    content: str,
                    metadata: Dict[str, Any],
                    doc_id: Optional[str] = None) -> str:
        """Add a document to the vector store"""

        if not doc_id:
            doc_id = str(uuid.uuid4())

        # Prepare metadata for ChromaDB (only string values allowed)
        chroma_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                chroma_metadata[key] = str(value)
            else:
                chroma_metadata[key] = json.dumps(value)

        try:
            # Add to collection
            self.collection.add(
                documents=[content],
                metadatas=[chroma_metadata],
                ids=[doc_id]
            )

            logging.info(f"Added document {doc_id} to vector store")
            return doc_id

        except Exception as e:
            logging.error(f"Failed to add document to vector store: {e}")
            raise

    def add_documents_batch(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add multiple documents in batch"""

        doc_ids = []
        contents = []
        metadatas = []

        for doc in documents:
            doc_id = doc.get('id', str(uuid.uuid4()))
            content = doc['content']
            metadata = doc.get('metadata', {})

            # Prepare metadata
            chroma_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    chroma_metadata[key] = str(value)
                else:
                    chroma_metadata[key] = json.dumps(value)

            doc_ids.append(doc_id)
            contents.append(content)
            metadatas.append(chroma_metadata)

        try:
            self.collection.add(
                documents=contents,
                metadatas=metadatas,
                ids=doc_ids
            )

            logging.info(f"Added {len(doc_ids)} documents to vector store")
            return doc_ids

        except Exception as e:
            logging.error(f"Failed to add documents batch to vector store: {e}")
            raise

    def search(self,
               query: str,
               n_results: int = 5,
               filter_metadata: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""

        try:
            # Prepare where clause for filtering
            where_clause = None
            if filter_metadata:
                where_clause = {}
                for key, value in filter_metadata.items():
                    where_clause[key] = {"$eq": str(value)}

            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )

            # Format results
            formatted_results = []

            if results['documents'] and len(results['documents']) > 0:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
                distances = results['distances'][0] if results['distances'] else [0.0] * len(documents)
                ids = results['ids'][0] if results['ids'] else [f"doc_{i}" for i in range(len(documents))]

                for i, (doc, metadata, distance, doc_id) in enumerate(zip(documents, metadatas, distances, ids)):
                    # Parse JSON metadata back
                    parsed_metadata = {}
                    for key, value in metadata.items():
                        try:
                            parsed_metadata[key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            parsed_metadata[key] = value

                    formatted_results.append({
                        'id': doc_id,
                        'content': doc,
                        'metadata': parsed_metadata,
                        'similarity_score': 1.0 - distance,  # Convert distance to similarity
                        'rank': i + 1
                    })

            logging.info(f"Search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logging.error(f"Search failed: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the vector store"""
        try:
            self.collection.delete(ids=[doc_id])
            logging.info(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to delete document {doc_id}: {e}")
            return False

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document by ID"""
        try:
            results = self.collection.get(ids=[doc_id], include=['documents', 'metadatas'])

            if results['documents'] and len(results['documents']) > 0:
                doc = results['documents'][0]
                metadata = results['metadatas'][0] if results['metadatas'] else {}

                # Parse JSON metadata back
                parsed_metadata = {}
                for key, value in metadata.items():
                    try:
                        parsed_metadata[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        parsed_metadata[key] = value

                return {
                    'id': doc_id,
                    'content': doc,
                    'metadata': parsed_metadata
                }

        except Exception as e:
            logging.error(f"Failed to get document {doc_id}: {e}")

        return None

    def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all documents in the vector store"""
        try:
            results = self.collection.get(limit=limit, include=['documents', 'metadatas'])

            documents = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    doc_content = results['documents'][i] if i < len(results['documents']) else ""
                    metadata = results['metadatas'][i] if i < len(results['metadatas']) else {}

                    # Parse JSON metadata back
                    parsed_metadata = {}
                    for key, value in metadata.items():
                        try:
                            parsed_metadata[key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            parsed_metadata[key] = value

                    documents.append({
                        'id': doc_id,
                        'content': doc_content[:200] + "..." if len(doc_content) > 200 else doc_content,
                        'metadata': parsed_metadata
                    })

            return documents

        except Exception as e:
            logging.error(f"Failed to list documents: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection.name,
                'persist_directory': str(self.persist_directory)
            }
        except Exception as e:
            logging.error(f"Failed to get stats: {e}")
            return {'error': str(e)}

    def clear_all(self) -> bool:
        """Clear all documents from the vector store"""
        try:
            # Get all document IDs
            results = self.collection.get()
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logging.info(f"Cleared {len(results['ids'])} documents from vector store")
            return True
        except Exception as e:
            logging.error(f"Failed to clear vector store: {e}")
            return False