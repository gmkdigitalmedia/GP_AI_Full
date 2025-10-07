# Multimodal RAG System

A powerful **Retrieval Augmented Generation** system that processes multiple document types (PDFs, images, text files) and provides AI-powered question answering with **local Ollama models**.

## Features

**Multimodal Document Processing**
- PDFs (text extraction + embedded images)
- Images (JPG, PNG, GIF, etc.) with AI vision analysis
- Text files (TXT, DOCX)
- Automatic content summarization and keyword extraction

**Local AI Models (Ollama)**
- **Llama 3.2 Vision** - Multimodal image understanding
- **Llama 3.2** - Text generation and chat
- **Nomic Embed** - High-quality embeddings

**Smart Storage**
- **ChromaDB** vector database for semantic search
- Persistent storage with metadata indexing
- Fast similarity search with source attribution

**Easy-to-Use Interface**
- Beautiful web UI with drag-drop upload
- Real-time chat with document context
- Source citations and similarity scores
- System statistics and document management

## Quick Start

### 1. Run Setup (Installs Ollama + Models)
```bash
cd multimodal-rag
bash setup.sh
```

### 2. Start the System
```bash
python main.py
```

### 3. Open Web Interface
```
http://localhost:8000
```

## Project Structure

```
multimodal-rag/
├── main.py                    # FastAPI web server
├── agents/
│   ├── multimodal_rag.py     # Main RAG orchestrator
│   ├── document_processor.py # Multi-format document processing
│   ├── vector_store.py       # ChromaDB integration
│   └── ollama_client.py      # Local AI model client
├── templates/
│   └── index.html            # Web interface
├── data/                     # Vector database storage
├── uploads/                  # Document uploads
├── setup.sh                 # Automated setup script
└── requirements.txt          # Python dependencies
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload and process documents |
| `/query` | POST | Query documents with RAG |
| `/chat` | POST | Interactive chat with context |
| `/documents` | GET | List all documents |
| `/stats` | GET | System statistics |
| `/health` | GET | Health check |

## Usage Examples

### Upload Documents
- Drag & drop files in the web interface
- Or use API: `POST /upload` with file

### Ask Questions
```
"What are the main topics discussed in the uploaded documents?"
"Can you summarize the PDF I uploaded?"
"What does the chart in image.png show?"
"Compare the findings between document A and B"
```

### Chat with Context
- Maintains conversation history
- References previous questions
- Provides source citations with similarity scores

## Manual Installation

If the setup script doesn't work:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Pull models
ollama pull llama3.2-vision
ollama pull llama3.2
ollama pull nomic-embed-text

# Install Python dependencies
pip install -r requirements.txt

# Run the system
python main.py
```

## Perfect for Tutorials Because:

**Complete multimodal pipeline** - Shows real RAG implementation
**Local models** - No API keys needed, runs anywhere
**Modern stack** - FastAPI, ChromaDB, Ollama
**Production patterns** - Error handling, logging, API design
**Easy deployment** - Single setup script
**Extensible** - Clean architecture for adding features

## Potential Extensions

- **Bulk document ingestion** from folders
- **Advanced chunking strategies** for large documents
- **Multi-language support** with different models
- **Docker containerization** for easy deployment
- **Authentication & user management**
- **Document versioning** and update tracking
- **Custom embedding models** for domain-specific use cases

## System Requirements

- **Python 3.8+**
- **8GB+ RAM** (for Llama models)
- **4GB+ disk space** (for models and data)
- **Linux/macOS/WSL** (Ollama requirement)

Ready to build the future of document AI!