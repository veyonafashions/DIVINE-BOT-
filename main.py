from flask import Flask, jsonify
import requests
import os
import json

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. SETUP: FILL IN YOUR DETAILS HERE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEBHOOK_URL = "https://discord.com/api/webhooks/1430311382775238791/pV42MGjMbXLaBzJv29YX984KNt_QXQfnWdsBoIz7XwRvsw96t-vEQ3AM80BRM4bvdJWk"
SERVER_ID = "615868918627565568"  # Paste the Server ID from the Widget page
IMAGE_URL = "https://i.ibb.co/CpnXPyLd/Gemini-Generated-Image-48c7ts48c7ts48c7.png" # Optional: Replace with your own image URL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Configuration
MESSAGE_ID_FILE = "message_id.txt"
WIDGET_API_URL = f"https://discord.com/api/guilds/{SERVER_ID}/widget.json"

# Initialize Flask App
app = Flask(__name__)

# --- Helper Functions ---
def read_message_id():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            return f.read().strip()
    return None

def save_message_id(message_id):
    with open(MESSAGE_ID_FILE, "w") as f:
        f.write(str(message_id))

def get_online_count():
    try:
        response = requests.get(WIDGET_API_URL)
        response.raise_for_status()
        data = response.json()
        return data.get('presence_count', 0)
    except Exception as e:
        print(f"Error fetching data from Discord Widget API: {e}")
        return None

# --- The Main Flask Route ---
@app.route('/update', methods=['GET'])
def update_discord_message():
    """This is the endpoint that the scheduler will hit."""
    online_count = get_online_count()

    if online_count is None:
        return jsonify({"status": "error", "message": "Could not retrieve member count from widget API."}), 500

    # Define the embed structure
    embed_data = {
      "title": "📊 Divine Hub Statistics",
      "description": (
          "Divine Hub is a universe of explosive multiplayer mayhem, where BombSquad's signature chaos thrives.\n\n"
          "We maintain high-performance servers running 24/7, preserving the game's iconic physics while delivering both classic and refreshed experiences..."
      ),
      "color": 9371903,
      "fields": [{"name": "MEMBERS ONLINE:", "value": f"```{online_count}```"}],
      "image": {"url": IMAGE_URL},
      "footer": {"text": "© DIVINE HUB TEAM"}
    }
    
    payload = {"embeds": [embed_data], "username": "Divine Hub"}
    message_id = read_message_id()
    
    if message_id:
        # EDIT the existing message
        url = f"{WEBHOOK_URL}/messages/{message_id}"
        response = requests.patch(url, json=payload)
        
        if response.status_code == 404: # Message was deleted
            print("Message not found, will create a new one.")
            message_id = None
            os.remove(MESSAGE_ID_FILE)
        elif response.status_code == 200:
            return jsonify({"status": "success", "action": "updated", "online_count": online_count})
        else:
            return jsonify({"status": "error", "message": f"Webhook edit failed: {response.text}"}), 500

    if not message_id:
        # POST a new message
        url = f"{WEBHOOK_URL}?wait=true"
        response = requests.post(url, json=payload)
        
        if response.status_code in [200, 201]:
            new_message_id = response.json()['id']
            save_message_id(new_message_id)
            return jsonify({"status": "success", "action": "created", "message_id": new_message_id})
        else:
            return jsonify({"status": "error", "message": f"Webhook post failed: {response.text}"}), 500

# Default route to confirm the server is running
@app.route('/')
def index():
    return "Flask server is running. Use the /update endpoint to trigger the Discord update."

if __name__ == '__main__':
    # For local testing. For production, use a WSGI server like Gunicorn.
    app.run(host='0.0.0.0', port=8080)
