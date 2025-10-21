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
UPDATE_INTERVAL_MINUTES = 5 # Changed from 10 hours to 5 minutes for better testing
INVITE_API_URL = f"https://discord.com/api/v9/invites/{INVITE_CODE}?with_counts=true"

# --- The Core Logic Function ---
def update_discord_message():
    """
    This function contains the logic to get the member count and update the message.
    The scheduler will call this function automatically.
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled update...")
    
    # --- THIS IS THE FIX ---
    # We create a header that disguises our script as a web browser.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    
    # 1. Get the total member count from the invite link
    try:
        # We add the 'headers' to the request.
        response = requests.get(INVITE_API_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # This is the correct key for the total member count from the API.
            total_count = data.get('approximate_member_count', 0)
        else:
            print(f"Error fetching invite data: {response.status_code} - {response.text}")
            return # Stop the function if we can't get the count
    except Exception as e:
        print(f"An exception occurred while fetching invite data: {e}")
        return
        
    if total_count == 0:
        print("API returned 0 members. This might be an error or rate limit. Skipping update.")
        return

    embed_data = {
    "title": "ABOUT US",
    "description": (
        ">>> **Dive into a universe of explosive multiplayer mayhem, where every match is an epic saga and every victory is legendary!**\n\n"
        "**The arena is eternal. Your controllers are charged. It's time to unleash chaos!**\n\n"
        "We're more than just a server; we're a thriving community of passionate gamers, united by the thrill of competition and the joy of camaraderie. Whether you're a seasoned veteran or a rising star, Divine Hub is your ultimate battleground."
    ),
    "color": 0x8E44AD,  # A stylish purple (you can adjust this hex code!)
    "fields": [
        {"name": "✨ **OUR LEGION GROWS:**", "value": f"```ini\n[ {total_count} Champions Strong ]\n```", "inline": True},
        {"name": "🎮 **WHAT WE OFFER:**", "value": "```md\n# Epic Tournaments\n# LFG Channels\n# Friendly Community\n# Exclusive Events\n```", "inline": True}
    ],
    "image": {"url": IMAGE_URL}, # This will be your amazing banner! # Optional: Add your server icon for extra flair!
    "footer": {"text": "© DIVINE HUB TEAM |  Powering Up Your Game!"}
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

@app.route('/')
def index():
    return "Flask server with internal scheduler is running. The update job runs in the background."

# Configure and start the scheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(update_discord_message, 'interval', minutes=UPDATE_INTERVAL_MINUTES)
scheduler.start()

print("Performing initial update on startup...")
update_discord_message()

print(f"Scheduler started. The message will be updated every {UPDATE_INTERVAL_MINUTES} minutes.")
print("The Flask web server is now running.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
