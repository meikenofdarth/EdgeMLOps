# app/edge_infer.py

import paho.mqtt.client as mqtt
import json
import joblib
import numpy as np
import os
import subprocess
from collections import deque
from datetime import datetime

# --- Configuration ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_SENSORS = "roomA/sensors"
MODEL_DIR = "models"
STATE_FILE = "app/state.json"
N_LAGS = 5  # Must match the training script
RETRAIN_THRESHOLD_RMSE = 50.0 # If rolling RMSE exceeds this, trigger retrain
PREDICTION_BUFFER_SIZE = 100 # Keep last 100 (actual, prediction) pairs

# --- Global State ---
# Use a deque for an efficient rolling buffer
prediction_buffer = deque(maxlen=PREDICTION_BUFFER_SIZE)
# Use a deque to store the most recent sensor readings to build features
latest_voc_readings = deque(maxlen=N_LAGS)
model = None
model_version = "N/A"

# --- Helper Functions ---
def load_latest_model():
    """Loads the most recently created model file from the models directory."""
    global model, model_version
    try:
        model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith(".joblib")]
        if not model_files:
            print("No models found. Waiting for a model to be trained.")
            return False
        latest_model_file = max(model_files, key=lambda f: os.path.getctime(os.path.join(MODEL_DIR, f)))
        model_path = os.path.join(MODEL_DIR, latest_model_file)
        model = joblib.load(model_path)
        model_version = latest_model_file
        print(f"Successfully loaded model: {model_version}")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

def save_state():
    """Saves current pipeline state to a JSON file."""
    rolling_rmse = calculate_rolling_rmse()
    state = {
        "model_version": model_version,
        "buffer_size": len(prediction_buffer),
        "rolling_rmse": rolling_rmse,
        "retrain_threshold": RETRAIN_THRESHOLD_RMSE,
        "last_updated": datetime.now().isoformat()
    }
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def calculate_rolling_rmse():
    """Calculates RMSE from the current prediction buffer."""
    if len(prediction_buffer) < 2:
        return None # Not enough data
    actuals, predictions = zip(*prediction_buffer)
    return np.sqrt(np.mean((np.array(actuals) - np.array(predictions))**2))

# --- MQTT Callback ---
def on_message(client, userdata, msg):
    """Callback for when a message is received from MQTT."""
    global latest_voc_readings, model

    try:
        # 1. Decode message and get the actual VOC value
        payload = json.loads(msg.payload.decode())
        actual_voc = payload['voc_ppb']
        latest_voc_readings.append(actual_voc)

        # 2. Make prediction if we have enough data and a model
        if len(latest_voc_readings) == N_LAGS and model:
            # Prepare features (must be in the same order as training)
            features = np.array(list(latest_voc_readings)).reshape(1, -1)
            prediction = model.predict(features)[0]

            # 3. Store (prediction, actual) pair in buffer
            # Note: We store the *next* actual value with the prediction made from the *previous* steps
            prediction_buffer.append((actual_voc, prediction))

            # 4. Compute rolling RMSE and check for drift
            rolling_rmse = calculate_rolling_rmse()
            if rolling_rmse is not None:
                print(f"Actual: {actual_voc:<5} | Pred: {prediction:<5.1f} | Rolling RMSE: {rolling_rmse:.2f}")

                if rolling_rmse > RETRAIN_THRESHOLD_RMSE:
                    print(f"!!! DRIFT DETECTED !!! RMSE ({rolling_rmse:.2f}) > Threshold ({RETRAIN_THRESHOLD_RMSE}).")
                    print("--- Triggering model retraining ---")
                    # This is a blocking call. In a real system, you'd use a message queue or API call.
                    subprocess.run(["python", "cloud/train.py"], check=True)
                    print("--- Retraining finished. Reloading new model. ---")
                    load_latest_model()
                    prediction_buffer.clear() # Clear buffer after retraining
                    latest_voc_readings.clear()

            # 5. Save current state for the dashboard
            save_state()

    except json.JSONDecodeError:
        print("Error decoding JSON from MQTT message.")
    except Exception as e:
        print(f"An error occurred in on_message: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    # Load the initial model on startup
    if not load_latest_model():
        print("Could not load a model on startup. Please run the training script first.")
        exit()

    # Set up MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="edge_inference_service")
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(MQTT_TOPIC_SENSORS)
        print(f"Subscribed to topic: {MQTT_TOPIC_SENSORS}")
        client.loop_forever() # Blocks and processes network traffic
    except ConnectionRefusedError:
        print("Connection to MQTT broker refused. Is it running?")
    except KeyboardInterrupt:
        print("Edge inference service stopped.")
        client.disconnect()