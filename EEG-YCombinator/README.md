# Neural Monitoring System

A FastAPI-based system for monitoring patients in stasis during deep-space voyages. This system provides real-time EEG data ingestion, anomaly detection, and statistical analysis for neural health monitoring.

## Features

- **Patient Registration**: Register and manage patients in stasis
- **EEG Data Ingestion**: Real-time processing of 21-channel EEG data
- **Anomaly Detection**: Binary classification for neural anomaly detection
- **Alpha/Delta Ratio (ADR)**: Automated calculation of ADR for sleep depth monitoring
- **Statistics & Trends**: Comprehensive statistical analysis and trend tracking
- **Notification System**: Accumulates alerts for ground control
- **Mock Data Streaming**: Built-in test data generation for development

## Quick Start

### Prerequisites

- Python 3.8+
- All dependencies listed in `requirements.txt`

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the API server:**
   ```bash
   python main.py
   ```

   The server will start at `http://localhost:8000`

3. **View API documentation:**
   Open `http://localhost:8000/docs` in your browser for interactive API documentation

### Running the Demo

Run the complete demonstration:
```bash
python client_demo.py
```

This will demonstrate all key features:
- Patient registration
- EEG data ingestion
- Mock data streaming
- Statistics computation
- Notification system

### Running Tests

Run integration tests to verify functionality:
```bash
python test_integration.py
```

## API Endpoints

### Health Check
- `GET /health` - Check API health and database connectivity

### Patient Management
- `POST /patients` - Register a new patient
- `GET /patients` - List all patients
- `GET /patients/{patient_id}` - Get patient details
- `GET /patients/{patient_id}/summary` - Get patient summary with health status

### Data Ingestion
- `POST /data/ingest` - Ingest EEG data for processing
- `POST /data/stream/start/{patient_id}` - Start mock data stream
- `POST /data/stream/stop/{patient_id}` - Stop mock data stream
- `GET /data/notifications/{patient_id}` - Get accumulated notifications

### Statistics
- `POST /statistics/compute` - Compute statistics for a time range
- `GET /statistics/trends/{patient_id}` - Get recent trends

## Data Format

### EEG Data Structure
The system expects EEG data in the following format:
- **Shape**: `[channels, samples]` where channels = 21
- **Type**: Float32 array
- **Sampling Rate**: 256 Hz (configurable)
- **Typical Range**: ±100 μV

### Example EEG Data Ingestion
```python
import numpy as np
import requests

# Generate 21-channel EEG data (5 seconds at 256 Hz)
eeg_data = np.random.randn(21, 1280) * 50

# Ingest data
response = requests.post("http://localhost:8000/data/ingest", json={
    "patient_id": "STASIS-001",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": eeg_data.tolist(),
    "metadata": {"source": "monitoring_system"}
})
```

## Patient Registration

Register a new patient:
```python
patient_data = {
    "patient_id": "STASIS-001",
    "name": "Commander Sarah Chen",
    "age": 34,
    "stasis_pod_id": "POD-ALPHA-01",
    "mission_id": "KEPLER-442B",
    "voyage_duration_years": 12.5,
    "medical_history": {
        "allergies": ["penicillin"],
        "chronic_conditions": [],
        "medications": []
    },
    "risk_factors": ["family_history_epilepsy"],
    "stasis_start_time": "2024-01-01T00:00:00Z"
}

response = requests.post("http://localhost:8000/patients", json=patient_data)
```

## Architecture

### Components
- **FastAPI**: Web framework for REST API
- **SQLite**: Patient data storage (easy local setup)
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **NumPy/SciPy**: Signal processing and statistics
- **Background Tasks**: Asynchronous data processing

### Data Flow
1. EEG data ingested via REST API
2. Data validated and processed using `utils.py` functions
3. Anomaly detection and ADR calculation performed
4. Results stored in database
5. Statistics computed on demand
6. Notifications accumulated for ground control

### Database Schema
- **patients**: Patient information and metadata
- **data_ingestions**: Record of processed EEG data with results

## Configuration

Key settings can be modified in the code:
- Database location: `neural_monitoring.db`
- EEG parameters: 21 channels, 256 Hz sampling rate
- Processing windows: 2-second windows with 1-second overlap
- Notification intervals: Configurable per patient

## Development

### Code Structure
```
├── main.py              # FastAPI application and endpoints
├── models.py            # Database models and Pydantic schemas
├── services.py          # Business logic services
├── utils.py             # Signal processing utilities (provided)
├── client_demo.py       # Complete demonstration script
├── test_integration.py  # Integration test suite
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Features
1. **Models**: Add new Pydantic schemas in `models.py`
2. **Services**: Implement business logic in `services.py`
3. **Endpoints**: Add API routes in `main.py`
4. **Tests**: Update `test_integration.py`

### Signal Processing
The system uses the provided `utils.py` functions:
- `calculate_adr()`: Alpha/Delta Ratio computation
- `model_binary_example()`: Mock anomaly detection
- `calculate_stft_psd()`: Power spectral density analysis

## Production Considerations

For production deployment, consider:
- **Database**: PostgreSQL instead of SQLite
- **Message Queue**: Kafka/Redis for data streaming
- **Monitoring**: Prometheus/Grafana for system monitoring
- **Security**: API key authentication, HTTPS
- **Scaling**: Horizontal scaling with load balancer
- **Data Storage**: Time-series database (InfluxDB) for EEG data

## API Documentation

Complete interactive API documentation is available at:
`http://localhost:8000/docs`

This includes:
- All endpoint definitions
- Request/response schemas
- Example requests
- Authentication details
- Parameter descriptions

## Troubleshooting

### Common Issues

1. **Database errors**: Delete `neural_monitoring.db` to reset
2. **Port conflicts**: Change port in `main.py` if 8000 is occupied
3. **Import errors**: Ensure all dependencies are installed
4. **Data format errors**: Verify EEG data shape is [21, samples]

### Logs
The system logs important events to console. Check logs for:
- Patient registration events
- Data processing results
- Error messages
- Stream start/stop events

## License

This project is part of a technical assessment and is intended for evaluation purposes only.