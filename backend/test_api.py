#!/usr/bin/env python3
import requests
import json

def test_rag_endpoint():
    url = "http://localhost:8000/rag"
    payload = {"query": "General Appropriations Bill"}
    
    print("Testing /rag endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ Error!")
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_rag_endpoint()
