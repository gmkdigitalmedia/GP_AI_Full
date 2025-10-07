#!/usr/bin/env python3
"""
Simple test to verify the Neural Monitoring System is working
"""
import requests
import json
import time

def test_server():
    print("Testing Neural Monitoring System...")
    
    # Test different ports
    base_url = None
    for port in range(8000, 8010):
        try:
            url = f"http://localhost:{port}"
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if 'Neural Monitoring System' in str(data.get('service', '')):
                    base_url = url
                    print(f"✅ Found Neural Monitoring System at {url}")
                    break
                else:
                    print(f"⚠️  Found other service at {url}: {data.get('service', 'Unknown')}")
        except:
            continue
    
    if not base_url:
        print("❌ Neural Monitoring System not found on ports 8000-8009")
        print("   Please start the server with: python3 main.py")
        return
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        health = response.json()
        print(f"Health Status: {health.get('status')}")
        print(f"Database: {health.get('database', 'unknown')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test patient registration
    try:
        patient_data = {
            "patient_id": "TEST-001",
            "name": "Test Patient",
            "age": 30,
            "stasis_pod_id": "POD-TEST-001",
            "mission_id": "TEST-MISSION",
            "voyage_duration_years": 5.0,
            "stasis_start_time": "2024-01-01T00:00:00Z"
        }
        
        response = requests.post(f"{base_url}/patients", json=patient_data)
        if response.status_code in [201, 400]:  # 201 = created, 400 = already exists
            print("✅ Patient registration endpoint working")
        else:
            print(f"❌ Patient registration failed: {response.status_code}")
            print(response.text)
            return
            
    except Exception as e:
        print(f"❌ Patient registration test failed: {e}")
        return
    
    # Test patient listing
    try:
        response = requests.get(f"{base_url}/patients")
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ Patient listing working ({len(patients)} patients)")
        else:
            print(f"❌ Patient listing failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Patient listing test failed: {e}")
        return
    
    # Test API docs
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print("❌ API documentation not accessible")
    except Exception as e:
        print(f"❌ API docs test failed: {e}")
    
    print(f"\n🎉 Neural Monitoring System is working!")
    print(f"   Server: {base_url}")
    print(f"   API Docs: {base_url}/docs")
    print(f"   To run full demo: python3 client_demo.py")
    print(f"   To run tests: python3 test_integration.py")

if __name__ == "__main__":
    test_server()