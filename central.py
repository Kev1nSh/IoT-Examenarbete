import asyncio
import smhi_api
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "fdc0486d-84d3-426b-bb88-857dfeb07b6e" # Capaz se usa despues
WRITE_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
READ_UUID = "c4ae3d9b-2eb6-4f2c-b6b5-cf08fe5bb888" # Capaz se usa despues



DEVICE_NAME = "John_Ble"
DEVICE_ADDRESS = "EA:D6:CF:F7:D6:DD" # Address of the NRF device

loop = None

message_queue = asyncio.Queue()

async def scanner():
    print("[Central]Scanning for devices...")
    devices = await BleakScanner.discover()
    nrf_device = next((d for d in devices if DEVICE_NAME in d.name), None)
    
    if nrf_device: 
        print(f"[Central] Device found: {nrf_device.name} ({nrf_device.address})")
        return nrf_device.address
    
    print("[Central] Device not found")
    return None



async def ble_loop():
    global loop
    loop = asyncio.get_running_loop()
    print("[Central] Starting BLE loop...")
    while True:
        adress = await scanner()
        if not adress:
            print("[Central] Device not found, retrying in 5 seconds...")
            await asyncio.sleep(5)
            continue

        async with BleakClient(adress) as client:
            if not client.is_connected:
                print("[Central] Couldn't connect to device")
                await asyncio.sleep(5)
                continue

            print(f"[Central] Connected to {adress}")

            try:
                while client.is_connected:
                    command = await message_queue.get()
                    print(f"[Central] Sending command: {command}")
                    await client.write_gatt_char(WRITE_UUID, command.encode())
                    print(f"[Central] Command sent: {command}")
                    await asyncio.sleep(1)

            except Exception as e:
                print(f"[Central] Error: {e}")
                continue


    
def send_ble_message(command: str):
    global loop
    
    try:
        if loop and loop.is_running():
            loop.call_soon_threadsafe(message_queue.put_nowait, command)
            print(f"[Central] Command queued: {command}")
        else:
            print("[Central] No running BLE loop.")
    except Exception as e:
        print(f"[Central] Error: {e}")
        return
    
def wait_until_loop_ready(timeout=5):
    import time
    start = time.time()
    while (time.time() - start) < timeout:
        if loop and loop.is_running():
            return True
        time.sleep(0.1)
    return False

if __name__ == "__main__":
    print("[Central] Starting BLE loop...")
    try:
        asyncio.run(ble_loop())
    except KeyboardInterrupt:
        print("[Central] Exiting...")


