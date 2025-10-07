import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .ollama_client import OllamaClient

class MultimodalRAG:
    """Main RAG agent that orchestrates multimodal document processing and retrieval"""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize components
        self.processor = DocumentProcessor()
        self.vector_store = VectorStore(persist_directory=str(self.data_dir / "chroma_db"))
        self.llm_client = OllamaClient()

        # Chat history
        self.chat_history: List[Dict[str, str]] = []

        logging.info("MultimodalRAG initialized")

    def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """Process and ingest a document into the RAG system"""

        try:
            # Process the document
            processed_content = self.processor.process_file(file_path)

            if 'error' in processed_content:
                return {'success': False, 'error': processed_content['error']}

            # Extract text content for indexing
            text_content = self.processor.extract_text_content(processed_content)

            # For images, get AI description
            if processed_content.get('type') == 'image':
                images = self.processor.get_images_for_vision(processed_content)
                if images:
                    ai_description = self.llm_client.analyze_image(
                        images[0],
                        "Describe this image in detail, including any text, objects, people, and context you can see."
                    )
                    text_content = f"{text_content}\\n\\nAI Description: {ai_description}"

            # Generate summary and keywords
            summary = self.llm_client.summarize_document(text_content)
            keywords = self.llm_client.extract_keywords(text_content)

            # Prepare metadata
            metadata = {
                'filename': processed_content.get('filename', 'unknown'),
                'file_type': processed_content.get('type', 'unknown'),
                'file_size': processed_content.get('file_size', 0),
                'summary': summary,
                'keywords': keywords,
                'ingestion_id': str(uuid.uuid4())
            }

            # Add document to vector store
            doc_id = self.vector_store.add_document(
                content=text_content,
                metadata=metadata
            )

            return {
                'success': True,
                'document_id': doc_id,
                'filename': processed_content.get('filename'),
                'file_type': processed_content.get('type'),
                'summary': summary,
                'keywords': keywords
            }

        except Exception as e:
            logging.error(f"Document ingestion failed: {e}")
            return {'success': False, 'error': str(e)}

    def query(self,
              question: str,
              n_results: int = 5,
              include_chat_history: bool = True) -> Dict[str, Any]:
        """Query the RAG system"""

        try:
            # Search for relevant documents
            search_results = self.vector_store.search(
                query=question,
                n_results=n_results
            )

            if not search_results:
                return {
                    'answer': "I couldn't find any relevant documents to answer your question.",
                    'sources': [],
                    'context_used': 0
                }

            # Prepare messages for chat
            messages = []

            # Add chat history if requested
            if include_chat_history and self.chat_history:
                messages.extend(self.chat_history[-6:])  # Last 3 exchanges

            # Add current question
            messages.append({"role": "user", "content": question})

            # Get answer with context
            result = self.llm_client.answer_question(
                question=question,
                context_chunks=search_results,
                include_sources=True
            )

            # Update chat history
            self.chat_history.append({"role": "user", "content": question})
            self.chat_history.append({"role": "assistant", "content": result['answer']})

            # Keep history manageable
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]

            return result

        except Exception as e:
            logging.error(f"Query failed: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'sources': [],
                'context_used': 0
            }

    def chat(self, message: str) -> Dict[str, Any]:
        """Interactive chat with the RAG system"""

        # For now, treat chat the same as query
        # Could be enhanced with different behavior for conversational context
        return self.query(message, include_chat_history=True)

    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about ingested documents"""

        try:
            vector_stats = self.vector_store.get_stats()
            documents = self.vector_store.list_documents(limit=50)

            # Analyze document types
            type_counts = {}
            for doc in documents:
                doc_type = doc['metadata'].get('file_type', 'unknown')
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

            return {
                'total_documents': vector_stats.get('total_documents', 0),
                'document_types': type_counts,
                'recent_documents': documents[:10]  # Recent 10
            }

        except Exception as e:
            logging.error(f"Failed to get document stats: {e}")
            return {'error': str(e)}

    def list_documents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List ingested documents"""

        try:
            return self.vector_store.list_documents(limit=limit)
        except Exception as e:
            logging.error(f"Failed to list documents: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the system"""

        try:
            return self.vector_store.delete_document(doc_id)
        except Exception as e:
            logging.error(f"Failed to delete document: {e}")
            return False

    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []
        logging.info("Chat history cleared")

    def check_system_status(self) -> Dict[str, Any]:
        """Check the status of all system components"""

        try:
            # Check Ollama models
            model_status = self.llm_client.check_models_available()

            # Check vector store
            vector_stats = self.vector_store.get_stats()

            # Check document processor
            processor_formats = list(self.processor.supported_formats.keys())

            return {
                'ollama_models': model_status,
                'vector_store': vector_stats,
                'supported_formats': processor_formats,
                'chat_history_length': len(self.chat_history)
            }

        except Exception as e:
            logging.error(f"System status check failed: {e}")
            return {'error': str(e)}

    def bulk_ingest(self, directory_path: str, file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Ingest all supported files from a directory"""

        if not file_extensions:
            file_extensions = list(self.processor.supported_formats.keys())

        directory = Path(directory_path)
        if not directory.exists():
            return {'success': False, 'error': 'Directory not found'}

        results = {
            'success': True,
            'processed': [],
            'failed': [],
            'total_processed': 0,
            'total_failed': 0
        }

        try:
            # Find all supported files
            files_to_process = []
            for ext in file_extensions:
                files_to_process.extend(directory.glob(f"*.{ext}"))

            # Process each file
            for file_path in files_to_process:
                try:
                    result = self.ingest_document(str(file_path))
                    if result['success']:
                        results['processed'].append({
                            'filename': result['filename'],
                            'document_id': result['document_id'],
                            'summary': result['summary'][:100] + "..." if len(result['summary']) > 100 else result['summary']
                        })
                        results['total_processed'] += 1
                    else:
                        results['failed'].append({
                            'filename': file_path.name,
                            'error': result['error']
                        })
                        results['total_failed'] += 1

                except Exception as e:
                    results['failed'].append({
                        'filename': file_path.name,
                        'error': str(e)
                    })
                    results['total_failed'] += 1

            if results['total_failed'] > 0:
                results['success'] = False

            return results

        except Exception as e:
            logging.error(f"Bulk ingestion failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_processed': 0,
                'total_failed': 0
            }