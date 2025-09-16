# Miniature IoT MLOps Pipeline

This project is a fully functional, miniature MLOps system for an IoT use case, built to run locally on a Mac. It demonstrates a complete, automated loop: data ingestion, edge inference, model drift detection, automated retraining, and live monitoring.

### Core Features
- **Data Simulation:** A Python script simulates an IoT sensor publishing environmental data via MQTT.
- **Real-time Inference:** An edge service subscribes to the sensor data, makes predictions using a trained model, and monitors its own performance (RMSE).
- **Automated Drift Detection & Retraining:** If the model's performance degrades (RMSE exceeds a threshold), the system automatically triggers a training script to create and deploy a new model.
- **Experiment Tracking:** MLflow is used to log training runs, parameters, metrics, and models.
- **Live Dashboard:** A Streamlit dashboard provides a real-time view of the pipeline's health, model version, and live sensor data.

---

### How to Run the System

**Prerequisites:**
- macOS
- [Homebrew](https://brew.sh)
- Python 3.11+
- Git

**1. Setup Instructions**

First, clone the repository and set up the environment.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/edge-mlops-mini.git
cd edge-mlops-mini

# Install system dependencies (MQTT Broker)
brew install mosquitto

# Create a Python virtual environment and activate it
python3 -m venv .venv
source .venv/bin/activate

# Install required Python packages
pip install --upgrade pip
pip install -r requirements.txt
```







### Running the Services
Open four separate terminal windows/tabs in the project directory. Make sure to activate the virtual environment (source .venv/bin/activate) in each terminal where you'll run a Python script.
Terminal 1: Start the MQTT Broker
```bash
mosquitto -v
```
#### Terminal 2: Start the IoT Data Publisher
code
```bash
python devices/publisher.py
```
(Wait ~30 seconds for it to generate some initial data before starting the trainer for the first time or the edge service.)
#### Terminal 3: Start the Edge Inference & Drift Detection Service
(Before running this for the first time, you need a model. Run python cloud/train.py once manually.)
code
```bash
python app/edge_infer.py
```
#### Terminal 4: Start the Monitoring Dashboard
```bash
streamlit run dashboard/dashboard.py
```
Now, open your web browser to the local URL provided by Streamlit (usually http://localhost:8501).
#### (Optional) Terminal 5: View MLflow Experiments
```bash
mlflow ui --port 5001
```
Open your browser to http://localhost:5001.