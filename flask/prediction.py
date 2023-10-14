from sklearn.preprocessing import LabelEncoder
import pickle
import numpy as np

def preprocess(tipo, distrito, habitaciones, baños, capacidad):
# Crear y ajustar el LabelEncoder directamente en el archivo prediction.py
    label_encoder = LabelEncoder()
    room_types = ['Private room', 'Entire home/apt', 'Shared room',] 
    label_encoder.fit(room_types)

    # Cargar modelos entrenados desde el archivo pickle
    with open('modelos_entrenados_xgboost_distritos.pkl', 'rb') as file:
        modelos_entrenados_xgboost = pickle.load(file)

        # Utiliza el LabelEncoder para transformar las categorías
        tipo = label_encoder.transform([tipo])[0]

        # Supongamos que tienes un modelo por distrito, selecciona el modelo correspondiente
        if distrito in modelos_entrenados_xgboost:
            modelo = modelos_entrenados_xgboost[distrito]
        else:
            # Puedes manejar este caso de error adecuadamente, por ejemplo, con un mensaje de error o un modelo predeterminado
            return None

        # Realiza cualquier otro preprocesamiento necesario en tus datos
        solicitud = np.array([tipo, habitaciones, baños, capacidad])

        # Retorna los datos necesarios para la predicción
        return solicitud

def estimation(solicitud, modelo):
    # Supongamos que solicitud es un conjunto de características preparadas para la predicción

    # Realiza la predicción utilizando el modelo cargado
    prediction = modelo.predict(solicitud.reshape(1, -1))

    # Devuelve el resultado de la predicción
    return prediction