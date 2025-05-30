# LinkedInAutomation.py

from flask import session, redirect, url_for, jsonify, request
from requests_oauthlib import OAuth2Session
import os
import requests
import tempfile
from functools import wraps

# Allow HTTP for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID = "78wr2cfw5cg4p0"
LINKEDIN_CLIENT_SECRET = "WPL_AP1.2qHMSIbGb6cmCvhn.2MAu4Q=="
REDIRECT_URI = os.environ["LINKEDIN_REDIRECT_URI"]

AUTHORIZATION_BASE_URL = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
POST_URL = 'https://api.linkedin.com/v2/ugcPosts'

SCOPE = "openid profile email w_member_social"


# Decorator to enforce login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Session:", dict(session))  # Add this line
        if 'linkedin_token' not in session:
            print("❌ No LinkedIn token in session.")
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    
    return decorated_function



# OAuth2 Session helper
def get_linkedin_session():
    return OAuth2Session(
        LINKEDIN_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )


# Route: Start OAuth flow
def linkedin_login():
    linkedin = get_linkedin_session()
    authorization_url, state = linkedin.authorization_url(AUTHORIZATION_BASE_URL)
    session["oauth_state"] = state
    return redirect(authorization_url)


# Route: Callback from LinkedIn
def linkedin_callback():
    saved_state = session.get("oauth_state")
    returned_state = request.args.get("state")

    if not saved_state or saved_state != returned_state:
        return "⚠️ Login error. Please <a href='/linkedin/login'>try again</a>.", 400

    try:
        linkedin = OAuth2Session(
            LINKEDIN_CLIENT_ID,
            state=saved_state,
            redirect_uri=REDIRECT_URI
        )
        token = linkedin.fetch_token(
            TOKEN_URL,
            client_secret=LINKEDIN_CLIENT_SECRET,
            authorization_response=request.url,
            include_client_id=True
        )
        session["linkedin_token"] = token
        frontend_url = os.environ.get("FRONTEND_URL", "/")
        return redirect(frontend_url)
    except Exception as e:
        return f"Error during LinkedIn login: {e}", 500
    print("🔐 Token saved to session:", session.get("linkedin_token"))


# API: Post text-only content
@login_required
def post_to_linkedin(content):
    token = session.get("linkedin_token")
    headers = {
        "Authorization": f"Bearer {token['access_token']}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    try:
        profile = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers).json()
        author_urn = f"urn:li:person:{profile['sub']}"

        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        response = requests.post(POST_URL, headers=headers, json=post_data)
        response.raise_for_status()
        return {"success": True, "response": response.json()}

    except Exception as e:
        return {"success": False, "error": str(e)}


# API: Post with image
@login_required
def post_with_image(content, image_file):
    token = session.get("linkedin_token")
    headers = {
        "Authorization": f"Bearer {token['access_token']}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    try:
        profile = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers).json()
        author_urn = f"urn:li:person:{profile['sub']}"

        # Step 1: Register image
        register_payload = {
            "registerUploadRequest": {
                "owner": author_urn,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [{
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }],
                "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
            }
        }
        register_resp = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            headers=headers,
            json=register_payload
        ).json()

        upload_url = register_resp["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = register_resp["value"]["asset"]

        # Step 2: Upload image
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            image_file.save(tmp.name)
            with open(tmp.name, 'rb') as img:
                upload_headers = {
                    "Authorization": f"Bearer {token['access_token']}",
                    "Content-Type": image_file.mimetype
                }
                upload_resp = requests.put(upload_url, data=img, headers=upload_headers)
                upload_resp.raise_for_status()

        # Step 3: Create post with image
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "IMAGE",
                    "media": [{
                        "status": "READY",
                        "description": {"text": "Image description"},
                        "media": asset_urn,
                        "title": {"text": "Image Title"}
                    }]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        response = requests.post(POST_URL, headers=headers, json=post_data)
        response.raise_for_status()
        return {"success": True, "response": response.json()}

    except Exception as e:
        return {"success": False, "error": str(e)}
