import requests

# LinkedIn Posting Logic via Unipile
def post_to_unipile(account_id, text):
    """
    Triggers a LinkedIn post via the Unipile API.
    
    Args:
        account_id (str): The Unipile account ID for the LinkedIn connection.
        text (str): The content of the post.
    
    Returns:
        dict: The response from the Unipile API.
    """
    url = "https://api20.unipile.com:15048/api/v1/posts"
    headers = {
        "X-API-KEY": "GZ4Napww.06tYodoW/wclbYDfXer1uh0c0hwOt2JOaTz2b7spddg=",
        "accept": "application/json"
    }

    # Unipile expects multipart/form-data for this endpoint
    files = {
        "account_id": (None, account_id),
        "text": (None, text)
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        print(f"Error posting to Unipile: {e}")
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_msg = e.response.json().get('message', error_msg)
            except:
                pass
        return {
            "success": False,
            "message": error_msg
        }

if __name__ == "__main__":
    # Test script (not used by the web app)
    print("This script is now a module for the LinkedIn AI Agent.")
