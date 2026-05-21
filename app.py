from flask import Flask, request, jsonify, send_from_directory, make_response
import os
import requests
from Posting import post_to_unipile

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Base directory for static files
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve static files for the root directory
@app.route('/')
def serve_index():
    return send_from_directory(ROOT_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Ensure the file exists before attempting to serve
    if os.path.isfile(os.path.join(ROOT_DIR, path)):
        return send_from_directory(ROOT_DIR, path)
    return jsonify({"error": "File Not Found", "path": path}), 404

# API Endpoint for LinkedIn Automation
@app.route('/api/post', methods=['POST', 'OPTIONS'])
def handle_post():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400
    
    account_id = data.get('account_id')
    text = data.get('text')
    
    if not account_id or not text:
        return jsonify({"success": False, "message": "Missing account_id or text"}), 400
    
    print(f"Triggering automation for account: {account_id}")
    
    # Trigger the posting logic in Posting.py
    result = post_to_unipile(account_id, text)
    
    if result.get("success"):
        return jsonify({
            "success": True, 
            "message": "Post successfully scheduled via Unipile",
            "data": result.get("data")
        })
    else:
        return jsonify({
            "success": False, 
            "message": f"Automation failed: {result.get('message')}"
        }), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def handle_login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Missing username or password"}), 400

    url = "https://api20.unipile.com:15048/api/v1/accounts"
    
    payload = {
        "provider": "LINKEDIN",
        "username": username,
        "password": password
    }
    
    headers = {
        "X-API-KEY": "GZ4Napww.06tYodoW/wclbYDfXer1uh0c0hwOt2JOaTz2b7spddg=",
        "accept": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # If it requires checkpoint or succeeds
        if response.status_code in [200, 202, 201]:
            return jsonify(response.json()), response.status_code
        else:
            return jsonify({
                "success": False,
                "message": response.text,
                "status": response.status_code
            }), response.status_code

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/solve_checkpoint', methods=['POST', 'OPTIONS'])
def handle_solve_checkpoint():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    data = request.json
    account_id = data.get('account_id')
    code = data.get('code')
    
    url = f"https://api20.unipile.com:15048/api/v1/accounts/{account_id}/solve"
    headers = {
        "X-API-KEY": "GZ4Napww.06tYodoW/wclbYDfXer1uh0c0hwOt2JOaTz2b7spddg=",
        "accept": "application/json"
    }
    
    try:
        response = requests.post(url, json={"code": code}, headers=headers)
        if response.ok:
            return jsonify(response.json()), response.status_code
        else:
            return jsonify({"message": response.text}), response.status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/status/<account_id>', methods=['GET', 'OPTIONS'])
def handle_status(account_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    url = f"https://api20.unipile.com:15048/api/v1/accounts/{account_id}"
    headers = {
        "X-API-KEY": "GZ4Napww.06tYodoW/wclbYDfXer1uh0c0hwOt2JOaTz2b7spddg=",
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.ok:
            return jsonify(response.json()), response.status_code
        else:
            return jsonify({"message": response.text}), response.status_code
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    print("--------------------------------------------------")
    print(f"LinkedIn AI Agent Backend Running from: {ROOT_DIR}")
    print("Accessible at http://localhost:8000")
    print("--------------------------------------------------")
    # Listen on 0.0.0.0 for broader accessibility
    app.run(debug=True, host='0.0.0.0', port=8000)
