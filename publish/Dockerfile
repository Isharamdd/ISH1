FROM python:latest
WORKDIR /app
COPY dummysensor-publish.py .
RUN pip install --no-cache-dir paho-mqtt redis psycopg2-binary cryptography
RUN python --version         # Check Python version
RUN pip freeze               # Verify installed dependencies
CMD ["python", "dummysensor-publish.py"]