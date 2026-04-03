import subprocess  
import re

def get_raspotifyname():
    command = "sudo systemctl status raspotify_boot.service"
    output = subprocess.getoutput(command)

    match = re.search(r'--name\s(RaspiSpotifyV\d{3})', output)

    if match:
        raspotify_name = match.group(1)
        print (f"Raspotify name: {raspotify_name}")
        return raspotify_name
    else:
        print("No match")
        return None
    

raspotify_name = get_raspotifyname()
print(raspotify_name)
