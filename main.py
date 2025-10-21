from flask import Flask, jsonify
import requests
import json

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. SETUP: FILL IN YOUR DETAILS HERE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEBHOOK_URL = "https://discord.com/api/webhooks/1430311382775238791/pV42MGjMbXLaBzJv29YX984KNt_QXQfnWdsBoIz7XwRvsw96t-vEQ3AM80BRM4bvdJWk"
SERVER_ID = "615868918627565568"  # Paste the Server ID from the Widget page

# ⬇️ PASTE THE MESSAGE ID YOU COPIED FROM DISCORD HERE ⬇️
TARGET_MESSAGE_ID = "1430317792464474152" 

IMAGE_URL = "https://i.ibb.co/CpnXPyLd/Gemini-Generated-Image-48c7ts48c7ts48c7.png"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Configuration
WIDGET_API_URL = f"https://discord.com/api/guilds/{SERVER_ID}/widget.json"

# Initialize Flask App
app = Flask(__name__)

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
    """This endpoint is triggered by an external scheduler to update a specific message."""
    
    if not TARGET_MESSAGE_ID or TARGET_MESSAGE_ID == "YOUR_TARGET_MESSAGE_ID_HERE":
        return jsonify({"status": "error", "message": "TARGET_MESSAGE_ID is not set in the script."}), 500
    
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
    
    # Construct the URL to edit the specific message
    edit_url = f"{WEBHOOK_URL}/messages/{TARGET_MESSAGE_ID}"
    
    # Send the PATCH request to edit the message
    response = requests.patch(edit_url, json=payload)
    
    if response.status_code == 200:
        return jsonify({"status": "success", "action": "updated", "online_count": online_count})
    elif response.status_code == 404:
        error_msg = f"Message with ID {TARGET_MESSAGE_ID} not found. Was it deleted? Please check the ID in the script."
        print(error_msg)
        return jsonify({"status": "error", "message": error_msg}), 404
    else:
        error_msg = f"Webhook edit failed: {response.status_code} - {response.text}"
        print(error_msg)
        return jsonify({"status": "error", "message": error_msg}), 500

# Default route to confirm the server is running
@app.route('/')
def index():
    return "Flask server is running. Use the /update endpoint to trigger the Discord update."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
