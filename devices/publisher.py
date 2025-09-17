# # devices/publisher.py

# import paho.mqtt.client as mqtt
# import json
# import time
# import random
# import csv
# import os
# from datetime import datetime

# # --- Configuration ---
# MQTT_BROKER = "broker"
# MQTT_PORT = 1883
# MQTT_TOPIC = "roomA/sensors"
# DATA_FILE = "data/raw.csv"
# PUBLISH_INTERVAL_S = 2

# # --- CSV File Setup ---
# CSV_HEADER = ["timestamp", "temp_c", "humidity", "voc_ppb"]
# # Create data directory if it doesn't exist
# os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# # Write header if file is new
# if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
#     with open(DATA_FILE, 'w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow(CSV_HEADER)

# # --- MQTT Client Setup ---
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected to MQTT Broker!")
#     else:
#         print(f"Failed to connect, return code {rc}\n")

# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="sensor_publisher")
# client.on_connect = on_connect
# client.connect(MQTT_BROKER, MQTT_PORT)
# client.loop_start() # Handles reconnects automatically

# # --- Main Loop ---
# try:
#     while True:
#         # 1. Generate random but structured data
#         timestamp = datetime.now().isoformat()
#         temp_c = round(random.uniform(20.0, 25.0), 2)
#         humidity = round(random.uniform(40.0, 60.0), 2)
#         # voc_ppb = random.randint(50, 300) # Parts Per Billion
#         voc_ppb = random.randint(50, 300) + 200 # Parts Per Billion


#         payload = {
#             "timestamp": timestamp,
#             "temp_c": temp_c,
#             "humidity": humidity,
#             "voc_ppb": voc_ppb
#         }
#         payload_json = json.dumps(payload)

#         # 2. Publish to MQTT topic
#         result = client.publish(MQTT_TOPIC, payload_json)
#         status = result[0]
#         if status == 0:
#             print(f"Published to `{MQTT_TOPIC}`: {payload_json}")
#         else:
#             print(f"Failed to send message to topic {MQTT_TOPIC}")


#         # 3. Append each message to data/raw.csv
#         with open(DATA_FILE, 'a', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow([timestamp, temp_c, humidity, voc_ppb])

#         time.sleep(PUBLISH_INTERVAL_S)

# except KeyboardInterrupt:
#     print("Publisher stopped.")
#     client.loop_stop()
#     client.disconnect()


# # devices/publisher.py

# import paho.mqtt.client as mqtt
# import json
# import time
# import random
# import csv
# import os
# from datetime import datetime

# # --- Configuration ---
# MQTT_BROKER = "broker"
# MQTT_PORT = 1883
# MQTT_TOPIC = "roomA/sensors"
# DATA_FILE = "data/raw.csv"
# PUBLISH_INTERVAL_S = 2

# # --- CSV File Setup ---
# CSV_HEADER = ["timestamp", "temp_c", "humidity", "voc_ppb"]
# os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
# if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
#     with open(DATA_FILE, 'w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow(CSV_HEADER)

# # --- FIX: Update to modern MQTT Callback API ---
# def on_connect(client, userdata, flags, reason_code, properties):
#     if reason_code.rc == 0:
#         print("Publisher: Connected to MQTT Broker!")
#     else:
#         print(f"Publisher: Failed to connect, return code {reason_code.rc}\n")

# # Use the recommended V2 of the callback API
# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor_publisher")
# client.on_connect = on_connect
# # --- End of Fix ---

# # --- Connection retry logic ---
# connected = False
# while not connected:
#     try:
#         client.connect(MQTT_BROKER, MQTT_PORT)
#         connected = True
#     except ConnectionRefusedError:
#         print("Publisher: Connection refused. Retrying in 5 seconds...")
#         time.sleep(5)

# client.loop_start()

# # --- Main Loop ---
# try:
#     while True:
#         timestamp = datetime.now().isoformat()
#         temp_c = round(random.uniform(20.0, 25.0), 2)
#         humidity = round(random.uniform(40.0, 60.0), 2)
#         # Revert to normal data for this test
#         voc_ppb = random.randint(50, 300)

#         payload = {"timestamp": timestamp, "temp_c": temp_c, "humidity": humidity, "voc_ppb": voc_ppb}
#         payload_json = json.dumps(payload)

#         result = client.publish(MQTT_TOPIC, payload_json)
#         # This check is good, but we also rely on the logs
#         if result[0] == 0:
#             print(f"Published to `{MQTT_TOPIC}`: {payload_json}")
#         else:
#             print(f"Failed to send message to topic {MQTT_TOPIC}")

#         with open(DATA_FILE, 'a', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow([timestamp, temp_c, humidity, voc_ppb])

#         time.sleep(PUBLISH_INTERVAL_S)

# except KeyboardInterrupt:
#     print("Publisher stopped.")
#     client.loop_stop()
#     client.disconnect()


# devices/publisher.py

import paho.mqtt.client as mqtt
import json
import time
import random
import csv
import os
from datetime import datetime

# --- Configuration ---
MQTT_BROKER = "broker"
MQTT_PORT = 1883
MQTT_TOPIC = "roomA/sensors"
DATA_FILE = "data/raw.csv"
PUBLISH_INTERVAL_S = 2

# --- CSV File Setup ---
CSV_HEADER = ["timestamp", "temp_c", "humidity", "voc_ppb"]
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)

# --- Update to modern MQTT Callback API ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.rc == 0:
        print("Publisher: Connected to MQTT Broker!")
    else:
        print(f"Publisher: Failed to connect, return code {reason_code.rc}\n")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor_publisher")
client.on_connect = on_connect

# --- Connection retry logic ---
connected = False
while not connected:
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        connected = True
    except ConnectionRefusedError:
        print("Publisher: Connection refused. Retrying in 5 seconds...")
        time.sleep(5)

client.loop_start()

# --- Main Loop ---
try:
    while True:
        timestamp = datetime.now().isoformat()
        temp_c = round(random.uniform(20.0, 25.0), 2)
        humidity = round(random.uniform(40.0, 60.0), 2)
        voc_ppb = random.randint(50, 300)

        payload = {"timestamp": timestamp, "temp_c": temp_c, "humidity": humidity, "voc_ppb": voc_ppb}
        payload_json = json.dumps(payload)

        result = client.publish(MQTT_TOPIC, payload_json)
        if result[0] == 0:
            print(f"Published to `{MQTT_TOPIC}`: {payload_json}")
        else:
            print(f"Failed to send message to topic {MQTT_TOPIC}")

        with open(DATA_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, temp_c, humidity, voc_ppb])

        time.sleep(PUBLISH_INTERVAL_S)

except KeyboardInterrupt:
    print("Publisher stopped.")
    client.loop_stop()
    client.disconnect()