import time
import random
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "ry5d1jc4WSqPOvfX4N91l56iOn9xwwC4cgpD_DGW5uCNexNhvOIsHQLlTP1hGVxKCTL7sBRitvGlouTs4u6juA=="
INFLUXDB_ORG = "OTH"
INFLUXDB_BUCKET = "sensor_data"

# Initialize the InfluxDB client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def generate_data():
    """Generate synthetic time series data for pressure, humidity, temperature, and sensor ID."""
    timestamp = datetime # Correctly set the current UTC timestamp
    pressure = round(random.uniform(950, 1050), 2)  # hPa
    humidity = round(random.uniform(30, 90), 2)  # %
    temperature = round(random.uniform(-10, 35), 2)  # Celsius
    appliance_id = random.randint(1, 11)

    return {
        "timestamp": timestamp,
        "pressure": pressure,
        "humidity": humidity,
        "temperature": temperature,
        "appliance_id": appliance_id,
    }

def write_to_influxdb(data):
    """Write a single data point to InfluxDB."""
    try:
        point = (
            Point("environment_data")
            .tag("appliance_id", data["appliance_id"])
            .field("pressure", data["pressure"])
            .field("humidity", data["humidity"])
            .field("temperature", data["temperature"])
            .time(data["timestamp"])
        )
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"Data written to InfluxDB: {data}")
    except Exception as e:
        print(f"Failed to write data to InfluxDB: {e}")

def main():
    """Main function to generate and send data in a loop."""
    try:
        while True:
            data = generate_data()
            print(f"Generated data: {data}")
            write_to_influxdb(data)
            print("Data written to InfluxDB.")
            time.sleep(10)  # Wait for 10 seconds before sending the next data point
    except KeyboardInterrupt:
        print("Stopped data generation.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
