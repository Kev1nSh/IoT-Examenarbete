import requests
import sys
import os

# Discord Bot Credentials
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
USER_ID = os.getenv("USER_ID")


def get_dm_channel():

    """Get the DM channel ID for the user."""
    url = "https://discord.com/api/v10/users/@me/channels"
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}", "Content-Type": "application/json"}
    data = {"recipient_id": USER_ID}

    response = requests.post(url, headers=headers, json=data)
    dm_channel = response.json()
    
    if "id" in dm_channel:
        return dm_channel["id"]
    else:
        print(f"Error: {dm_channel}")
        return None

def send_data_server(message): 
    

    url = f"https://discord.com/api/v9/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}",
                "Content-Type": "application/json"}
    data = {"content": message}

    response = requests.post(url, headers=headers, json=data)
    print(response.json()) # För och se om det fungerar


def send_discord_dm(message):
     
    dm_channel_id = get_dm_channel()
    if not dm_channel_id:
        print("Failed to get DM channel ID.")
        return
    
    # 445981470545149963 Johns
    mention = f"<@{USER_ID}>"
    message = f"{mention} {message}"

    url = f"https://discord.com/api/v10/channels/{dm_channel_id}/messages"
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}", "Content-Type": "application/json"}
    data = {"content": message}

    response = requests.post(url, headers=headers, json=data)
    print(response.json())

def main():
   
    going_to_rain = sys.argv[1].lower() == "true" # Detta är för att göra om det till en boolean efter att ha fått det som en string från sys.argv
    going_to_snow = sys.argv[2].lower() == "true" 
    temperature = sys.argv[3]

    # Create a message based on conditions
    message = "**Good morning! ☀️**\nHere is your weather update:\n"
    if going_to_rain:
        message += "🌧 It might rain soon. Bring an umbrella! ☔\n"
    if going_to_snow:
        message += "❄ Snow is expected. Dress warmly! 🧣\n"
    message += f"🌡 Current Temperature: {temperature}°C"

    # Send the DM
    send_discord_dm(message)
    send_data_server(message)

if __name__ == "__main__":
    main()
