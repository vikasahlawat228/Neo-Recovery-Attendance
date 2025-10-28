#!/usr/bin/env python3
"""
Test script to verify Vercel deployment
Run this after deploying to Vercel to test the API endpoints
"""

import requests
import json

def test_vercel_deployment(base_url):
    """Test the Vercel deployment"""
    print(f"Testing Vercel deployment at: {base_url}")
    print("=" * 60)
    
    # Test 1: Health check (employees endpoint)
    try:
        print("1. Testing /api/employees endpoint...")
        response = requests.get(f"{base_url}/api/employees", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Found {len(data)} employees")
            if data:
                print(f"   Sample employee: {data[0]}")
        else:
            print(f"   ❌ Failed! Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network Error: {e}")
    
    print()
    
    # Test 2: Test attendance endpoint (with testing mode)
    try:
        print("2. Testing /api/attendance endpoint...")
        test_data = {
            "employee_id": 1,
            "testing_mode": True
        }
        response = requests.post(
            f"{base_url}/api/attendance", 
            json=test_data,
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Response: {data}")
        else:
            print(f"   ❌ Failed! Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network Error: {e}")
    
    print()
    
    # Test 3: Test today's attendance count
    try:
        print("3. Testing /api/attendance/today endpoint...")
        response = requests.get(f"{base_url}/api/attendance/today", timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Today's attendance count: {data.get('count', 'N/A')}")
        else:
            print(f"   ❌ Failed! Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network Error: {e}")

if __name__ == "__main__":
    # Replace with your actual Vercel URL
    vercel_url = input("Enter your Vercel deployment URL (e.g., https://your-app.vercel.app): ").strip()
    
    if not vercel_url:
        print("No URL provided. Exiting.")
        exit(1)
    
    if not vercel_url.startswith('http'):
        vercel_url = f"https://{vercel_url}"
    
    test_vercel_deployment(vercel_url)
