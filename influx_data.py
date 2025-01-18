import time
import random
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "9B_mtf5XgsMeN8OOr4lg6RFD8ZGyKkPlAj1cRZs8LxZLR6qwimyUZGT5goBKo9BecXlwB9bUtQsh3iFjcnMtpQ=="
INFLUXDB_ORG = "OTH"
INFLUXDB_BUCKET = "sensor_values"

# Initialize the InfluxDB client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def generate_sensor_data(sensor_id):
    """Generate synthetic sensor data for different sensor types."""
    timestamp = datetime.utcnow()  # Use UTC timestamp
    data = {}

    if sensor_id == 1:  # Fire/CO Detection
        data["co_detection"] = round(random.uniform(0.0, 10.0), 2)
        data["temperature"] = round(random.uniform(20.0, 25.0), 2)
        data["humidity"] = round(random.uniform(30.0, 50.0), 2)
        data["smoke_level"] = random.randint(0, 2)  # 0: Low, 1: Moderate, 2: High

    elif sensor_id == 2:  # Leak/Moisture Detection
        data["moisture_detection_level"] = random.randint(0, 2)  # 0: Dry, 1: Wet, 2: Flood
        data["leakage"] = random.randint(0, 2)  # 0: No Leak, 1: Minor Leak, 2: Major Leak

    elif sensor_id == 3:  # Window & Door Open/Close Detection
        data["status"] = random.randint(0, 1)  # 0: Closed, 1: Open

    elif sensor_id == 4:  # Smart Thermostat
        data["temperature"] = round(random.uniform(18.0, 28.0), 2)
        data["humidity"] = round(random.uniform(40.0, 60.0), 2)

    elif sensor_id == 5:  # Motion Sensors
        data["temperature"] = round(random.uniform(20.0, 30.0), 2)
        data["light"] = round(random.uniform(100.0, 800.0), 2)
        data["humidity"] = round(random.uniform(30.0, 50.0), 2)
        data["vibration"] = round(random.uniform(0.01, 0.10), 3)
        data["uv"] = round(random.uniform(0.0, 3.0), 2)
        data["motion"] = random.randint(0, 1)  # 0: Not Detected, 1: Detected

    elif sensor_id == 6:  # Smart Garage Door
        data["status"] = random.randint(0, 1)  # 0: Closed, 1: Open

    data["sensor_id"] = sensor_id
    data["timestamp"] = timestamp

    return data

def write_sensor_data_to_influxdb(data):
    """Write a single sensor data point to InfluxDB."""
    try:
        point = (
            Point("sensor_readings")
            .tag("sensor_id", str(data["sensor_id"]))
            .time(data["timestamp"])
        )

        for field, value in data.items():
            if field not in ["sensor_id", "timestamp"]:
                point.field(field, value)

        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"Data written to InfluxDB: {data}")
    except Exception as e:
        print(f"Failed to write data to InfluxDB: {e}")

def main():
    """Main function to generate and send sensor data in a loop."""
    try:
        while True:
            sensor_id = random.randint(1, 6)  # Select a random sensor
            sensor_data = generate_sensor_data(sensor_id)
            print(f"Generated data: {sensor_data}")
            write_sensor_data_to_influxdb(sensor_data)
            print("Data written to InfluxDB.")
            time.sleep(5)  # Wait for 5 seconds before sending the next data point
    except KeyboardInterrupt:
        print("Stopped data generation.")
    finally:
        client.close()

if __name__ == "__main__":
    main()