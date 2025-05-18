import os
import json
import joblib
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv()

BROKER      = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC       = os.getenv("KAFKA_TOPIC")
MODEL_PATH  = os.getenv("MODEL_PATH")

PG_DBNAME   = os.getenv("PG_DBNAME")
PG_USER     = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST     = os.getenv("PG_HOST")
PG_PORT     = os.getenv("PG_PORT")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="happiness_group"
)

model = joblib.load(MODEL_PATH)

conn = psycopg2.connect(
    dbname=PG_DBNAME,
    user=PG_USER,
    password=PG_PASSWORD,
    host=PG_HOST,
    port=PG_PORT
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    country TEXT,
    year INT,
    happiness_score_predicted FLOAT,
    happiness_score_real FLOAT
)
""")
conn.commit()

feature_columns = [
    "gdp_per_capita",
    "social_support",
    "healthy_life_expectancy",
    "freedom_to_make_life_choices",
    "generosity",
    "perceptions_of_corruption"
]

for message in consumer:
    data = message.value
    country    = data["country"]
    year       = int(data["year"])
    real_score = float(data["happiness_score"])
    df_features = pd.DataFrame([{
        "gdp_per_capita":              data["gdp_per_capita"],
        "social_support":              data["social_support"],
        "healthy_life_expectancy":     data["healthy_life_expectancy"],
        "freedom_to_make_life_choices":data["freedom_to_make_life_choices"],
        "generosity":                  data["generosity"],
        "perceptions_of_corruption":   data["perceptions_of_corruption"]
    }])
    prediction = float(model.predict(df_features)[0])

    cursor.execute(
        "INSERT INTO predictions (country, year, happiness_score_predicted, happiness_score_real) VALUES (%s, %s, %s, %s)",
        (country, year, prediction, real_score)
    )
    conn.commit()

    print(f"Procesado: {country} ({year}) → Predicción: {prediction:.4f}, Real: {real_score:.4f}")

