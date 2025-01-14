import time
import random
import json
import redis
import paho.mqtt.client as mqtt
from cryptography.fernet import Fernet

# MQTT Configuration
BROKER = "mqtt-broker"
PORT = 1883
TOPIC_PREFIX = "sensor"  # Topic prefix for sensors
SENSOR_IDS = range(1, 7)  # Total of 6 sensors

# Redis Configuration
REDIS_HOST = "redis"
REDIS_PORT = 6379

# Load encryption key
with open("encryption_key_user1.key", "rb") as key_file:
    key = key_file.read()
cipher = Fernet(key)

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Sensor type categories and fields
SENSOR_TYPES = {
    1: {
        "name": "Fire/CO Detection",
        "fields": {
            "co_detection": lambda: round(random.uniform(0.0, 10.0), 2),  # CO level in air
            "smart_level": lambda: random.choice(["Low", "Moderate", "High"]),
            "temperature": lambda: round(random.uniform(20.0, 25.0), 2),
            "humidity": lambda: round(random.uniform(30.0, 50.0), 2),
            "timestamp": lambda: time.strftime("%Y-%m-%d %H:%M:%S")
        }
    },
    2: {
        "name": "Leak/Moisture Detection",
        "fields": {
            "moisture_detection_level": lambda: random.choice(["Dry", "Wet", "Flood"]),
            "leakage": lambda: random.choice(["No Leak", "Minor Leak", "Major Leak"]),
            "timestamp": lambda: time.strftime("%Y-%m-%d %H:%M:%S")
        }
    },
    3: {
        "name": "Window & Door Open/Close Detection",
        "fields": {
            "status": lambda: random.choice(["Open", "Close"]),
            "timestamp": lambda: time.strftime("%Y-%m-%d %H:%M:%S")
        }
    },
    4: {
        "name": "Smart Thermostat",
        "fields": {
            "temperature": lambda: round(random.uniform(18.0, 28.0), 2),
            "humidity": lambda: round(random.uniform(40.0, 60.0), 2),
            "timestamp": lambda: time.strftime("%Y-%m-%d %H:%M:%S")
        }
    },
    5: {
        "name": "Motion Sensors",
        "fields": {
            "motion": lambda: random.choice(["Detected", "Not Detected"]),
            "temperature": lambda: round(random.uniform(20.0, 30.0), 2),
            "light": lambda: round(random.uniform(100.0, 800.0), 2),
            "humidity": lambda: round(random.uniform(30.0, 50.0), 2),
            "vibration": lambda: round(random.uniform(0.01, 0.10), 3),
            "uv": lambda: round(random.uniform(0.0, 3.0), 2),
            "timestamp": lambda: time.strftime("%Y-%m-%d %H:%M:%S")
        }
    },
    6: {
        "name": "Smart Garage Door",
        "fields": {
            "status": lambda: random.choice(["Door Open", "Door Close"]),
            "timestamp": lambda: time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
}

# Publish dummy sensor data for all sensors
def publish_dummy_data():
    while True:
        for sensor_id in SENSOR_IDS:
            # Get sensor details
            sensor_type = SENSOR_TYPES.get(sensor_id, {})
            if not sensor_type:
                continue

            # Generate sensor data dynamically, ensuring 'sensor_name' comes first
            sensor_data = {
                "sensor_name": sensor_type["name"],
                "sensor_id": sensor_id,
                **{field: generator() for field, generator in sensor_type["fields"].items()}
            }

            # Serialize and encrypt the data
            json_data = json.dumps(sensor_data)
            encrypted_message = cipher.encrypt(json_data.encode())

            # Save encrypted data to Redis
            redis_key = f"sensor{sensor_id}:latest_sensor_data"
            redis_client.set(redis_key, encrypted_message.decode())

            # Publish encrypted payload to MQTT
            topic = f"{TOPIC_PREFIX}{sensor_id}/data"
            client.publish(topic, encrypted_message)
            print(f"Published encrypted data to topic {topic}: {encrypted_message.decode()}")

        # Delay to simulate real-time data
        time.sleep(5)

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = lambda client, userdata, flags, rc: print("Connected to MQTT broker" if rc == 0 else f"Failed to connect, return code {rc}")

# Connect to MQTT broker and start publishing
try:
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    publish_dummy_data()
except Exception as e:
    print(f"Failed to connect or publish: {e}")
finally:
    client.loop_stop()
    client.disconnect()
