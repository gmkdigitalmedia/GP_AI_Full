# Manual Testing Instructions

## Quick Test Commands

### 1. Start the Server (Terminal 1)
```bash
cd /mnt/c/Users/ibm/Documents/SWE_Take_Home
python3 main.py
```
You should see:
```
Starting server on http://localhost:8001
API documentation available at: http://localhost:8001/docs
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### 2. Test the Server (Terminal 2)
```bash
cd /mnt/c/Users/ibm/Documents/SWE_Take_Home

# Simple health check
curl http://localhost:8001/health

# Expected response:
# {"status":"healthy","service":"Neural Monitoring System","version":"1.0.0","database":"connected","timestamp":"..."}
```

### 3. Run the Demo (Terminal 2)
```bash
python3 client_demo.py
```

### 4. Run Integration Tests (Terminal 2)
```bash
python3 test_integration.py
```

## Manual API Testing

### Register a Patient
```bash
curl -X POST http://localhost:8001/patients \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "DEMO-001",
    "name": "Demo Patient",
    "age": 35,
    "stasis_pod_id": "POD-DEMO-01",
    "mission_id": "DEMO-MISSION",
    "voyage_duration_years": 10.0,
    "stasis_start_time": "2024-01-01T00:00:00Z"
  }'
```

### List Patients
```bash
curl http://localhost:8001/patients
```

### Ingest EEG Data
```bash
curl -X POST http://localhost:8001/data/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "DEMO-001",
    "timestamp": "2024-01-01T10:00:00Z",
    "data": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
    "metadata": {"test": true}
  }'
```

### Get Patient Summary
```bash
curl http://localhost:8001/patients/DEMO-001/summary
```

## API Documentation

Visit: http://localhost:8001/docs

This provides:
- Interactive API testing
- Complete endpoint documentation
- Request/response schemas
- Example requests

## Troubleshooting

### Server Won't Start
1. Check dependencies: `pip3 install -r requirements.txt`
2. Check port availability: `netstat -tlnp | grep 800`
3. Kill existing processes: `pkill -f main.py`

### Connection Refused
1. Make sure server is running (should show "Uvicorn running...")
2. Check correct port (server shows which port it's using)
3. Try: `curl http://localhost:8001/health`

### Database Errors
1. Delete database file: `rm neural_monitoring.db`
2. Restart server

### Demo Script Issues
1. Make sure server is running first
2. Check client_demo.py is using correct port
3. Run: `python3 test_simple.py` to verify connectivity

## Expected Demo Output

The client demo should show:
```
============================================================
                        HEALTH CHECK                        
============================================================
✓ API is healthy

============================================================
                    PATIENT REGISTRATION                    
============================================================
✓ Registered patient: STASIS-001
✓ Registered patient: STASIS-002

============================================================
                      PATIENT LISTING                       
============================================================
Found 2 active patients:
  - STASIS-001: Commander Sarah Chen (Pod: POD-ALPHA-01)
  - STASIS-002: Dr. Marcus Webb (Pod: POD-BETA-02)

... (continues with data ingestion, streaming, statistics)
```

## File Structure Check

Make sure you have these files:
```
├── main.py              # Main FastAPI application
├── models.py            # Database models
├── services.py          # Business logic
├── utils.py             # Provided utilities (original)
├── client_demo.py       # Demo script
├── test_integration.py  # Integration tests
├── test_simple.py       # Simple connectivity test
├── requirements.txt     # Dependencies
├── README.md           # Full documentation
└── neural_monitoring.db # SQLite database (created automatically)
```

## Success Criteria

✅ Server starts without errors
✅ Health check returns "healthy" status
✅ Patient registration works
✅ EEG data ingestion processes successfully
✅ Statistics computation works
✅ API documentation is accessible
✅ Demo script completes successfully
✅ Integration tests pass