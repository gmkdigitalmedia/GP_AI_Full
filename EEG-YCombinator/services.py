"""
Business logic services for the Neural Monitoring System
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import Patient, DataIngestion, PatientCreate, PatientSummary
from utils import calculate_adr, model_binary_example
import threading
import time

logger = logging.getLogger(__name__)

class PatientService:
    """Service for managing patient operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Create a new patient"""
        # Check if patient already exists
        existing = self.db.query(Patient).filter(
            Patient.patient_id == patient_data.patient_id
        ).first()
        
        if existing:
            raise ValueError(f"Patient with ID {patient_data.patient_id} already exists")
        
        # Create new patient
        patient = Patient(**patient_data.model_dump())
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        
        logger.info(f"Created patient: {patient.patient_id}")
        return patient
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID"""
        return self.db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()
    
    def list_patients(self, active_only: bool = True) -> List[Patient]:
        """List all patients"""
        query = self.db.query(Patient)
        if active_only:
            query = query.filter(Patient.is_active == True)
        return query.all()
    
    def update_last_data_received(self, patient_id: str, timestamp: datetime):
        """Update the last data received timestamp for a patient"""
        patient = self.get_patient(patient_id)
        if patient:
            patient.last_data_received = timestamp
            self.db.commit()
    
    def get_patient_summary(self, patient_id: str) -> Optional[PatientSummary]:
        """Get comprehensive patient summary"""
        patient = self.get_patient(patient_id)
        if not patient:
            return None
        
        # Calculate stasis duration
        stasis_duration = datetime.utcnow() - patient.stasis_start_time
        stasis_duration_hours = stasis_duration.total_seconds() / 3600
        
        # Get recent statistics
        recent_stats = self._get_recent_statistics(patient_id)
        
        # Determine health status
        health_status = self._determine_health_status(recent_stats)
        
        return PatientSummary(
            patient_id=patient.patient_id,
            name=patient.name,
            stasis_pod_id=patient.stasis_pod_id,
            is_active=patient.is_active,
            stasis_duration_hours=stasis_duration_hours,
            last_data_received=patient.last_data_received,
            recent_adr_mean=recent_stats.get('adr_mean'),
            recent_anomaly_count=recent_stats.get('anomaly_count', 0),
            health_status=health_status
        )
    
    def _get_recent_statistics(self, patient_id: str) -> Dict[str, Any]:
        """Get recent statistics for a patient (last 24 hours)"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        recent_data = self.db.query(DataIngestion).filter(
            DataIngestion.patient_id == patient_id,
            DataIngestion.timestamp >= cutoff_time
        ).all()
        
        if not recent_data:
            return {}
        
        # Calculate statistics
        adr_values = [d.adr_mean for d in recent_data if d.adr_mean is not None]
        anomaly_count = sum(d.anomaly_count for d in recent_data)
        
        return {
            'adr_mean': np.mean(adr_values) if adr_values else None,
            'anomaly_count': anomaly_count,
            'data_points': len(recent_data)
        }
    
    def _determine_health_status(self, stats: Dict[str, Any]) -> str:
        """Determine patient health status based on recent statistics"""
        if not stats:
            return "unknown"
        
        anomaly_count = stats.get('anomaly_count', 0)
        data_points = stats.get('data_points', 1)
        
        # Simple heuristic: if more than 10% of recent data shows anomalies
        anomaly_rate = anomaly_count / max(data_points, 1)
        
        if anomaly_rate > 0.15:
            return "critical"
        elif anomaly_rate > 0.08:
            return "warning"
        else:
            return "normal"

class DataIngestionService:
    """Service for handling EEG data ingestion and processing"""
    
    def __init__(self, db: Session):
        self.db = db
        self.patient_service = PatientService(db)
        # In-memory storage for real-time processing
        self.active_streams: Dict[str, Dict] = {}
        self.notification_accumulator: Dict[str, List] = {}
    
    def ingest_data(self, patient_id: str, timestamp: datetime, 
                   data: np.ndarray, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming EEG data"""
        try:
            # Validate patient exists
            patient = self.patient_service.get_patient(patient_id)
            if not patient:
                raise ValueError(f"Patient {patient_id} not found")
            
            # Validate data format
            if len(data.shape) != 2:
                raise ValueError("Data must be 2D array [channels x samples]")
            
            if data.shape[0] != 21:
                raise ValueError("Expected 21 EEG channels")
            
            # Process data
            processing_results = self._process_eeg_data(data)
            
            # Store ingestion record
            ingestion = DataIngestion(
                patient_id=patient_id,
                timestamp=timestamp,
                channels=data.shape[0],
                samples=data.shape[1],
                anomaly_count=processing_results['anomaly_count'],
                adr_mean=processing_results['adr_mean']
            )
            
            self.db.add(ingestion)
            self.db.commit()
            
            # Update patient last data received
            self.patient_service.update_last_data_received(patient_id, timestamp)
            
            # Add to notification accumulator
            self._add_to_notification_buffer(patient_id, processing_results)
            
            logger.info(f"Processed data for patient {patient_id}: "
                       f"{processing_results['anomaly_count']} anomalies, "
                       f"ADR mean: {processing_results['adr_mean']:.3f}")
            
            return {
                'status': 'success',
                'anomaly_count': processing_results['anomaly_count'],
                'adr_mean': processing_results['adr_mean'],
                'samples_processed': data.shape[1]
            }
            
        except Exception as e:
            logger.error(f"Error processing data for patient {patient_id}: {str(e)}")
            raise
    
    def _process_eeg_data(self, data: np.ndarray) -> Dict[str, Any]:
        """Process EEG data to extract features and anomalies"""
        # Calculate ADR (Alpha/Delta Ratio)
        adr_values = calculate_adr(data)
        adr_mean = float(np.mean(adr_values))
        
        # Generate binary anomaly predictions
        anomaly_mask = model_binary_example(data)
        anomaly_count = int(np.sum(anomaly_mask))
        
        return {
            'adr_mean': adr_mean,
            'adr_values': adr_values,
            'anomaly_count': anomaly_count,
            'anomaly_mask': anomaly_mask,
            'total_samples': data.shape[1]
        }
    
    def _add_to_notification_buffer(self, patient_id: str, results: Dict[str, Any]):
        """Add processing results to notification buffer"""
        if patient_id not in self.notification_accumulator:
            self.notification_accumulator[patient_id] = []
        
        self.notification_accumulator[patient_id].append({
            'timestamp': datetime.utcnow(),
            'anomaly_count': results['anomaly_count'],
            'adr_mean': results['adr_mean'],
            'total_samples': results['total_samples']
        })
    
    def get_accumulated_notifications(self, patient_id: str, 
                                    clear_buffer: bool = True) -> List[Dict[str, Any]]:
        """Get accumulated notifications for a patient"""
        notifications = self.notification_accumulator.get(patient_id, [])
        
        if clear_buffer and patient_id in self.notification_accumulator:
            self.notification_accumulator[patient_id] = []
        
        return notifications
    
    def start_mock_stream(self, patient_id: str) -> str:
        """Start a mock data stream for testing"""
        if patient_id in self.active_streams:
            raise ValueError(f"Stream already active for patient {patient_id}")
        
        stream_id = f"stream_{patient_id}_{int(time.time())}"
        self.active_streams[patient_id] = {
            'stream_id': stream_id,
            'active': True,
            'start_time': datetime.utcnow()
        }
        
        # Start background thread for mock data generation
        thread = threading.Thread(
            target=self._mock_data_generator,
            args=(patient_id,),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Started mock stream {stream_id} for patient {patient_id}")
        return stream_id
    
    def stop_mock_stream(self, patient_id: str):
        """Stop mock data stream"""
        if patient_id in self.active_streams:
            self.active_streams[patient_id]['active'] = False
            del self.active_streams[patient_id]
        
        logger.info(f"Stopped mock stream for patient {patient_id}")
    
    def _mock_data_generator(self, patient_id: str):
        """Generate mock EEG data in background thread"""
        while (patient_id in self.active_streams and 
               self.active_streams[patient_id]['active']):
            
            try:
                # Generate mock EEG data (21 channels, 1280 samples = 5 seconds at 256 Hz)
                mock_data = np.random.randn(21, 1280) * 50  # Typical EEG amplitude range
                
                # Add some realistic EEG patterns
                t = np.linspace(0, 5, 1280)  # 5 seconds
                for ch in range(21):
                    # Add alpha rhythm (~10 Hz)
                    alpha = 10 * np.sin(2 * np.pi * 10 * t)
                    # Add some delta activity (~2 Hz)  
                    delta = 20 * np.sin(2 * np.pi * 2 * t)
                    mock_data[ch, :] += alpha + delta
                
                # Process the data
                self.ingest_data(
                    patient_id=patient_id,
                    timestamp=datetime.utcnow(),
                    data=mock_data,
                    metadata={'source': 'mock_stream'}
                )
                
                # Wait 5 seconds before next chunk
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in mock data generator for {patient_id}: {str(e)}")
                break
        
        logger.info(f"Mock data generator stopped for patient {patient_id}")

class StatisticsService:
    """Service for computing and retrieving patient statistics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def compute_statistics(self, patient_id: str, start_time: datetime, 
                         end_time: datetime, metrics: List[str]) -> Dict[str, Any]:
        """Compute statistics for a patient over a time range"""
        # Get data ingestion records
        data_records = self.db.query(DataIngestion).filter(
            DataIngestion.patient_id == patient_id,
            DataIngestion.timestamp >= start_time,
            DataIngestion.timestamp <= end_time
        ).order_by(DataIngestion.timestamp).all()
        
        if not data_records:
            return {'message': 'No data available for the specified time range'}
        
        results = {}
        
        if 'adr' in metrics:
            adr_values = [r.adr_mean for r in data_records if r.adr_mean is not None]
            if adr_values:
                results['adr'] = {
                    'mean': float(np.mean(adr_values)),
                    'std': float(np.std(adr_values)),
                    'min': float(np.min(adr_values)),
                    'max': float(np.max(adr_values)),
                    'count': len(adr_values)
                }
        
        if 'anomalies' in metrics:
            total_anomalies = sum(r.anomaly_count for r in data_records)
            total_samples = sum(r.samples for r in data_records)
            
            results['anomalies'] = {
                'total_anomalies': total_anomalies,
                'total_samples': total_samples,
                'anomaly_rate': total_anomalies / total_samples if total_samples > 0 else 0,
                'data_points': len(data_records)
            }
        
        results['time_range'] = {
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'duration_hours': (end_time - start_time).total_seconds() / 3600
        }
        
        return results
    
    def get_recent_trends(self, patient_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get recent trends for a patient"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        return self.compute_statistics(
            patient_id=patient_id,
            start_time=start_time,
            end_time=end_time,
            metrics=['adr', 'anomalies']
        )