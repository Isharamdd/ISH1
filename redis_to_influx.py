import redis
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import random
from datetime import datetime

# Redis Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# InfluxDB Configuration
INFLUXDB_URL = "http://localhost:8086"  
INFLUXDB_TOKEN = "ry5d1jc4WSqPOvfX4N91l56iOn9xwwC4cgpD_DGW5uCNexNhvOIsHQLlTP1hGVxKCTL7sBRitvGlouTs4u6juA=="
INFLUXDB_ORG = "OTH"
INFLUXDB_BUCKET = "sensor_data"

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
try:
    print("Connecting to Redis...")
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
    print("Connected to Redis successfully.")
except Exception as e:
    print(f"Redis connection error: {e}")

try:
    print("Connecting to InfluxDB...")
    influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    print("Connected to InfluxDB successfully.")
except Exception as e:
    print(f"InfluxDB connection error: {e}")

# Connect to InfluxDB
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def generate_data():
    """Generate synthetic time-series data."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    return {
        "timestamp": timestamp,
        "pressure": round(random.uniform(950, 1050), 2),
        "humidity": round(random.uniform(30, 90), 2),
        "temperature": round(random.uniform(-10, 35), 2),
        "sensor_id": random.randint(1, 42),
    }

def transfer_data():
    """Fetch sensor data from Redis and write it to InfluxDB."""
    keys = redis_client.keys("sensor:*:latest_sensor_data")
    points = []
    for key in keys:
        raw_data = redis_client.get(key)
        if raw_data:
            try:
                sensor_data = json.loads(raw_data)
                sensor_id = sensor_data.get("sensor_id")
                temperature = sensor_data.get("temperature")
                humidity = sensor_data.get("humidity")
                pressure = sensor_data.get("pressure")
                timestamp = sensor_data.get("timestamp")

                if None in (sensor_id, temperature, humidity, pressure, timestamp):
                    print(f"Skipping incomplete data for {key}: {sensor_data}")
                    continue

                points.append(
                    Point("sensor_data")
                    .tag("sensor_id", sensor_id)
                    .field("temperature", temperature)
                    .field("humidity", humidity)
                    .field("pressure", pressure)
                    .time(timestamp)
                )
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON for {key}: {e}")
            except Exception as e:
                print(f"Failed to process data for {key}: {e}")

    if points:
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
        print(f"Transferred {len(points)} data points to InfluxDB.")

    


if __name__ == "__main__":
    transfer_data()



