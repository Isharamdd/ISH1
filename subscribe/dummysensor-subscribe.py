import redis
import json
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

# Callback for connection success
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")

        # Dynamically subscribe to all sensor topics
        for sensor_id in SENSOR_IDS:
            topic = f"{TOPIC_PREFIX}{sensor_id}/data"
            client.subscribe(topic)
            print(f"Subscribed to topic: {topic}")
    else:
        print(f"Failed to connect, return code {rc}")

# Callback for message reception
def on_message(client, userdata, message):
    try:
        # Decode the received encrypted message
        encrypted_message = message.payload.decode()

        # Decrypt the message
        decrypted_message = cipher.decrypt(encrypted_message.encode()).decode()
        print(f"Decrypted message: {decrypted_message}")

        # Parse the JSON payload
        try:
            sensor_data = json.loads(decrypted_message)  # Deserialize JSON
            print(f"Received JSON data: {sensor_data}")

            # Validate JSON structure
            required_keys = ["sensor_id", "sensor_name", "timestamp"]
            if not all(key in sensor_data for key in required_keys):
                raise ValueError(f"Incomplete JSON data: {sensor_data}")

            # Save the data to Redis (per SensorID)
            sensor_id = sensor_data["sensor_id"]
            redis_key = f"sensor{sensor_id}:latest_sensor_data"
            redis_client.set(redis_key, json.dumps(sensor_data))  # Store as a JSON string in Redis
            print(f"Latest sensor data saved to Redis for Sensor ID {sensor_id}: {sensor_data}")

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON for topic {message.topic}: {e}")

    except Exception as e:
        print(f"Failed to process message: {e}")

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker and start listening
try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except Exception as e:
    print(f"Failed to connect or listen: {e}")
finally:
    client.disconnect()
