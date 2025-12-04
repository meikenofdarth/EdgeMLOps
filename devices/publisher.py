# devices/publisher.py (Corrected for Testability)

import paho.mqtt.client as mqtt
import json
import time
import random
import csv
import os
from datetime import datetime

# --- Constants and Config (Safe to run on import) ---
MQTT_BROKER = "broker"
MQTT_PORT = 1883
MQTT_TOPIC = "roomA/sensors"
DATA_FILE = "data/raw.csv"
PUBLISH_INTERVAL_S = 2
CSV_HEADER = ["timestamp", "temp_c", "humidity", "voc_ppb"]

# --- Functions (Safe to run on import) ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Publisher: Connected to MQTT Broker!")
    else:
        print(f"Publisher: Failed to connect, return code {reason_code}\n")

def generate_sensor_data(current_voc_state):
    voc_change = random.uniform(-15.0, 15.0)
    new_voc = current_voc_state + voc_change
    if new_voc < 50: new_voc = 50
    if new_voc > 400: new_voc = 400
    
    payload = {
        "timestamp": datetime.now().isoformat(),
        "temp_c": round(random.uniform(20.0, 25.0), 2),
        "humidity": round(random.uniform(40.0, 60.0), 2),
        "voc_ppb": int(new_voc)
    }
    return payload, new_voc

# --- Main application logic ---
def main():
    """Main function to run the publisher service."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor_publisher")
    client.on_connect = on_connect

    connected = False
    while not connected:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT)
            connected = True
        except ConnectionRefusedError:
            print("Publisher: Connection refused. Retrying in 5 seconds...")
            time.sleep(5)

    client.loop_start()

    try:
        current_voc = 150.0
        while True:
            payload, current_voc = generate_sensor_data(current_voc)
            payload_json = json.dumps(payload)
            
            result = client.publish(MQTT_TOPIC, payload_json)
            if result.rc == 0:
                print(f"Published to `{MQTT_TOPIC}`: {payload_json}")
            else:
                print(f"Failed to send message to topic {MQTT_TOPIC}")

            with open(DATA_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([payload["timestamp"], payload["temp_c"], payload["humidity"], payload["voc_ppb"]])

            time.sleep(PUBLISH_INTERVAL_S)

    except KeyboardInterrupt:
        print("Publisher stopped.")
        client.loop_stop()
        client.disconnect()

# --- This guard ensures this code only runs when the script is executed directly ---
if __name__ == "__main__":
    main()