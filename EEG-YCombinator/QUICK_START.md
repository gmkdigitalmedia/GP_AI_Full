# Neural Monitoring System - Quick Start


## Super Quick Demo (One Command)

```bash
./run_demo.sh
```

This script will:
1. Install dependencies
2. Start the server (auto-selects available port)
3. Run the complete demonstration
4. Show you next steps

## Manual Steps

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Start Server
```bash
python3 main.py
```
The server will auto-select an available port and show you the URL.

### 3. Run Demo (in another terminal)
```bash
python3 client_demo.py
```
The client will auto-discover the server port.

### 4. Run Tests
```bash
python3 test_integration.py
```

## What You'll See

The demo will show:
- Patient registration
- EEG data ingestion  
- Mock data streaming
- Anomaly detection
- Statistical analysis
- Health monitoring

## Troubleshooting

**Dependency Conflicts**: The updated requirements.txt uses compatible versions

**Port Issues**: Server auto-detects available ports 8000-8009

**Python Command**: Use `python3` instead of `python`

**Permission Issues**: Make sure run_demo.sh is executable: `chmod +x run_demo.sh`

## API Documentation

Once the server is running, visit the URL it shows (e.g., http://localhost:8001/docs) for interactive API documentation.

## Architecture Highlights

- **FastAPI**: Auto-generated API docs, fast performance
- **SQLite**: Zero-config database (creates neural_monitoring.db)
- **Real-time Processing**: Background tasks for data streaming
- **Comprehensive Testing**: Full integration test suite
- **Production Ready**: Clean architecture, error handling, documentation