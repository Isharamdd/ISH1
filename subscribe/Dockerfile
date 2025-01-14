FROM python:latest
WORKDIR /app
COPY dummysensor-subscribe.py .
RUN pip install --no-cache-dir paho-mqtt redis psycopg2-binary cryptography
CMD ["python", "dummysensor-subscribe.py"]

