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

# ─── LinkedIn Target Search Endpoints ────────────────────────────────────────

UNIPILE_BASE  = "https://api20.unipile.com:15048/api/v1"
UNIPILE_KEY   = "GZ4Napww.06tYodoW/wclbYDfXer1uh0c0hwOt2JOaTz2b7spddg="
UNIPILE_ACCT  = "roVMOMXnT3GIbCSE6b-49Q"

def _unipile_headers():
    return {
        "X-API-KEY": UNIPILE_KEY,
        "accept": "application/json",
        "Content-Type": "application/json"
    }

@app.route('/resolve/locations', methods=['GET', 'OPTIONS'])
def resolve_locations():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"items": []}), 400
    try:
        resp = requests.get(
            f"{UNIPILE_BASE}/linkedin/search/parameters",
            headers=_unipile_headers(),
            params={"account_id": UNIPILE_ACCT, "type": "LOCATION", "keywords": q, "limit": 10},
            timeout=20
        )
        resp.raise_for_status()
        items = [{"id": r.get("id"), "title": r.get("title", "")} for r in resp.json().get("items", [])]
        return jsonify({"items": items})
    except Exception as e:
        return jsonify({"items": [], "error": str(e)}), 500

@app.route('/resolve/industries', methods=['GET', 'OPTIONS'])
def resolve_industries():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"items": []}), 400
    try:
        resp = requests.get(
            f"{UNIPILE_BASE}/linkedin/search/parameters",
            headers=_unipile_headers(),
            params={"account_id": UNIPILE_ACCT, "type": "INDUSTRY", "keywords": q, "limit": 10},
            timeout=20
        )
        resp.raise_for_status()
        items = [{"id": r.get("id"), "title": r.get("title", "")} for r in resp.json().get("items", [])]
        return jsonify({"items": items})
    except Exception as e:
        return jsonify({"items": [], "error": str(e)}), 500

@app.route('/search', methods=['POST', 'OPTIONS'])
def handle_search():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    body = request.json or {}

    professions = body.get('professions', [])
    locations   = body.get('locations', [])
    industries  = body.get('industries', [])
    limit       = min(int(body.get('limit', 10)), 50)
    max_pages   = min(int(body.get('max_pages', 5)), 20)

    if not professions and not locations and not industries:
        return jsonify({"detail": "Please provide at least one location, industry, or profession."}), 400

    # Resolve location IDs
    location_ids = []
    for loc in locations:
        try:
            r = requests.get(
                f"{UNIPILE_BASE}/linkedin/search/parameters",
                headers=_unipile_headers(),
                params={"account_id": UNIPILE_ACCT, "type": "LOCATION", "keywords": loc, "limit": 3},
                timeout=15
            )
            items = r.json().get("items", [])
            if items:
                location_ids.append(items[0]["id"])
        except:
            pass

    # Resolve industry IDs
    industry_ids = []
    for ind in industries:
        try:
            r = requests.get(
                f"{UNIPILE_BASE}/linkedin/search/parameters",
                headers=_unipile_headers(),
                params={"account_id": UNIPILE_ACCT, "type": "INDUSTRY", "keywords": ind, "limit": 3},
                timeout=15
            )
            items = r.json().get("items", [])
            if items:
                industry_ids.append(items[0]["id"])
        except:
            pass

    keywords = " OR ".join(p.strip() for p in professions if p.strip())

    # Run LinkedIn search
    search_body = {"api": "classic", "category": "people", "limit": limit}
    if keywords:   search_body["keywords"]  = keywords
    if location_ids: search_body["location"] = location_ids
    if industry_ids: search_body["industry"] = industry_ids

    all_profiles = []
    cursor = None
    for _ in range(max_pages):
        params = {"account_id": UNIPILE_ACCT}
        if cursor:
            params["cursor"] = cursor
        try:
            resp = requests.post(
                f"{UNIPILE_BASE}/linkedin/search",
                headers=_unipile_headers(),
                params=params,
                json=search_body,
                timeout=30
            )
            data = resp.json()
            items = data.get("items", [])
            if not items:
                break
            for raw in items:
                all_profiles.append({
                    "id":          raw.get("id", ""),
                    "full_name":   raw.get("name") or raw.get("full_name", ""),
                    "occupation":  raw.get("headline", ""),
                    "location":    raw.get("location", ""),
                    "Linkedin URL": raw.get("profile_url") or raw.get("public_profile_url", ""),
                    "Usernames":   raw.get("public_identifier", "")
                })
            cursor = data.get("cursor")
            if not cursor:
                break
        except Exception as e:
            print(f"Search error: {e}")
            break

    return jsonify({
        "success": True,
        "count": len(all_profiles),
        "profiles": all_profiles
    })


if __name__ == '__main__':
    print("--------------------------------------------------")
    print(f"LinkedIn AI Agent Backend Running from: {ROOT_DIR}")
    print("Accessible at http://localhost:8000")
    print("--------------------------------------------------")
    # Listen on 0.0.0.0 for broader accessibility
    app.run(debug=True, host='0.0.0.0', port=8000)
