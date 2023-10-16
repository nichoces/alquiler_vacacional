import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
import numpy as np
import warnings

warnings.filterwarnings("ignore")
# Cargar el LabelEncoder previamente entrenado
with open('/home/ubuntu/prod/alquiler_vacacional/LabelEncoder_model.pkl', 'rb') as le_file:
    label_encoder = pickle.load(le_file)

room_type_encoder = label_encoder['room_type']
neighbourhood_encoder = label_encoder['neighbourhood']

# Cargar modelos entrenados
with open('/home/ubuntu/prod/alquiler_vacacional/modelos_entrenados_xgboost_distritos.pkl', 'rb') as file:
    modelos_entrenados_xgboost_distritos = pickle.load(file)

# Función para realizar la predicción
def predict_price(distrito, predicciones):
    # Supongamos que distrito es el distrito en el que quieres hacer la predicción
    if distrito in modelos_entrenados_xgboost_distritos:
        modelo = modelos_entrenados_xgboost_distritos[distrito]
    else:
        # Manejar este caso de error adecuadamente, por ejemplo, con un mensaje de error o un modelo predeterminado
        return None

    # Crear un DataFrame con un índice
    dataframe_prediccion = pd.DataFrame([predicciones], 
        columns=["accommodates", "bedrooms", "beds", "Grouped_reviews", "num_bathrooms", "room_type_encoded", "neighbourhood_encoded"])

    # Modificar directamente los valores en el DataFrame
    dataframe_prediccion['neighbourhood_encoded'] = neighbourhood_encoder.transform(
        dataframe_prediccion['neighbourhood_encoded'])
    dataframe_prediccion['room_type_encoded'] = room_type_encoder.transform(
        dataframe_prediccion['room_type_encoded'])

    # Realizar la predicción
    precio_prediccion = modelo.predict(dataframe_prediccion)
    precio_prediccion = round(precio_prediccion[0], 2)

    return precio_prediccion
