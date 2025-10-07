import ollama
import base64
import logging
from typing import List, Dict, Any, Optional
import json

class OllamaClient:
    """Client for interacting with local Ollama models"""

    def __init__(self):
        self.text_model = "llama3.2"  # For text generation
        self.vision_model = "llama3.2-vision"  # For multimodal analysis
        self.embedding_model = "nomic-embed-text"  # For embeddings

        logging.info("Ollama client initialized")

    def generate_text(self,
                     prompt: str,
                     context: Optional[str] = None,
                     max_tokens: int = 1000) -> str:
        """Generate text response using Ollama"""

        # Combine context and prompt
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\\n\\nQuestion: {prompt}\\n\\nAnswer:"

        try:
            response = ollama.generate(
                model=self.text_model,
                prompt=full_prompt,
                options={
                    'num_predict': max_tokens,
                    'temperature': 0.7,
                    'top_p': 0.9
                }
            )

            return response['response'].strip()

        except Exception as e:
            logging.error(f"Text generation failed: {e}")
            return f"Error generating response: {str(e)}"

    def analyze_image(self,
                     image_base64: str,
                     prompt: str = "Describe this image in detail") -> str:
        """Analyze image using vision model"""

        try:
            # Prepare the message for multimodal model
            response = ollama.generate(
                model=self.vision_model,
                prompt=prompt,
                images=[image_base64],
                options={
                    'temperature': 0.3,
                    'num_predict': 500
                }
            )

            return response['response'].strip()

        except Exception as e:
            logging.error(f"Image analysis failed: {e}")
            return f"Error analyzing image: {str(e)}"

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks"""

        embeddings = []

        try:
            for text in texts:
                response = ollama.embeddings(
                    model=self.embedding_model,
                    prompt=text
                )
                embeddings.append(response['embedding'])

            logging.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings

        except Exception as e:
            logging.error(f"Embedding generation failed: {e}")
            # Return dummy embeddings if fails
            return [[0.0] * 768 for _ in texts]

    def chat_with_context(self,
                         messages: List[Dict[str, str]],
                         context_documents: List[str] = None) -> str:
        """Chat with conversation context and RAG context"""

        try:
            # Prepare context
            system_message = "You are a helpful AI assistant with access to document content."

            if context_documents:
                context_text = "\\n\\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(context_documents)])
                system_message += f"\\n\\nRelevant documents:\\n{context_text}"

            # Prepare chat messages
            chat_messages = [{"role": "system", "content": system_message}]
            chat_messages.extend(messages)

            # Use Ollama chat API
            response = ollama.chat(
                model=self.text_model,
                messages=chat_messages,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_predict': 1000
                }
            )

            return response['message']['content'].strip()

        except Exception as e:
            logging.error(f"Chat failed: {e}")
            return f"Error in chat: {str(e)}"

    def summarize_document(self, content: str, max_length: int = 200) -> str:
        """Summarize document content"""

        prompt = f"""Please provide a concise summary of the following content in about {max_length} words:

{content[:4000]}  # Limit input length

Summary:"""

        try:
            response = ollama.generate(
                model=self.text_model,
                prompt=prompt,
                options={
                    'num_predict': max_length + 50,
                    'temperature': 0.3
                }
            )

            return response['response'].strip()

        except Exception as e:
            logging.error(f"Summarization failed: {e}")
            return f"Error summarizing: {str(e)}"

    def extract_keywords(self, content: str) -> List[str]:
        """Extract key topics/keywords from content"""

        prompt = f"""Extract the 5-10 most important keywords or topics from this content. Return only the keywords separated by commas:

{content[:2000]}

Keywords:"""

        try:
            response = ollama.generate(
                model=self.text_model,
                prompt=prompt,
                options={
                    'num_predict': 100,
                    'temperature': 0.3
                }
            )

            # Parse keywords from response
            keywords_text = response['response'].strip()
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]

            return keywords[:10]  # Limit to 10 keywords

        except Exception as e:
            logging.error(f"Keyword extraction failed: {e}")
            return []

    def answer_question(self,
                       question: str,
                       context_chunks: List[Dict[str, Any]],
                       include_sources: bool = True) -> Dict[str, Any]:
        """Answer question using RAG context"""

        # Prepare context from retrieved chunks
        context_texts = []
        sources = []

        for chunk in context_chunks:
            context_texts.append(chunk['content'])
            sources.append({
                'filename': chunk['metadata'].get('filename', 'Unknown'),
                'similarity': chunk.get('similarity_score', 0.0)
            })

        context_text = "\\n\\n".join([f"[Source {i+1}] {text}" for i, text in enumerate(context_texts)])

        # Generate answer
        prompt = f"""Based on the following context, please answer the question. If the answer cannot be found in the context, say so.

Context:
{context_text}

Question: {question}

Answer:"""

        try:
            response = ollama.generate(
                model=self.text_model,
                prompt=prompt,
                options={
                    'num_predict': 800,
                    'temperature': 0.5
                }
            )

            answer = response['response'].strip()

            result = {'answer': answer}

            if include_sources:
                result['sources'] = sources
                result['context_used'] = len(context_chunks)

            return result

        except Exception as e:
            logging.error(f"Question answering failed: {e}")
            return {
                'answer': f"Error answering question: {str(e)}",
                'sources': sources if include_sources else []
            }

    def check_models_available(self) -> Dict[str, bool]:
        """Check if required models are available"""

        models_status = {}

        try:
            # Get list of available models
            available_models = ollama.list()

            # Extract model names safely
            model_names = []
            models_list = available_models.get('models', [])

            for model in models_list:
                # Handle different response formats
                if isinstance(model, dict):
                    # Try different possible keys
                    name = model.get('name') or model.get('model') or model.get('id')
                    if name:
                        model_names.append(name)
                elif isinstance(model, str):
                    model_names.append(model)

            logging.info(f"Available models: {model_names}")

            # Check each required model
            models_status[self.text_model] = self.text_model in model_names
            models_status[self.vision_model] = self.vision_model in model_names
            models_status[self.embedding_model] = self.embedding_model in model_names

        except Exception as e:
            logging.error(f"Failed to check models: {e}")
            models_status = {
                self.text_model: False,
                self.vision_model: False,
                self.embedding_model: False,
                'error': str(e)
            }

        return models_status