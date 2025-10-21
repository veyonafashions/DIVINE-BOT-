from flask import Flask
import requests
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. SETUP: FILL IN YOUR DETAILS HERE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEBHOOK_URL = "https://discord.com/api/webhooks/1430311382775238791/pV42MGjMbXLaBzJv29YX984KNt_QXQfnWdsBoIz7XwRvsw96t-vEQ3AM80BRM4bvdJWk"
INVITE_CODE = "aMHKp7XZQd"  # The code from your server's invite link
TARGET_MESSAGE_ID = "1430317792464474152" # The message to edit
IMAGE_URL = "https://i.ibb.co/CpnXPyLd/Gemini-Generated-Image-48c7ts48c7ts48c7.png"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Configuration
UPDATE_INTERVAL_HOURS = 10
INVITE_API_URL = f"https://discord.com/api/v9/invites/{INVITE_CODE}?with_counts=true"

# --- The Core Logic Function ---
def update_discord_message():
    """
    This function contains the logic to get the member count and update the message.
    The scheduler will call this function automatically.
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled update...")
    
    # 1. Get the total member count from the invite link
    try:
        response = requests.get(INVITE_API_URL)
        if response.status_code == 200:
            data = response.json()
            total_count = data.get('guild', {}).get('approximate_member_count', 0)
        else:
            print(f"Error fetching invite data: {response.status_code} - {response.text}")
            return # Stop the function if we can't get the count
    except Exception as e:
        print(f"An exception occurred while fetching invite data: {e}")
        return

    # 2. Define the embed structure
    embed_data = {
      "title": "ABOUT US",
      "description": (
          "Divine Hub is a universe of explosive multiplayer mayhem...\n\n"
          "The arena is eternal. The controllers are ready. Bombs away!"
      ),
      "color": 9371903,
      "fields": [{"name": "TOTAL MEMBERS:", "value": f"```{total_count}```"}],
      "image": {"url": IMAGE_URL},
      "footer": {"text": "© DIVINE HUB TEAM"}
    }
    
    payload = {"embeds": [embed_data], "username": "Divine Hub"}
    edit_url = f"{WEBHOOK_URL}/messages/{TARGET_MESSAGE_ID}"
    
    # 3. Send the PATCH request to edit the message via webhook
    try:
        response = requests.patch(edit_url, json=payload)
        if response.status_code == 200:
            print(f"Successfully updated message. Total members: {total_count}")
        else:
            print(f"Webhook update failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An exception occurred during the webhook request: {e}")


# --- Flask and Scheduler Setup ---
app = Flask(__name__)

# This route is just to confirm the server is alive if you visit its URL.
@app.route('/')
def index():
    return "Flask server with internal scheduler is running. The update job runs in the background."

# Configure and start the scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(update_discord_message, 'interval', hours=UPDATE_INTERVAL_HOURS)
scheduler.start()

# Run the update once on startup
print("Performing initial update on startup...")
update_discord_message()

print(f"Scheduler started. The message will be updated every {UPDATE_INTERVAL_HOURS} hours.")
print("The Flask web server is now running.")

if __name__ == '__main__':
    # For production, use 'gunicorn app:app'
    # For simple hosting like Replit, this is fine.
    app.run(host='0.0.0.0', port=8080)
