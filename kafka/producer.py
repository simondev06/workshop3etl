from dotenv import load_dotenv
import os
from kafka import KafkaProducer
import pandas as pd
import json
import time

load_dotenv()
BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC  = os.getenv("KAFKA_TOPIC")
DATA_FILE = os.getenv("DATA_PROCESSED_PATH")

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

df = pd.read_csv(DATA_FILE)

for _, row in df.iterrows():
    message = row.to_dict()
    producer.send(TOPIC, value=message)
    print(f"Mensaje enviado: {message}")
    time.sleep(1)

producer.flush()

