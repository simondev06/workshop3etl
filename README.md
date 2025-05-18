# Proyecto de prediccion indice de felicidad con machine learning y streaming en Kafka

Este proyecto tiene como objetivo predecir el índice de felicidad de varios paises en varios años diferentes, usando modelos de machine learning, ETL y procesamiento de datos en streaming con Kafka, esos resultados se almacenan en una base de datos postgresql y podrían luego analizarse con alguna visualización.

## Estructura del proeycto

```
workshop3etl/
│
├── data/                  
│   └── raw/               # datos inciales
│       └── 2015.csv
│       └── 2016.csv
│       └── 2017.csv
│       └── 2018.csv
│       └── 2019.csv
│   └── processed/         # datos transformados para el entrenmiento
│       └── happiness_ready.csv
├── docker-compose.yml     # yaml con logica de kafka
├── model/                 
│   └── modelo_regresion_felicidad.pkl
├── kafka/                 
│   ├── producer.py
│   ├── consumer.py
│   └── prueba_db.py       # prueba pa ver registros indivuiduales de la db 
├── db/                    # base de datos                                                                                                      
│   └── predictions.db
├── notebooks/             # EDA, entrenamiento y predicciones
│   ├── eda_model.ipynb
│   └── predictions.ipynb
├── .env                   # variables entorno
├── requirements.txt       # dependencias
├── README.md              
└── .gitignore             
```

---

## Variables entorno

crear un archivo .env:

```env
# Configuración kafka
KAFKA_BOOTSTRAP_SERVERS=(host:puerto)
KAFKA_TOPIC=(nombre del topic)

# Configuración de postgresql
PG_DBNAME=(nombre de db)
PG_USER=(crear user)
PG_PASSWORD=(poner pw)
PG_HOST=(host)
PG_PORT=(puerto)

# Rutas de archivos
MODEL_PATH=../model/rutamodelo.pkl
DATA_PROCESSED_PATH=../data/processed/rutadatosdeentrenamiento.csv
```

Este archivo se carga en los scripts mediante `dotenv`.

---

## Requisitos

Instalar las dependencias con:

```bash
pip install -r requirements.txt
```

**Dependencias:**

* pandas, numpy, scikit-learn
* psycopg2-binary
* python-dotenv
* kafka-python
* matplotlib
* jupyter

---

## Funcionamiento

### 1. ETL y EDA

El nb `notebooks/eda_model.ipynb` toma el archivo original, realiza limpieza, transformación y normalizacion de los datos para juntarlos y dejar un mismo dataset con toda la info completa y guarda el resultado final en `data/processed/happiness_ready.csv` además de hacer un analisis exploratorio con algunas visualizaciones.

### 2. Entrenamiento del modelo

En `notebooks/eda_model.ipynb` tambien se entrena un modelo de regresión lineal con los datos ya listos y se guardan tanto el modelo (`modelo_regresion_felicidad.pkl`) como las metricas.

### 3. Streaming con kafka

* **Producer (producer.py)**: Lee los datos procesados y envía uno a uno los registros al topico de Kafka (`happiness_topic`).
* **Consumer (consumer.py)**: Escucha el topic, toma cada mensaje, realiza la predicción con el modelo que habia entrenado, y guarda los resultados en la base de datos postgresql, que tiene los puntajes de felicidad de la predicción y los reales para la comparación.

### 4. Evaluación y Visualización

En `notebooks/predictions.ipynb` se leen los datos desde la tabla predictions en postgresql y se comparan las predicciones con los valores reales del índice de felicidad yse visualiza en forma de dispersion (real vs. predicho) y se pasan las metricas otra vez.

---

## Base de datos

Se utiliza **postgresql** para almacenar las predicciones. La tabla predictions contiene:

* `country`
* `year`
* `happiness_score_predicted` (la prediccion)
* `happiness_score_real` (el real)

---
## Instalacion y ejecucion local
```bash
# 1. clonar el repo
git clone https://github.com/simondev06/workshop3etl
cd workshop3etl

# 2. crear .env
# editar .env con lo que corresponda:
#   KAFKA_BOOTSTRAP_SERVERS=...
#   KAFKA_TOPIC=...
#   PG_DBNAME=...
#   PG_USER=...
#   PG_PASSWORD=...
#   PG_HOST=...
#   PG_PORT=...
#   MODEL_PATH=...
#   DATA_PROCESSED_PATH=...

# 3. crear y activar el venv de python
python3 -m venv venv
source venv/bin/activate

# 4. instalar la dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 5. levantar servicios con docker
docker-compose up -d
# verificar que estan activos
docker-compose ps

# 6. ejecutar notebook de EDA y preprocesamiento
jupyter notebook 
# buscar y ejecutar notebooks/eda_model.ipynb
# al final de eejcutar se habrá creado `model/modelo_regresion_felicidad.pkl`.

# 7. iniciar el consumer de Kafka
cd kafka
python consumer.py
# el consumer lee el topic, aplica el modelo para cada mensaje que recibe y va llenando la tabla predictions en la db
# dejar corriendo en primer plano

# 8. en otra terminal iniciar el producer
source venv/bin/activate
cd kafka
python producer.py
# envia cada fila en mensjaes de `happiness_ready.csv` al topic pa que consumer lo lea.

# 9. ejecutar notebook de evaluacion de las predicciones cuando el producer ha enviado todos los mensajes 
jupyter notebook notebooks/predictions.ipynb
# se conecta a postgresql, lee el puntaje predicho y el real y muestra las metricas y la dispersion.

# 10. ejecutar script de prueba de base de datos (opcional)
cd kafka
python prueba_db.py
# muestra un registro de la tabla predictions en la db (el query esta hecho para mostrar uno mediante el id asi que puede editarse y cambiar el id para ver otro regitsro)

# 11. parar servicios
# parar kafka y postgresql al terminar con 
docker-compose down
```
## contacto: sagru6@gmail.com
