import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import datetime # Bara för att testa calculate_device_awake_time
import os

# Spotify API credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI") # Till PI
DEVICE_NAME = os.getenv("SPOTIFY_DEVICE_NAME")

scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope,
                                               cache_path=".cache"))

# Vi hämtar in devicens id
"""def get_device(device_name, retries=5, delay=2):
    for attempt in range(retries):
        devices = sp.devices()
        for device in devices['devices']:
            if device_name.lower() in device['name'].lower():
                print(f"Device found: '{device_name}' in attempt {attempt+1}") # Detta är för att se att det fungerar # Ska tas bort senare
                return device['id']
        print(f"Device not found: '{device_name}', retrying in {delay} seconds...")
        time.sleep(delay)
    print(f"Failed to find device: '{device_name}', exiting!")
    return None"""

def get_device(device_name):
    devices = sp.devices()
    for device in devices['devices']:
        if device_name.lower() in device['name'].lower():
            print(f"Device found: '{device_name}'") # Detta är för att se att det fungerar # Ska tas bort senare
            return device['id']
    print(f"Device not found: '{device_name}', exiting!")
    return None

# Vi startar musiken på den valda enheten        
def play_music():
    
    device_name = DEVICE_NAME
    device_id = get_device(device_name)
    if not device_id:
        print("Failed to find device, exiting...")
        return
    try:
        sp.start_playback(device_id=device_id, context_uri="spotify:playlist:4j3Z36o56Iw3KhqPRkNaIP?si=873552eb6676486")
        sp.volume(50, device_id=device_id)
        print("Music started on given device") # Detta är för att se att det fungerar # Ska tas bort senare
    except Exception as e:
        print(f"Spotify API error: {e}")

def calculate_device_awake_time(device_name, check_interval=5,max_duration=3600):
    start_time = None
    total_up_time = 0
    end_time = datetime.datetime.now() + datetime.timedelta(seconds=max_duration)

    while datetime.datetime.now() < end_time:
        device_id = get_device(device_name)

        if device_id:
            if start_time is None:
                start_time = datetime.datetime.now()
            print(f"Device '{device_name}' is awake, starting timer")
        else: 
            if start_time is not None:
                total_up_time = (datetime.datetime.now() - start_time).total_seconds()
                print(f"Device '{device_name}' is asleep, stopping timer")
                return total_up_time
    
        time.sleep(check_interval)

    print(f"Max duration of {max_duration} seconds reached, stopping timer")
    return total_up_time
            

if __name__ == "__main__":
    devices = sp.devices()
    print(devices)
    device_name = "KSG Rum"

    #uptime = calculate_device_awake_time(device_name)
    #print(f"Device was awake for {uptime:.2f} seconds")
    play_music()
    # 542 sekunder = 9 minuter
