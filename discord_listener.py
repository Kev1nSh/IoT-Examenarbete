import discord 
import asyncio
import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI
from central import send_ble_message

load_dotenv()

last_command_from = {}

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(f"Discord token loaded: {'YES' if DISCORD_TOKEN else 'NO'}")
print(f"Discord channel ID loaded: {'YES' if DISCORD_CHANNEL_ID else 'NO'}")
print(f"OpenAI API key loaded: {'YES' if OPENAI_API_KEY else 'NO'}")


try:
    DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL_ID)
except ValueError:
    print("Error: DISCORD_CHANNEL_ID must be an integer.")
    exit(1)

# Initiera OpenAI API
client_ai = OpenAI(api_key=OPENAI_API_KEY)



# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client  = discord.Client(intents=intents)


def interpret_command(message_content):
    try:
        print(f"[GPT INPUT] {message_content}")
        response = client_ai.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [
                {
                    "role": "system", 
                    "content":(
                        "Du är en strikt och exakt kommandotolk för ett motor- och LED-system. "
                        "Du får ett kort textmeddelande från en användare på svenska, spanska eller engelska. "
                        "Din uppgift är att tolka vad användaren vill göra och svara med exakt ett av följande kommandon (ingen extra text):\n\n"
                        
                        "- start\n"
                        "  Används om användaren vill öppna eller stänga gardinerna. Exempel: 'öppna', 'stäng', 'abre', 'cierra', 'starta', 'activa motor'\n\n"
                        
                        "- toggle\n"
                        "  Används om användaren vill slå på eller av en LED. Exempel: 'sätt på', 'sätt av', 'slå på', 'slå av', 'tända', 'apagar', 'prender', 'turn on', 'turn off'\n\n"
                        
                        "- create led\n"
                        "  Används när användaren vill skapa en LED. Exempel: 'skapa', 'create', 'crear', 'lägg till', 'add led'\n"
                        "  Även om användaren bara skriver 'create' eller 'crear', tolka det som 'create led'\n\n"
                        
                        "- erase led\n"
                        "  Används när användaren vill ta bort en LED. Exempel: 'ta bort', 'delete', 'erase', 'borrar', 'remove led'\n\n"
                        
                        "- led X\n"
                        "  Används när användaren vill välja en specifik LED. Svara som 'led 1', 'led 2', 'led3', etc.\n"
                        "  Giltiga uttryck är t.ex. 'led 1', 'led1', 'select led 2', 'välj led 3', 'quiero el led4'\n\n"
                        
                        "Godkända format tillåter både mellanslag och sammanskrivna ord, som 'led2' eller 'led 2'.\n"
                        "Om du inte är säker, svara exakt: unknown"
                    ) 
                },
                {"role": "user", "content": message_content}
            ],
            temperature = 0
        )
        command = response.choices[0].message.content.strip().lower()
        print(f"[GPT OUTPUT] {command}")
        return command
    
    except Exception as e:
        print(f"[ERROR] Error interpreting command: {e}")
        return "unknown"
    
@client.event
async def on_ready():
    print(f"[DEBUG] Bot in as {client.user}")

@client.event
async def on_message(message):
    print(f"[DEBUG] Message received: {message.content} from {message.author}")
    if str(message.author.id) == str(client.user.id):
        print("[DEBUG] Ignoring own message")
        return
    
    if message.channel.id != DISCORD_CHANNEL_ID:
        return
    
    now = datetime.now()
    user_id = str(message.author.id)

    if user_id in last_command_from:
        if now - last_command_from[user_id] < timedelta(seconds=2):
            print(f"[DEBUG] Ignoring command from user")
            return
        
    last_command_from[user_id] = now


    loop = asyncio.get_event_loop()
    interpreted_command = await loop.run_in_executor(None, lambda: interpret_command(message.content))
    print(f"[DEBUG] Interpreted command: {interpreted_command}")
    
    if interpreted_command == "unknown":
        await message.channel.send("Did not understand the command. Please try again.")
        return

    if interpreted_command == "start":
       
        send_ble_message("start")
        await message.channel.send("Blinds are opening!")
    
    elif interpreted_command == "toggle":
        
        send_ble_message("toggle")
        await message.channel.send("LED toggled!")
    
    elif interpreted_command == "create led":
        send_ble_message("create led")
        await message.channel.send("LED created!")
    
    elif interpreted_command == "erase led":
        send_ble_message("erase led")
        await message.channel.send("LED erased!")

    elif interpreted_command and interpreted_command.startswith("led"):
        try:
            led_number = int(interpreted_command.split(" ")[1])
            send_ble_message(f"led{led_number}")
            await message.channel.send(f"LED {led_number} selected!")
        except ValueError:
            await message.channel.send("Invalid LED number. Please provide a valid number.")
    
    else:
        
        await message.channel.send("Did not understand the command. Please try again.")

"""
    print("[DEBUG] Starting Discord bot...")
    try: 
        client.run(DISCORD_TOKEN)

    except Exception as e:
        print(f"[ERROR] Error starting Discord bot: {e}")
"""



def start_bot():
    print("[DEBUG] Starting Discord bot...")
    try: 
        client.run(DISCORD_TOKEN)
    
    except Exception as e:
        print(f"[ERROR] Error starting Discord bot: {e}")
