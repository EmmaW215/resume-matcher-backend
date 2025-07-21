#!/usr/bin/env python3
"""
Test script to verify CORS configuration
"""
import requests
import json

def test_cors_config():
    """Test CORS configuration with different origins"""
    
    # Test origins
    test_origins = [
        "https://matchwise-ai.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "https://invalid-domain.com"  # This should be blocked
    ]
    
    backend_url = "https://resume-matcher-backend-rrrw.onrender.com"
    
    print("Testing CORS configuration...")
    print("=" * 50)
    
    for origin in test_origins:
        try:
            headers = {
                'Origin': origin,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            # Test preflight request
            response = requests.options(f"{backend_url}/api/compare", headers=headers)
            
            if response.status_code == 200:
                print(f"✅ {origin} - CORS allowed")
            else:
                print(f"❌ {origin} - CORS blocked (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ {origin} - Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("CORS test completed!")

if __name__ == "__main__":
    test_cors_config() 