"""
Data models for the Neural Monitoring System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field
import json

Base = declarative_base()

# SQLAlchemy Models
class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    stasis_pod_id = Column(String, nullable=False)
    mission_id = Column(String, nullable=False)
    voyage_duration_years = Column(Float, nullable=False)
    medical_history = Column(JSON, default=dict)
    baseline_eeg_profile = Column(JSON, default=dict)
    risk_factors = Column(JSON, default=list)
    stasis_start_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    last_data_received = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DataIngestion(Base):
    __tablename__ = "data_ingestions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    channels = Column(Integer, nullable=False)
    samples = Column(Integer, nullable=False)
    anomaly_count = Column(Integer, default=0)
    adr_mean = Column(Float, nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class PatientCreate(BaseModel):
    patient_id: str = Field(..., description="Unique patient identifier")
    name: str = Field(..., description="Patient full name")
    age: int = Field(..., ge=0, le=150, description="Patient age")
    stasis_pod_id: str = Field(..., description="Stasis pod identifier")
    mission_id: str = Field(..., description="Mission identifier")
    voyage_duration_years: float = Field(..., gt=0, description="Expected voyage duration in years")
    medical_history: Optional[Dict[str, Any]] = Field(default_factory=dict)
    baseline_eeg_profile: Optional[Dict[str, Any]] = Field(default_factory=dict)
    risk_factors: Optional[List[str]] = Field(default_factory=list)
    stasis_start_time: datetime = Field(..., description="When stasis began")

class PatientResponse(BaseModel):
    id: int
    patient_id: str
    name: str
    age: int
    stasis_pod_id: str
    mission_id: str
    voyage_duration_years: float
    medical_history: Dict[str, Any]
    baseline_eeg_profile: Dict[str, Any]
    risk_factors: List[str]
    stasis_start_time: datetime
    is_active: bool
    last_data_received: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PatientSummary(BaseModel):
    patient_id: str
    name: str
    stasis_pod_id: str
    is_active: bool
    stasis_duration_hours: float
    last_data_received: Optional[datetime]
    recent_adr_mean: Optional[float]
    recent_anomaly_count: int
    health_status: str  # "normal", "warning", "critical"

class EEGDataIngestion(BaseModel):
    patient_id: str = Field(..., description="Patient identifier")
    timestamp: datetime = Field(..., description="Data timestamp")
    data: List[List[float]] = Field(..., description="EEG data [channels x samples]")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DataIngestionResponse(BaseModel):
    status: str
    message: str
    patient_id: str
    timestamp: str
    samples: int
    anomaly_count: int
    adr_mean: Optional[float]

class StatisticsRequest(BaseModel):
    patient_id: str
    start_time: datetime
    end_time: datetime
    metrics: List[str] = Field(default=["adr", "anomalies"], description="Metrics to compute")

class StatisticsResponse(BaseModel):
    patient_id: str
    start_time: datetime
    end_time: datetime
    statistics: Dict[str, Any]

# Database setup
def create_database():
    """Create SQLite database and tables"""
    engine = create_engine("sqlite:///neural_monitoring.db", echo=False)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session_maker():
    """Get SQLAlchemy session maker"""
    engine = create_database()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)