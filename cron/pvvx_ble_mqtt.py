#!/usr/bin/env python3

import asyncio
import struct
import time
from datetime import datetime
from bleak import BleakScanner
import paho.mqtt.client as mqtt
import json

# ================= MQTT =================
MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
MQTT_USER = "admin"
MQTT_PASS = "pihome"

TOPIC = "tele/SENSOR"

# ================= BEHAVIOUR =================
PUBLISH_INTERVAL = 55  # seconds
state = {}
last_publish = 0

# ================= MQTT CLIENT =================
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()


# ===== MAC -> Tasmota-style ATC key =====
def mac_to_atc(mac: str):
    return "ATC" + mac.replace(":", "")[-6:].lower()

# ===== UPDATE STATE =====
def update_state(mac, parsed):

    key = mac_to_atc(mac)

    state[key] = {
        "Temperature": parsed["Temperature"],
        "Humidity": parsed["Humidity"],
        "Battery": parsed["Battery"],
        "LastUpdate": time.time()
    }

# ===== PUBLISH FULL TASMOTA SENSOR FRAME =====
def publish():
    global last_publish

    payload = {
        "Time": datetime.now().isoformat(),
    }

    # strip internal metadata before publishing
    for k, v in state.items():
        payload[k] = {
            "Temperature": v["Temperature"],
            "Humidity": v["Humidity"],
            "Battery": v["Battery"]
        }

    client.publish(TOPIC, json.dumps(payload), qos=0, retain=False)
    print("PUBLISHED:", payload)

    last_publish = time.time()

# ===== BLE CALLBACK =====
def callback(device, advertisement_data):

    service_data = advertisement_data.service_data

    if not service_data:
        return

    for uuid, data in service_data.items():

        # Environmental sensing UUID
        if uuid.lower() == "0000181a-0000-1000-8000-00805f9b34fb":

            try:
                # PVVX custom format — little-endian, hundredths
                temp = int.from_bytes(data[6:8], 'little', signed=True) / 100
                hum  = int.from_bytes(data[8:10], 'little') / 100
                batt = data[12]  # battery % at offset 12, after 2-byte voltage at 10-11

                parsed = {
                    "Temperature": round(temp, 1),
                    "Humidity":    round(hum, 1),
                    "Battery":     batt
                }

                update_state(device.address, parsed)
                print(device.address, parsed)

            except Exception as e:
                print("PARSE ERROR:", e)

# ===== MAIN LOOP =====
async def main():
    global last_publish

    scanner = BleakScanner(callback)
    await scanner.start()

    while True:
        await asyncio.sleep(5)

        # publish every 55 seconds regardless of sensor updates
        if time.time() - last_publish > PUBLISH_INTERVAL:
            if state:
                publish()


if __name__ == "__main__":
    asyncio.run(main())
