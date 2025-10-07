"""
Integration Tests for Neural Monitoring System

This test suite validates all major functionality of the API.
Run this after starting the server to verify everything works correctly.
"""
import unittest
import requests
import numpy as np
import time
from datetime import datetime, timedelta
from client_demo import NeuralMonitoringClient, generate_mock_eeg_data

class TestNeuralMonitoringSystem(unittest.TestCase):
    """Integration tests for the Neural Monitoring System"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.client = NeuralMonitoringClient()  # Will auto-detect port
        cls.test_patient_id = "TEST-PATIENT-001"
        
        # Verify API is running
        try:
            health = cls.client.health_check()
            assert health['status'] == 'healthy'
        except Exception as e:
            raise RuntimeError(f"API server not running or unhealthy: {str(e)}")
    
    def setUp(self):
        """Set up for each test"""
        # Clean up any existing test patient
        try:
            self.client.get_patient(self.test_patient_id)
            # If patient exists, we'll work with it
        except requests.exceptions.HTTPError:
            # Patient doesn't exist, which is fine
            pass
    
    def test_01_health_check(self):
        """Test API health check"""
        health = self.client.health_check()
        self.assertEqual(health['status'], 'healthy')
        self.assertIn('database', health)
        self.assertIn('timestamp', health)
    
    def test_02_patient_registration(self):
        """Test patient registration"""
        patient_data = {
            "patient_id": self.test_patient_id,
            "name": "Test Patient",
            "age": 30,
            "stasis_pod_id": "TEST-POD-001",
            "mission_id": "TEST-MISSION",
            "voyage_duration_years": 5.0,
            "medical_history": {"test": "data"},
            "baseline_eeg_profile": {"alpha_freq": 10.0},
            "risk_factors": ["test_factor"],
            "stasis_start_time": datetime.utcnow().isoformat()
        }
        
        try:
            result = self.client.register_patient(patient_data)
            self.assertEqual(result['patient_id'], self.test_patient_id)
            self.assertEqual(result['name'], "Test Patient")
            self.assertTrue(result['is_active'])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                # Patient already exists, that's okay for tests
                pass
            else:
                raise
    
    def test_03_patient_retrieval(self):
        """Test patient retrieval"""
        # Ensure patient exists first
        self.test_02_patient_registration()
        
        patient = self.client.get_patient(self.test_patient_id)
        self.assertEqual(patient['patient_id'], self.test_patient_id)
        self.assertIn('name', patient)
        self.assertIn('is_active', patient)
    
    def test_04_patient_listing(self):
        """Test patient listing"""
        patients = self.client.list_patients()
        self.assertIsInstance(patients, list)
        
        # Should contain our test patient if it exists
        patient_ids = [p['patient_id'] for p in patients]
        # We don't assert test patient is there since other tests might run first
    
    def test_05_eeg_data_ingestion(self):
        """Test EEG data ingestion"""
        # Ensure patient exists
        self.test_02_patient_registration()
        
        # Generate test EEG data
        eeg_data = generate_mock_eeg_data(channels=21, samples=1280)
        
        result = self.client.ingest_eeg_data(
            patient_id=self.test_patient_id,
            eeg_data=eeg_data,
            metadata={"test": "integration_test"}
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['patient_id'], self.test_patient_id)
        self.assertEqual(result['samples'], 1280)
        self.assertIn('anomaly_count', result)
        self.assertIn('adr_mean', result)
        self.assertIsInstance(result['anomaly_count'], int)
        self.assertIsInstance(result['adr_mean'], (int, float))
    
    def test_06_patient_summary(self):
        """Test patient summary"""
        # Ensure patient exists and has some data
        self.test_05_eeg_data_ingestion()
        
        summary = self.client.get_patient_summary(self.test_patient_id)
        
        self.assertEqual(summary['patient_id'], self.test_patient_id)
        self.assertIn('health_status', summary)
        self.assertIn('stasis_duration_hours', summary)
        self.assertIn('recent_anomaly_count', summary)
        self.assertIn(summary['health_status'], ['normal', 'warning', 'critical', 'unknown'])
    
    def test_07_statistics_computation(self):
        """Test statistics computation"""
        # Ensure patient has data
        self.test_05_eeg_data_ingestion()
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        stats = self.client.compute_statistics(
            patient_id=self.test_patient_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            metrics=["adr", "anomalies"]
        )
        
        self.assertEqual(stats['patient_id'], self.test_patient_id)
        self.assertIn('statistics', stats)
        # Should have some data if ingestion worked
    
    def test_08_mock_streaming(self):
        """Test mock data streaming"""
        # Ensure patient exists
        self.test_02_patient_registration()
        
        # Start stream
        start_result = self.client.start_mock_stream(self.test_patient_id)
        self.assertEqual(start_result['status'], 'started')
        self.assertIn('stream_id', start_result)
        
        # Let it run for a few seconds
        time.sleep(8)  # Should generate at least one data point
        
        # Check notifications
        notifications = self.client.get_notifications(self.test_patient_id)
        self.assertEqual(notifications['patient_id'], self.test_patient_id)
        self.assertIn('summary', notifications)
        
        # Stop stream
        stop_result = self.client.stop_mock_stream(self.test_patient_id)
        self.assertEqual(stop_result['status'], 'stopped')
    
    def test_09_trends(self):
        """Test trends retrieval"""
        # Ensure patient has some data
        self.test_05_eeg_data_ingestion()
        
        trends = self.client.get_trends(self.test_patient_id, hours=1)
        
        self.assertEqual(trends['patient_id'], self.test_patient_id)
        self.assertEqual(trends['hours'], 1)
        self.assertIn('trends', trends)
    
    def test_10_error_handling(self):
        """Test error handling"""
        # Test non-existent patient
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.client.get_patient("NON-EXISTENT-PATIENT")
        self.assertEqual(context.exception.response.status_code, 404)
        
        # Test invalid EEG data
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            invalid_data = np.random.randn(10, 100)  # Wrong number of channels
            self.client.ingest_eeg_data(self.test_patient_id, invalid_data)
        self.assertEqual(context.exception.response.status_code, 400)
    
    def test_11_data_validation(self):
        """Test data validation"""
        # Test missing required fields in patient registration
        invalid_patient = {
            "patient_id": "INVALID-001",
            "name": "Invalid Patient"
            # Missing required fields
        }
        
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.client.register_patient(invalid_patient)
        self.assertEqual(context.exception.response.status_code, 422)  # Validation error
    
    def test_12_api_documentation(self):
        """Test API documentation is accessible"""
        response = requests.get(f"{self.client.base_url}/docs")
        self.assertEqual(response.status_code, 200)
        
        # Test OpenAPI schema
        response = requests.get(f"{self.client.base_url}/openapi.json")
        self.assertEqual(response.status_code, 200)
        
        schema = response.json()
        self.assertIn('openapi', schema)
        self.assertIn('paths', schema)

def run_integration_tests():
    """Run integration tests with detailed output"""
    print("Neural Monitoring System - Integration Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNeuralMonitoringSystem)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = failures == 0 and errors == 0
    print(f"\nOverall Result: {'PASS' if success else 'FAIL'}")
    
    return success

if __name__ == "__main__":
    run_integration_tests()