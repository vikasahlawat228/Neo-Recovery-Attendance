#!/usr/bin/env python3
"""
Debug script for Vercel deployment
This will help identify what's causing the 500 error
"""

import requests
import json

def debug_vercel_deployment(base_url):
    """Debug the Vercel deployment step by step"""
    print(f"🔍 Debugging Vercel deployment at: {base_url}")
    print("=" * 60)
    
    # Test 1: Health check (should work even without Google Sheets)
    try:
        print("1. Testing /api/health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Health check passed - Function is running")
        else:
            print("   ❌ Health check failed")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network Error: {e}")
    
    print()
    
    # Test 2: Employees endpoint (this is where the error occurs)
    try:
        print("2. Testing /api/employees endpoint...")
        response = requests.get(f"{base_url}/api/employees", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Employees endpoint working")
        else:
            print("   ❌ Employees endpoint failed")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network Error: {e}")
    
    print()
    
    # Test 3: Check if it's a CORS issue
    try:
        print("3. Testing with CORS headers...")
        headers = {
            'Origin': 'https://your-frontend-domain.com',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{base_url}/api/employees", headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        
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
    
    debug_vercel_deployment(vercel_url)
