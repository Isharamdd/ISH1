from datetime import datetime
from influxdb_client import InfluxDBClient, Point
import random

# InfluxDB Configuration
INFLUX_URL = "http://localhost:8086"  # Replace with your InfluxDB URL
INFLUX_TOKEN = "ry5d1jc4WSqPOvfX4N91l56iOn9xwwC4cgpD_DGW5uCNexNhvOIsHQLlTP1hGVxKCTL7sBRitvGlouTs4u6juA=="
INFLUX_ORG = "OTH"
INFLUX_BUCKET = "sensor_data"

# Measurement Name
MEASUREMENT_NAME = "environment_data"

# Initialize InfluxDB Client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

def generate_data():
    """Generate synthetic time series data for pressure, humidity, temperature, and sensor ID."""
    timestamp = datetime
    pressure = round(random.uniform(950, 1050), 2)  # hPa
    humidity = round(random.uniform(30, 90), 2)  # %
    temperature = round(random.uniform(-10, 35), 2)  # Celsius
    sensor_id = 1
    #sensor_id = random.randint(1, 42)  # Sensor ID between 1 and 42

    return {
        "timestamp": timestamp,
        "pressure": pressure,
        "humidity": humidity,
        "temperature": temperature,
        "sensor_id": sensor_id,
    }

def add_data(sensor_id: int, temperature: float, humidity: float, pressure: float, timestamp: datetime):
    """
    Add data to the InfluxDB bucket 'sensor_data'.
    """
    data_point = (
        Point(MEASUREMENT_NAME)
        .tag("sensor_id", sensor_id)
        .field("temperature", temperature)
        .field("humidity", humidity)
        .field("pressure", pressure)
        .time(timestamp.isoformat())
    )
    write_api = client.write_api()
    write_api.write(bucket=INFLUX_BUCKET, record=data_point)
    print(f"Data added: {sensor_id=}, {temperature=}, {humidity=}, {pressure=}, {timestamp=}")

if __name__ == "__main__":
    # Example Data
    add_data(
        sensor_id=1,
        temperature=25.5,
        humidity=55.0,
        pressure=1015.0,
        timestamp=datetime.utcnow()
    )
