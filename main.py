import schedule
import time
import datetime
import subprocess
import smhi_api
import sys
import os 
import threading
import traceback
import central
import discord_listener


# Schedule times
WEEKDAY_OPEN_TIME = "07:30"
WEEKEND_OPEN_TIME = "09:00"
DISPLAY_DISCORD_WEEKDAY_TIME = "07:35"
DISPLAY_DISCORD_WEEKEND_TIME = "09:15"
SPOTIFY_WEEKDAY_TIME = "07:40"
SPOTIFY_WEEKEND_TIME = "09:30"
CLOSE_TIME = "22:00"

# Detect correct python executable (Windows vs Linux)
#PYTHON_CMD = os.path.join(sys.prefix, "bin", "python") if sys.platform != "win32" else os.path.join(sys.prefix, "Scripts", "python.exe")

PYTHON_CMD = os.path.abspath(".venv/bin/python")  # Ensures the correct venv path

def log_error(name, e):                     
    with open("error_log.txt", "a") as f:
        f.write(f"[{datetime.datetime.now()}] Error in {name}: {str(e)}\n")
        f.write(traceback.format_exc())
        f.write("\n")


def run_script(script_name, args=None):
    
    try:
        cmd = [PYTHON_CMD, script_name]
        if args:
            cmd.extend(args)
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        log_error(script_name, e)


def roll_blinds():
    if central.wait_until_loop_ready():
        central.send_ble_message("start")
        print("Rolling blinds")
    else:
        print("[main] BLE loop not ready!")



def weather_scripts():
    try: 
        weather_data = smhi_api.fetch_data()
        if weather_data: 
            going_to_rain, going_to_snow, temperature = smhi_api.filter_data(weather_data)
            weather_args = [str(going_to_rain).lower(), str(going_to_snow).lower(), str(temperature)] # Detta är för att göra om det till en string för att kunna skicka det som argument till display.py och discord.py
            run_script("discord_bot.py", weather_args)                                                    # Sen jag gör de till en boolean i display.py och discord.py   
            #run_script("display.py", weather_args)
            print("Weather scripts done") # För att se om det kommer hit

    except Exception as e:
        log_error("weather_scripts", e)
        print(f"Error in weather_scripts: {e}")

def start_spotify():

    try:
        run_script("spotify_api.py")
        print("Spotify script done") #För att se om det kommer hit

    except Exception as e:
        log_error("start_spotify", e)
        print(f"Error in start_spotify: {e}")

def start_central():
    import asyncio
    try:
        asyncio.run(central.ble_loop())
    except Exception as e:
        log_error("start_central", e)
        print(f"Error in start_central: {e}")
        
def run_discord_listener():
    try:
        print("Starting Discord listener")
        discord_listener.start_bot()

    except Exception as e:
        log_error("run_discord_listener", e)
        print(f"Error in run_discord_listener: {e}")

# Schedule tasks


schedule.every().monday.at(WEEKDAY_OPEN_TIME).do(roll_blinds)
schedule.every().tuesday.at(WEEKDAY_OPEN_TIME).do(roll_blinds)
schedule.every().wednesday.at(WEEKDAY_OPEN_TIME).do(roll_blinds)
schedule.every().thursday.at(WEEKDAY_OPEN_TIME).do(roll_blinds)
schedule.every().friday.at(WEEKDAY_OPEN_TIME).do(roll_blinds)

schedule.every().saturday.at(WEEKEND_OPEN_TIME).do(roll_blinds)
schedule.every().sunday.at(WEEKEND_OPEN_TIME).do(roll_blinds)

schedule.every().day.at(CLOSE_TIME).do(roll_blinds)

schedule.every().monday.at(SPOTIFY_WEEKDAY_TIME).do(start_spotify)
schedule.every().tuesday.at(SPOTIFY_WEEKDAY_TIME).do(start_spotify)
schedule.every().wednesday.at(SPOTIFY_WEEKDAY_TIME).do(start_spotify)
schedule.every().thursday.at(SPOTIFY_WEEKDAY_TIME).do(start_spotify)
schedule.every().friday.at(SPOTIFY_WEEKDAY_TIME).do(start_spotify)

schedule.every().saturday.at(SPOTIFY_WEEKEND_TIME).do(start_spotify)
schedule.every().sunday.at(SPOTIFY_WEEKEND_TIME).do(start_spotify)

schedule.every().monday.at(DISPLAY_DISCORD_WEEKDAY_TIME).do(weather_scripts)
schedule.every().tuesday.at(DISPLAY_DISCORD_WEEKDAY_TIME).do(weather_scripts)
schedule.every().wednesday.at(DISPLAY_DISCORD_WEEKDAY_TIME).do(weather_scripts)
schedule.every().thursday.at(DISPLAY_DISCORD_WEEKDAY_TIME).do(weather_scripts)
schedule.every().friday.at(DISPLAY_DISCORD_WEEKDAY_TIME).do(weather_scripts)

schedule.every().saturday.at(DISPLAY_DISCORD_WEEKEND_TIME).do(weather_scripts)
schedule.every().sunday.at(DISPLAY_DISCORD_WEEKEND_TIME).do(weather_scripts)


if __name__ == "__main__":
    
    print("Starting automation, scheduler is running..")
    weather_scripts() # temporary test
    start_spotify() # temporary test
    print("Automation loop is running..")

    # Startar Discord listener i bakgrunden
    discord_thread = threading.Thread(target=run_discord_listener, daemon=True)
    discord_thread.start()
    print("Discord listener started in background")

    # Startar Central i bakgrunden
    central_thread = threading.Thread(target=start_central, daemon=True)
    central_thread.start()
    print("Central started in background")

    # Main loop
    while True:
        schedule.run_pending()
        time.sleep(1) 
    


