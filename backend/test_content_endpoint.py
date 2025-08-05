#!/usr/bin/env python
import requests
import json

def test_content_endpoint():
    url = "http://127.0.0.1:8000/api/books/books/32/content/"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"\nError Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection error - server might not be running")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_content_endpoint()