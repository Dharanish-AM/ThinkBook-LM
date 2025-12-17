import urllib.request
import urllib.parse
import json
import os
import sys

BASE_URL = "http://localhost:8000/api"
TEST_DIR = os.path.dirname(os.path.abspath(__file__))

def post_multipart(url, fields, files):
    boundary = '----------Boundary123456789'
    data = []
    
    for key, value in fields.items():
        data.append(f'--{boundary}'.encode())
        data.append(f'Content-Disposition: form-data; name="{key}"'.encode())
        data.append(b'')
        data.append(str(value).encode())
        
    for key, (filename, content, mime_type) in files.items():
        data.append(f'--{boundary}'.encode())
        data.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"'.encode())
        data.append(f'Content-Type: {mime_type}'.encode())
        data.append(b'')
        data.append(content)
        
    data.append(f'--{boundary}--'.encode())
    data.append(b'')
    
    body = b'\r\n'.join(data)
    req = urllib.request.Request(url, data=body)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def post_form(url, data):
    encoded_data = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=encoded_data)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def test_upload(filename):
    filepath = os.path.join(TEST_DIR, filename)
    print(f"Uploading {filename}...")
    with open(filepath, "rb") as f:
        content = f.read()
    
    status, response = post_multipart(
        f"{BASE_URL}/upload_file", 
        {}, 
        {"file": (filename, content, "text/plain")}
    )
    
    if status == 200:
        print(f"✅ Upload success: {response}")
        return True
    else:
        print(f"❌ Upload failed: {status} - {response}")
        return False

def test_query(question):
    print(f"Querying: '{question}'...")
    status, response = post_form(f"{BASE_URL}/query", {"q": question, "k": 4})
    
    if status == 200:
        answer = response.get("answer", "")
        print(f"✅ Answer: {answer}")
        return answer
    else:
        print(f"❌ Query failed: {status} - {response}")
        return ""

def get_mime_type(filename):
    ext = filename.lower().split('.')[-1]
    mime_types = {
        'txt': 'text/plain',
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'wav': 'audio/wav',
        'mp3': 'audio/mpeg',
        'mp4': 'video/mp4',
        'mkv': 'video/x-matroska'
    }
    return mime_types.get(ext, 'application/octet-stream')

def main():
    sample_files = [
        "sample_notes.txt",
        "sample_document.pdf", 
        "sample_image.png",
        "sample_audio.wav",
        "sample_video.mp4"
    ]

    print("=== 1. Testing File Uploads ===")
    results = {}
    for filename in sample_files:
        if not os.path.exists(os.path.join(TEST_DIR, filename)):
            print(f"⚠️ Skipping {filename} (not found)")
            continue
            
        print(f"\nProcessing {filename}...")
        
        # Read file with generic binary mode
        filepath = os.path.join(TEST_DIR, filename)
        with open(filepath, "rb") as f:
            content = f.read()
            
        mime_type = get_mime_type(filename)
        status, response = post_multipart(
            f"{BASE_URL}/upload_file", 
            {}, 
            {"file": (filename, content, mime_type)}
        )
        
        if status == 200:
            print(f"✅ Upload success: {filename}")
            results[filename] = "Success"
        else:
            print(f"❌ Upload failed: {filename} ({status}) - {response}")
            results[filename] = f"Failed ({status})"

    print("\n=== 2. Testing Retrieval (sample_notes.txt) ===")
    # specific queries for the text file we know the content of
    test_query("What is AWS VPC Peering?")
    test_query("What is OAuth used for?")

    print("\n=== Test Summary ===")
    for fname, res in results.items():
        print(f"{fname}: {res}")

if __name__ == "__main__":
    main()
