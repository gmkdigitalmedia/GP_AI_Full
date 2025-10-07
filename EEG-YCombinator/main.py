"""
Neural Monitoring System API

A FastAPI-based system for monitoring patients in stasis during deep-space voyages.
Provides endpoints for patient registration, EEG data ingestion, and statistical analysis.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import (
    get_session_maker, PatientCreate, PatientResponse, PatientSummary,
    EEGDataIngestion, DataIngestionResponse, StatisticsRequest, StatisticsResponse
)
from services import PatientService, DataIngestionService, StatisticsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Neural Monitoring System",
    description="Deep-space neural monitoring system for stasis patients",
    version="1.0.0"
)

# Database dependency
SessionLocal = get_session_maker()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Global data ingestion service (for background processing)
_data_ingestion_service = None

def get_data_ingestion_service(db: Session = Depends(get_db)) -> DataIngestionService:
    global _data_ingestion_service
    if _data_ingestion_service is None:
        _data_ingestion_service = DataIngestionService(db)
    return _data_ingestion_service

# API Endpoints

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Neural Monitoring System is operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "service": "Neural Monitoring System",
            "version": "1.0.0",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "Neural Monitoring System",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Patient Management Endpoints

@app.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED, tags=["Patients"])
async def register_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new patient in the system.
    
    This endpoint allows registration of patients who will be monitored during stasis.
    Each patient must have a unique patient_id and valid stasis pod assignment.
    """
    try:
        patient_service = PatientService(db)
        patient = patient_service.create_patient(patient_data)
        return patient
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create patient")

@app.get("/patients", response_model=List[PatientResponse], tags=["Patients"])
async def list_patients(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all registered patients.
    
    - **active_only**: If True, only returns patients currently in active monitoring
    """
    try:
        patient_service = PatientService(db)
        patients = patient_service.list_patients(active_only=active_only)
        return patients
        
    except Exception as e:
        logger.error(f"Error listing patients: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list patients")

@app.get("/patients/{patient_id}", response_model=PatientResponse, tags=["Patients"])
async def get_patient(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific patient"""
    try:
        patient_service = PatientService(db)
        patient = patient_service.get_patient(patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving patient: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve patient")

@app.get("/patients/{patient_id}/summary", response_model=PatientSummary, tags=["Patients"])
async def get_patient_summary(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive patient summary including current health status.
    
    Returns patient information with:
    - Current health status (normal/warning/critical)
    - Recent anomaly detection statistics
    - ADR (Alpha/Delta Ratio) measurements
    - Stasis duration
    """
    try:
        patient_service = PatientService(db)
        summary = patient_service.get_patient_summary(patient_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get patient summary")

# Data Ingestion Endpoints

@app.post("/data/ingest", response_model=DataIngestionResponse, tags=["Data Ingestion"])
async def ingest_eeg_data(
    data: EEGDataIngestion,
    background_tasks: BackgroundTasks,
    ingestion_service: DataIngestionService = Depends(get_data_ingestion_service)
):
    """
    Ingest EEG data for a patient.
    
    This endpoint accepts EEG time-series data and processes it for:
    - Anomaly detection using binary classification
    - Alpha/Delta Ratio (ADR) calculation
    - Real-time monitoring alerts
    
    - **patient_id**: Patient identifier
    - **timestamp**: Data timestamp  
    - **data**: 2D array [channels x samples] - expects 21 EEG channels
    - **metadata**: Optional metadata about the recording
    
    The data is processed asynchronously and results stored for statistical analysis.
    """
    try:
        # Convert data to numpy array
        eeg_data = np.array(data.data, dtype=np.float32)
        
        # Process data synchronously for immediate response
        # In a production system, this might be queued for async processing
        result = ingestion_service.ingest_data(
            patient_id=data.patient_id,
            timestamp=data.timestamp,
            data=eeg_data,
            metadata=data.metadata
        )
        
        return DataIngestionResponse(
            status="success",
            message="EEG data processed successfully",
            patient_id=data.patient_id,
            timestamp=data.timestamp.isoformat(),
            samples=eeg_data.shape[1],
            anomaly_count=result['anomaly_count'],
            adr_mean=result['adr_mean']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error ingesting EEG data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process EEG data")

@app.post("/data/stream/start/{patient_id}", tags=["Data Ingestion"])
async def start_mock_stream(
    patient_id: str,
    ingestion_service: DataIngestionService = Depends(get_data_ingestion_service)
):
    """
    Start a mock EEG data stream for testing purposes.
    
    This creates a background process that generates realistic mock EEG data
    every 5 seconds. Useful for testing the ingestion pipeline and statistics.
    """
    try:
        stream_id = ingestion_service.start_mock_stream(patient_id)
        
        return {
            "status": "started",
            "patient_id": patient_id,
            "stream_id": stream_id,
            "message": "Mock EEG stream started - data will be generated every 5 seconds"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting mock stream: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start mock stream")

@app.post("/data/stream/stop/{patient_id}", tags=["Data Ingestion"])
async def stop_mock_stream(
    patient_id: str,
    ingestion_service: DataIngestionService = Depends(get_data_ingestion_service)
):
    """Stop the mock EEG data stream for a patient"""
    try:
        ingestion_service.stop_mock_stream(patient_id)
        
        return {
            "status": "stopped",
            "patient_id": patient_id,
            "message": "Mock EEG stream stopped"
        }
        
    except Exception as e:
        logger.error(f"Error stopping mock stream: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop mock stream")

@app.get("/data/notifications/{patient_id}", tags=["Data Ingestion"])
async def get_notifications(
    patient_id: str,
    clear_buffer: bool = True,
    ingestion_service: DataIngestionService = Depends(get_data_ingestion_service)
):
    """
    Get accumulated notification data for a patient.
    
    Returns all processing results accumulated since the last call.
    This simulates the notification service that would alert ground control.
    
    - **clear_buffer**: If True, clears the notification buffer after returning data
    """
    try:
        notifications = ingestion_service.get_accumulated_notifications(
            patient_id=patient_id,
            clear_buffer=clear_buffer
        )
        
        # Calculate summary statistics
        total_anomalies = sum(n['anomaly_count'] for n in notifications)
        total_samples = sum(n['total_samples'] for n in notifications)
        avg_adr = np.mean([n['adr_mean'] for n in notifications]) if notifications else 0
        
        return {
            "patient_id": patient_id,
            "notification_count": len(notifications),
            "summary": {
                "total_anomalies": total_anomalies,
                "total_samples": total_samples,
                "anomaly_rate": total_anomalies / total_samples if total_samples > 0 else 0,
                "average_adr": float(avg_adr)
            },
            "notifications": notifications
        }
        
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")

# Statistics Endpoints

@app.post("/statistics/compute", response_model=StatisticsResponse, tags=["Statistics"])
async def compute_statistics(
    request: StatisticsRequest,
    db: Session = Depends(get_db)
):
    """
    Compute neural monitoring statistics for a patient over a specified time range.
    
    Available metrics:
    - **adr**: Alpha/Delta Ratio statistics (mean, std, min, max)
    - **anomalies**: Anomaly detection statistics (total count, rate)
    
    Time range is limited to 7 days maximum for performance.
    """
    try:
        # Validate time range
        if (request.end_time - request.start_time).days > 7:
            raise HTTPException(
                status_code=400,
                detail="Time range cannot exceed 7 days"
            )
        
        stats_service = StatisticsService(db)
        statistics = stats_service.compute_statistics(
            patient_id=request.patient_id,
            start_time=request.start_time,
            end_time=request.end_time,
            metrics=request.metrics
        )
        
        return StatisticsResponse(
            patient_id=request.patient_id,
            start_time=request.start_time,
            end_time=request.end_time,
            statistics=statistics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error computing statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compute statistics")

@app.get("/statistics/trends/{patient_id}", tags=["Statistics"])
async def get_patient_trends(
    patient_id: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get recent statistical trends for a patient.
    
    - **hours**: Number of hours to look back (maximum 168 = 7 days)
    
    Returns trends over the specified time period for visualization.
    """
    try:
        if hours > 168:  # 7 days
            raise HTTPException(
                status_code=400,
                detail="Hours cannot exceed 168 (7 days)"
            )
        
        stats_service = StatisticsService(db)
        trends = stats_service.get_recent_trends(patient_id=patient_id, hours=hours)
        
        return {
            "patient_id": patient_id,
            "hours": hours,
            "timestamp": datetime.utcnow().isoformat(),
            "trends": trends
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trends")

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Find an available port
    def find_free_port():
        for port in range(8000, 8010):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return 8000  # fallback
    
    port = find_free_port()
    print(f"Starting server on http://localhost:{port}")
    print(f"API documentation available at: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)