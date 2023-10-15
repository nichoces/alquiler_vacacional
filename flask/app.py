from flask import Flask, request, render_template, jsonify, redirect, url_for
import sys
import requests
import datetime
from flask_cors import CORS
import json

# Importa la función de predicción desde prediction.py
from prediction import predict_price
from price import ajustar_precio

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173, https://trip-jun-bridge.netlify.app"}})

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('form'))

@app.route('/form', methods=['GET', 'POST'])
def form():
    try:
        if request.method == 'POST':
            distrito = request.form['distrito']
            tipo = request.form['room_type_encoded']
            capacidad = int(request.form['accommodates'])
            habitaciones = int(request.form['bedrooms'])
            camas = int(request.form['beds'])
            num_bathrooms = int(request.form['num_bathrooms'])
            fechas = request.form['fechas']
            neighbourhood_encoded = request.form['neighbourhood_encoded']
            grouped_reviews = int(request.form['Grouped_reviews'])

            # Crea un JSON con las características introducidas por el usuario
            data = {
                'distrito': distrito,
                'room_type_encoded': tipo,
                'accommodates': capacidad,
                'bedrooms': habitaciones,
                'beds': camas,
                'num_bathrooms': num_bathrooms,
                'fechas': fechas,
                'neighbourhood_encoded': neighbourhood_encoded,
                'Grouped_reviews': grouped_reviews
            }

            # Envía los datos a la ruta /api/predict
            response = requests.post('http://localhost:3500/api/predict', json=data)

            if response.status_code == 200:
                try:
                    prediction_data = response.json()
                except json.JSONDecodeError:
                    return "Error: La respuesta del servidor no es un JSON válido", 500
            else:
                return f"Error: {response.status_code}", response.status_code

            precio_maximo_por_dia = prediction_data.get('precio_maximo_por_dia')
            precio_minimo_por_dia = prediction_data.get('precio_minimo_por_dia')
            precio_maximo_estancia = prediction_data.get('precio_maximo_estancia')
            precio_minimo_estancia = prediction_data.get('precio_minimo_estancia')

            return render_template('prediction.html',
                                precio_maximo_por_dia=precio_maximo_por_dia,
                                precio_minimo_por_dia=precio_minimo_por_dia,
                                precio_maximo_estancia=precio_maximo_estancia,
                                precio_minimo_estancia=precio_minimo_estancia)

        return render_template('form.html')
    
    except Exception as e:
        print(f"Error en form: {str(e)}", file=sys.stderr)
        return jsonify({'error': 'Error interno en el servidor'}), 500



@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json()

        # Extrae las características del JSON recibas
        distrito = data.get('distrito')
        tipo = data.get('room_type_encoded')
        capacidad = data.get('accommodates')
        habitaciones = data.get('bedrooms')
        camas = data.get('beds')
        num_bathrooms = data.get('num_bathrooms')
        fechas = data.get('fechas')
        neighbourhood_encoded = data.get('neighbourhood_encoded')
        grouped_reviews = data.get('Grouped_reviews')

        # Llama a la función de predicción desde prediction.py
        predicciones = [capacidad, habitaciones, camas, grouped_reviews, num_bathrooms, tipo, neighbourhood_encoded]
        precio_prediccion = predict_price(distrito, predicciones)

        if precio_prediccion is None:
            return jsonify({'error': 'No se pudo realizar la predicción para el distrito especificado'}), 500

# Aplica la función ajustar_precio
        precio_ajustado = ajustar_precio(precio_prediccion, fechas)

# Devuelve la valoración del modelo en formato JSON
        return jsonify(precio_ajustado)

    except Exception as e:
        # Captura cualquier excepción, loga y devuelve una respuesta genérica al cliente.
        print(f"Error al procesar la solicitud: {str(e)}", file=sys.stderr)
        return jsonify({'error': 'Error interno en el servidor'}), 500
    
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run(debug=True, port=3500)