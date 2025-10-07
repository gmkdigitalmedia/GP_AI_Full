#!/bin/bash
# Multimodal RAG Setup Script

echo "Setting up Multimodal RAG with Ollama..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start Ollama service (if not running)
echo "Starting Ollama service..."
ollama serve &

# Wait a moment for service to start
sleep 3

# Pull required models
echo "Downloading Llama 3.2 Vision (multimodal)..."
ollama pull llama3.2-vision

echo "Downloading Llama 3.2 (text generation)..."
ollama pull llama3.2

echo "Downloading Nomic Embed (embeddings)..."
ollama pull nomic-embed-text

echo "Setup complete!"
echo ""
echo "To start the RAG system:"
echo "   python main.py"
echo ""
echo "Then open: http://localhost:8000"