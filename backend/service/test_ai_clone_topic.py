#!/usr/bin/env python3
"""
Test script for AI Clone API
"""
import requests
import base64
import json
import time

def test_ai_clone_api():
    # API endpoint
    base_url = "http://192.168.30.206:8777"
    endpoint = f"{base_url}/api/v1/ai-clone/create-video-full-text-form"
    
    # Test data
    audio_file = "/home/quangnm/seadev_backend_backup/ai_service/voiceclone_tts/model_english/Brian.wav"
    image_file = "/home/quangnm/seadev_backend_backup/ai_service/Sonic/examples/image/leonnado.jpg"
    
    user_id = 1
    reference_text = "The thing always happens that you really believe in, and the belief in a thing makes it happen."
    target_text = "Hello, this is a test of the human clone API. I hope it works perfectly!"
    language = "english"
    dynamic_scale = 1.0
    
    print("=== Testing AI Clone API ===")
    print(f"Endpoint: {endpoint}")
    print(f"Audio file: {audio_file}")
    print(f"Image file: {image_file}")
    print(f"Reference text: {reference_text}")
    print(f"Target text: {target_text}")
    print(f"User ID: {user_id}")
    print(f"Language: {language}")
    print()
    
    try:
        # Prepare files and data for multipart form
        with open(audio_file, 'rb') as af, open(image_file, 'rb') as imf:
            files = {
                'reference_audio': ('Brian.wav', af, 'audio/wav'),
                'image': ('leonnado.jpg', imf, 'image/jpeg')
            }
            
            data = {
                'user_id': user_id,
                'reference_text': reference_text,
                'target_text': target_text,
                'language': language,
                'dynamic_scale': dynamic_scale
            }
            
            print("Sending request to AI Clone API...")
            start_time = time.time()
            
            response = requests.post(
                endpoint,
                files=files,
                data=data,
                timeout=600  # 10 minutes timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"Request completed in {duration:.2f} seconds")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print()
            
            if response.status_code == 200:
                result = response.json()
                print("=== SUCCESS ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                if result.get("success"):
                    print(f"\n✅ Video created successfully!")
                    print(f"Video ID: {result.get('video_id')}")
                    print(f"Session ID: {result.get('session_id')}")
                    print(f"Video URL: {result.get('video_url')}")
                    print(f"Video Filename: {result.get('video_filename')}")
                    print(f"Status: {result.get('status')}")
                    print(f"Total Processing Time: {result.get('total_processing_time')} seconds")
                else:
                    print(f"\n❌ Video creation failed!")
                    print(f"Error: {result.get('error')}")
                    print(f"Message: {result.get('message')}")
                
            else:
                print(f"=== ERROR {response.status_code} ===")
                try:
                    error_detail = response.json()
                    print(json.dumps(error_detail, indent=2, ensure_ascii=False))
                except:
                    print(response.text)
                    
    except requests.exceptions.Timeout:
        print("❌ Request timeout!")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_human_clone_service_directly():
    """Test Human Clone service directly to isolate issues"""
    print("\n=== Testing Human Clone Service Directly ===")
    
    # Files
    audio_file = "/home/quangnm/seadev_backend_backup/ai_service/voiceclone_tts/model_english/Brian.wav"
    image_file = "/home/quangnm/seadev_backend_backup/ai_service/Sonic/examples/image/leonnado.jpg"
    
    # Read and encode files
    with open(audio_file, 'rb') as f:
        audio_content = f.read()
        audio_base64 = base64.b64encode(audio_content).decode()
    
    with open(image_file, 'rb') as f:
        image_content = f.read()
        image_base64 = base64.b64encode(image_content).decode()
    
    # Payload
    payload = {
        "reference_audio_base64": audio_base64,
        "reference_text": "The thing always happens that you really believe in, and the belief in a thing makes it happen.",
        "target_text": "Hello, this is a test of the human clone API. I hope it works perfectly!",
        "image_base64": image_base64,
        "language": "english",
        "dynamic_scale": 1.0
    }
    
    # Call Human Clone service
    url = "http://192.168.30.206:8779/ai/human-clone/generate"
    
    try:
        print(f"Calling Human Clone service: {url}")
        start_time = time.time()
        
        response = requests.post(
            url,
            json=payload,
            timeout=600
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Request completed in {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("=== Human Clone Service SUCCESS ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"=== Human Clone Service ERROR {response.status_code} ===")
            try:
                error_detail = response.json()
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"❌ Error calling Human Clone service: {e}")

if __name__ == "__main__":
    # Test the full API first
    test_ai_clone_api()
    
    # Also test Human Clone service directly
    test_human_clone_service_directly()
