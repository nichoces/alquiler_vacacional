import pandas as pd
import pickle
import json

# Cargar el LabelEncoder previamente entrenado
with open('flask/LabelEncoder_model.pkl', 'rb') as le_file:
    label_encoder = pickle.load(le_file)

room_type_encoder = label_encoder['room_type']
neighbourhood_encoder = label_encoder['neighbourhood']

# Cargar modelos entrenados
with open('flask/modelos_entrenados_xgboost_distritos.pkl', 'rb') as file:
    modelos_entrenados_xgboost_distritos = pickle.load(file)

# Función para realizar la predicción
def predict_price(distrito, predicciones):
    #distrito en el que quieres hacer la predicción
    if distrito in modelos_entrenados_xgboost_distritos:
        modelo = modelos_entrenados_xgboost_distritos[distrito]
    else:
        print(f"Error: No se encontró el modelo para el distrito {distrito}")

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

# Función para extraer el R2 de un distrito en porcentaje
def calcular_r2_porcentaje(distrito):

    with open('flask/r2_por_distrito.json', 'r', encoding='utf-8') as file:
        distrito_r2 = json.load(file)

    r2 = distrito_r2.get(distrito, 0.0)

    r2_porcentaje = r2 * 100
    r2_porcentaje = round(r2_porcentaje, 2)

    return r2_porcentaje