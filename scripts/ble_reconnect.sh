#!/bin/bash

BLE_MAC="70:99:1C:D2:72:AD" # MAC-adress till JBL GO 2
RECONNECT_INTERVAL="10" 

# Koden loopar hela tiden och kollar om den är ansluten även när det är ansluten, så det kan lite av en belastning på systemet.
# Borde egengligen kolla om enheten är ansluten och om den inte är det, då köra en loop som kollar om den är ansluten varje sekund tills den är det.
# Borde kanske kanske fixas men får fungera så här så länge. #TODO fixa detta 

# Glöm inte att köra chmod +x ble_reconnect.sh för att göra filen exekverbar samt att köra scripten när PI bootar upp.
# crontab -e
# @reboot /bin/bash /home/pi/bluetooth-reconnect.sh &  # Kan vara fel men kolla upp detta


while true; do

    #Kolla om enheten är ansluten
    if bluetoothctl info "$BLE_MAC" | grep -q "Connected: yes"; then
        echo "$(date) - JBL GO 2 is connected"
    else
        echo "$(date) - JBL GO 2 is not connected, reconnecting..."
 
        if bluetoothctl show | grep -q "Powered: yes" && bluetoothctl devices | grep -q "$BLE_MAC"; then
            bluetoothctl power on
            bluetoothctl connect "$BLE_MAC"
            bluetoothctl trust "$BLE_MAC"
        else 
            echo "$(date) - JBL GO 2 not found or BLE is off, scanning..."
            bluetoothctl scan on
            sleep 10
            bluetoothctl scan off
        fi
    fi

    sleep "$RECONNECT_INTERVAL"

done