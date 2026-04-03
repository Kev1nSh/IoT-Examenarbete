#!/bin/bash

# Exit if another instance of this script is already running, already caus me issues and headaches haha
LOCKFILE="/tmp/raspotify_boot.lock"
exec 200>$LOCKFILE
flock -n 200 || {
    echo "Another instance of this script is already running."
    exit 1
}

# Spotify API credentials
CLIENT_ID="18280288b49c4bd084105e1f8a32d32f"
CLIENT_SECRET="62f916e46cc941e1897f159b77a652d5"
TOKEN_URL="https://accounts.spotify.com/api/token"

# Get the OAuth token
get_spotify_token() {
    TOKEN_RESPONSE=$(curl -s -X "POST" -H "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=client_credentials&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET" \
        "$TOKEN_URL")

    echo "Spotify Response: $TOKEN_RESPONSE"  # Debugging line

    TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')

    if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
        echo "$TOKEN" > /tmp/spotify_token
        echo "New Spotify token obtained."
    else
        echo "Failed to get Spotify token. Response was: $TOKEN_RESPONSE"
        exit 1
    fi
}

start_pulseaudio() {
    pulseaudio --start
    sleep 5
    pactl set-default-sink bluez_sink.70_99_1C_D2_72_AD.1
    pactl set-sink-volume bluez_sink.70_99_1C_D2_72_AD.1 80%
    
}

restart_avahi() { #May not be needed
    echo "Restarting Avahi..."
    sudo systemctl restart avahi-daemon.service 
    sleep 2
}


start_librespot() {
    while true; do
        TOKEN=$(cat /tmp/spotify_token)

        # Kill any existing librespot instances before starting a new one
        pkill -9 -e librespot
        sleep 2

        restart_avahi
        start_pulseaudio

        SPOTIFY_NAME="RaspiSpotifyV$(shuf -i 100-999 -n 1)"

        echo "Starting librespot with name: $SPOTIFY_NAME on $(date)"

         /usr/bin/librespot --name "$SPOTIFY_NAME" \
                            --backend pulseaudio \
                            --device bluez_sink.70_99_1C_D2_72_AD.1 \
                            --bitrate 320 \
                            --disable-audio-cache \
                            --enable-volume-normalisation \
                            --verbose

        echo "Librespot crashed. Restarting in 5 seconds..."
        sleep 5  # Wait before restart
    done
}

# Get token initially
get_spotify_token

# Run token refresh in the background every 55 minutes
while true; do
    sleep 3300  # Refresh every 55 minutes (token expires in 1 hour)
    get_spotify_token
done &


start_librespot
