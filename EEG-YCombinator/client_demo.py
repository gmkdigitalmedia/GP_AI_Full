"""
Client Demo Script for Neural Monitoring System

This script demonstrates all the key features of the API:
1. Patient registration
2. EEG data ingestion (manual and streaming)
3. Patient summaries and statistics
4. Notification system

Run this after starting the API server to see the system in action.
"""
import requests
import numpy as np
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any

class NeuralMonitoringClient:
    """Client for interacting with the Neural Monitoring System API"""
    
    def __init__(self, base_url: str = None):
        if base_url is None:
            # Auto-detect running server by checking for our specific API
            for port in range(8000, 8010):
                try:
                    test_url = f"http://localhost:{port}"
                    response = requests.get(f"{test_url}/health", timeout=1)
                    if response.status_code == 200:
                        health_data = response.json()
                        # Check if this is our Neural Monitoring System
                        if ('database' in health_data or 
                            'service' in health_data and 'Neural' in str(health_data.get('service', ''))):
                            base_url = test_url
                            break
                        # Also try checking if we can access a specific endpoint
                        try:
                            patients_response = requests.get(f"{test_url}/patients", timeout=1)
                            # If patients endpoint exists (even if empty), this is our API
                            if patients_response.status_code in [200, 422]:  # 422 is validation error, still our API
                                base_url = test_url
                                break
                        except:
                            pass
                except:
                    continue
            
            if base_url is None:
                base_url = "http://localhost:8000"  # fallback
        
        self.base_url = base_url
        self.session = requests.Session()
        print(f"Connecting to API at: {self.base_url}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def register_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new patient"""
        response = self.session.post(f"{self.base_url}/patients", json=patient_data)
        response.raise_for_status()
        return response.json()
    
    def list_patients(self, active_only: bool = True) -> list:
        """List all patients"""
        response = self.session.get(f"{self.base_url}/patients", params={"active_only": active_only})
        response.raise_for_status()
        return response.json()
    
    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """Get patient details"""
        response = self.session.get(f"{self.base_url}/patients/{patient_id}")
        response.raise_for_status()
        return response.json()
    
    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """Get patient summary with health status"""
        response = self.session.get(f"{self.base_url}/patients/{patient_id}/summary")
        response.raise_for_status()
        return response.json()
    
    def ingest_eeg_data(self, patient_id: str, eeg_data: np.ndarray, 
                       timestamp: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Ingest EEG data for a patient"""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        if metadata is None:
            metadata = {}
        
        data = {
            "patient_id": patient_id,
            "timestamp": timestamp,
            "data": eeg_data.tolist(),
            "metadata": metadata
        }
        
        response = self.session.post(f"{self.base_url}/data/ingest", json=data)
        response.raise_for_status()
        return response.json()
    
    def start_mock_stream(self, patient_id: str) -> Dict[str, Any]:
        """Start mock EEG data stream"""
        response = self.session.post(f"{self.base_url}/data/stream/start/{patient_id}")
        response.raise_for_status()
        return response.json()
    
    def stop_mock_stream(self, patient_id: str) -> Dict[str, Any]:
        """Stop mock EEG data stream"""
        response = self.session.post(f"{self.base_url}/data/stream/stop/{patient_id}")
        response.raise_for_status()
        return response.json()
    
    def get_notifications(self, patient_id: str, clear_buffer: bool = True) -> Dict[str, Any]:
        """Get accumulated notifications"""
        params = {"clear_buffer": clear_buffer}
        response = self.session.get(f"{self.base_url}/data/notifications/{patient_id}", 
                                  params=params)
        response.raise_for_status()
        return response.json()
    
    def compute_statistics(self, patient_id: str, start_time: str, end_time: str, 
                         metrics: list = None) -> Dict[str, Any]:
        """Compute statistics for a patient"""
        if metrics is None:
            metrics = ["adr", "anomalies"]
        
        data = {
            "patient_id": patient_id,
            "start_time": start_time,
            "end_time": end_time,
            "metrics": metrics
        }
        
        response = self.session.post(f"{self.base_url}/statistics/compute", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_trends(self, patient_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get patient trends"""
        params = {"hours": hours}
        response = self.session.get(f"{self.base_url}/statistics/trends/{patient_id}", 
                                  params=params)
        response.raise_for_status()
        return response.json()

def generate_mock_eeg_data(channels: int = 21, samples: int = 1280) -> np.ndarray:
    """Generate realistic mock EEG data"""
    # Start with random noise
    data = np.random.randn(channels, samples) * 10
    
    # Add realistic EEG patterns
    t = np.linspace(0, 5, samples)  # 5 seconds at 256 Hz
    
    for ch in range(channels):
        # Alpha rhythm (8-13 Hz, prominent in occipital regions)
        if ch >= 18:  # Back channels
            alpha = 15 * np.sin(2 * np.pi * 10 * t + np.random.random() * 2 * np.pi)
            data[ch, :] += alpha
        
        # Delta waves (0.5-4 Hz, sleep/anesthesia)
        delta = 25 * np.sin(2 * np.pi * 2 * t + np.random.random() * 2 * np.pi)
        data[ch, :] += delta
        
        # Add some beta activity (13-30 Hz)
        beta = 5 * np.sin(2 * np.pi * 20 * t + np.random.random() * 2 * np.pi)
        data[ch, :] += beta
    
    # Add some artifacts occasionally
    if np.random.random() < 0.1:
        artifact_start = np.random.randint(0, samples - 100)
        artifact_ch = np.random.randint(0, channels)
        data[artifact_ch, artifact_start:artifact_start+100] += np.random.randn(100) * 50
    
    return data

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")

def print_results(title: str, data: Dict[str, Any]):
    """Pretty print results"""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2, default=str))

def main():
    """Main demo function"""
    print("Neural Monitoring System - Client Demo")
    print("=" * 60)
    
    # Initialize client
    client = NeuralMonitoringClient()
    
    # Health check
    print_section("HEALTH CHECK")
    try:
        health = client.health_check()
        print_results("API Health Status", health)
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to API server!")
        print("Please start the server first with: python main.py")
        return
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return
    
    # Test patient registration
    print_section("PATIENT REGISTRATION")
    
    # Create test patients
    test_patients = [
        {
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
            "baseline_eeg_profile": {
                "alpha_frequency": 10.2,
                "alpha_power": 45.3
            },
            "risk_factors": ["family_history_epilepsy"],
            "stasis_start_time": (datetime.utcnow() - timedelta(hours=48)).isoformat()
        },
        {
            "patient_id": "STASIS-002", 
            "name": "Dr. Marcus Webb",
            "age": 42,
            "stasis_pod_id": "POD-BETA-02",
            "mission_id": "KEPLER-442B",
            "voyage_duration_years": 12.5,
            "medical_history": {},
            "baseline_eeg_profile": {},
            "risk_factors": [],
            "stasis_start_time": (datetime.utcnow() - timedelta(hours=72)).isoformat()
        }
    ]
    
    for patient_data in test_patients:
        try:
            result = client.register_patient(patient_data)
            print(f"✓ Registered patient: {result['patient_id']}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                print(f"Patient {patient_data['patient_id']} already exists - skipping")
            else:
                print(f"✗ Failed to register {patient_data['patient_id']}: {str(e)}")
        except Exception as e:
            print(f"✗ Error registering {patient_data['patient_id']}: {str(e)}")
    
    # List patients
    print_section("PATIENT LISTING")
    try:
        patients = client.list_patients()
        print(f"Found {len(patients)} active patients:")
        for patient in patients:
            print(f"  - {patient['patient_id']}: {patient['name']} "
                  f"(Pod: {patient['stasis_pod_id']})")
    except Exception as e:
        print(f"✗ Error listing patients: {str(e)}")
        return
    
    if not patients:
        print("No patients found - demo cannot continue")
        return
    
    # Use first patient for remaining demos
    demo_patient = patients[0]
    patient_id = demo_patient['patient_id']
    
    print(f"\nUsing patient {patient_id} for remaining demonstrations...")
    
    # Manual data ingestion
    print_section("MANUAL EEG DATA INGESTION")
    
    try:
        # Generate and ingest some test data
        for i in range(3):
            eeg_data = generate_mock_eeg_data()
            result = client.ingest_eeg_data(
                patient_id=patient_id,
                eeg_data=eeg_data,
                metadata={"source": "demo_client", "batch": i+1}
            )
            print(f"✓ Ingested batch {i+1}: {result['anomaly_count']} anomalies, "
                  f"ADR: {result['adr_mean']:.3f}")
            time.sleep(1)  # Small delay between batches
            
    except Exception as e:
        print(f"✗ Error ingesting data: {str(e)}")
    
    # Patient summary
    print_section("PATIENT SUMMARY")
    try:
        summary = client.get_patient_summary(patient_id)
        print_results("Patient Summary", summary)
    except Exception as e:
        print(f"✗ Error getting patient summary: {str(e)}")
    
    # Start mock streaming
    print_section("MOCK EEG STREAMING")
    try:
        result = client.start_mock_stream(patient_id)
        print_results("Stream Started", result)
        
        print("\nStreaming EEG data for 30 seconds...")
        print("(Data is generated every 5 seconds)")
        
        # Let it run for 30 seconds
        time.sleep(30)
        
        # Check notifications
        print("\nChecking accumulated notifications...")
        notifications = client.get_notifications(patient_id)
        print_results("Notifications", notifications)
        
        # Stop streaming
        result = client.stop_mock_stream(patient_id)
        print(f"✓ Stream stopped: {result['message']}")
        
    except Exception as e:
        print(f"✗ Error with mock streaming: {str(e)}")
    
    # Statistics computation
    print_section("STATISTICS COMPUTATION")
    try:
        # Compute statistics for the last hour
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        stats = client.compute_statistics(
            patient_id=patient_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            metrics=["adr", "anomalies"]
        )
        print_results("Statistics (Last Hour)", stats)
        
    except Exception as e:
        print(f"✗ Error computing statistics: {str(e)}")
    
    # Trends
    print_section("PATIENT TRENDS")
    try:
        trends = client.get_trends(patient_id, hours=1)
        print_results("Recent Trends", trends)
    except Exception as e:
        print(f"✗ Error getting trends: {str(e)}")
    
    # Final patient summary
    print_section("FINAL PATIENT STATUS")
    try:
        summary = client.get_patient_summary(patient_id)
        print_results("Updated Patient Summary", summary)
    except Exception as e:
        print(f"✗ Error getting final summary: {str(e)}")
    
    print_section("DEMO COMPLETE")
    print("The Neural Monitoring System demo has completed successfully!")
    print("\nKey features demonstrated:")
    print("✓ Patient registration and management")
    print("✓ Manual EEG data ingestion")
    print("✓ Automated mock data streaming")
    print("✓ Real-time anomaly detection")
    print("✓ Alpha/Delta Ratio (ADR) calculation")
    print("✓ Statistical analysis and trends")
    print("✓ Notification accumulation system")
    print("✓ Health status monitoring")
    
    print(f"\nAPI Documentation available at: http://localhost:8000/docs")
    print(f"Total patients in system: {len(patients)}")

if __name__ == "__main__":
    main()