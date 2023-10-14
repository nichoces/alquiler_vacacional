from flask import Flask, request, render_template, jsonify, redirect, url_for
import sys
import requests
import datetime
from flask_cors import CORS
import json


# Importa las funciones desde tus scripts personalizados
from prediction import preprocess, estimation
from price import ajustar_precio

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173, https://trip-jun-bridge.netlify.app"}})


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('form'))

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        distrito = request.form['distrito']
        subdistrito = request.form['subdistrito']
        tipo = request.form['room_type']
        capacidad = int(request.form['accomodates'])
        habitaciones = int(request.form['bedrooms'])
        baños = int(request.form['num_bathrooms'])
        fechas = request.form['fechas']

        # Prepara los datos en un diccionario JSON
        data = {
            'distrito': distrito,
            'subdistrito': subdistrito,
            'room_type': tipo,
            'bedrooms': habitaciones,
            'accomodates': capacidad,
            'num_bathrooms': baños,
            'fechas': fechas
        }

        # Envía los datos a la ruta /api/predict
        response = requests.post('http://localhost:3500/api/predict', json=data)

        # Comprobar si la respuesta tiene contenido y es JSON válido
        if response.status_code == 200:
            try:
                prediction_data = response.json()
            except json.JSONDecodeError:
        # Manejar el caso de que la respuesta no sea JSON válido
                return "Error: La respuesta del servidor no es un JSON válido", 500
        else:
        # Manejar el caso de que la solicitud no se haya realizado correctamente
            return f"Error: {response.status_code}", response.status_code

        # Procesa la respuesta JSON
        prediction_data = response.json()

        # Obtén los datos de la respuesta
        precio_maximo_por_dia = prediction_data.get('precio_maximo_por_dia')
        precio_minimo_por_dia = prediction_data.get('precio_minimo_por_dia')
        precio_maximo_estancia = prediction_data.get('precio_maximo_estancia')
        precio_minimo_estancia = prediction_data.get('precio_minimo_estancia')

        # Ajusta los precios según las fechas
        precio_maximo_por_dia = ajustar_precio(precio_maximo_por_dia, fechas)
        precio_minimo_por_dia = ajustar_precio(precio_minimo_por_dia, fechas)
        precio_maximo_estancia = ajustar_precio(precio_maximo_estancia, fechas)
        precio_minimo_estancia = ajustar_precio(precio_minimo_estancia, fechas)

        return render_template('prediction.html',
                               precio_maximo_por_dia=precio_maximo_por_dia,
                               precio_minimo_por_dia=precio_minimo_por_dia,
                               precio_maximo_estancia=precio_maximo_estancia,
                               precio_minimo_estancia=precio_minimo_estancia)

    return render_template('form.html')


@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json()

            # Verificando se os parâmetros esperados estão no JSON recebido
        expected_params = ['tipo', 'distrito', 'barrio', 'hab', 'banos', 'area', 'furnished']
        for param in expected_params:
            if param not in data:
                return jsonify({'error': f'Parâmetro {param} não fornecido'}), 400

        # Extraer detalles del JSON recibido
        tipo = data['room_type']
        distrito = data['distrito']
        subdistrito = data['subdistrito']
        habitaciones = data['bedrooms']
        capacidad = data['accomodates']  # Corrige el nombre de la clave
        baños = data['num_bathrooms']
        fechas = data['fechas']

        # Hacer la predicción
        solicitud = preprocess(tipo, distrito, subdistrito, habitaciones, baños, capacidad)
        prediction = estimation(solicitud)

        # Aplicar el factor de ajuste al precio por día
        prediction = ajustar_precio(prediction,fechas)

        # Calcular precio máximo y mínimo por día
        precio_maximo_por_dia = prediction * 1.2
        precio_minimo_por_dia = prediction * 0.8

        # Calcular la duración de la estancia en días
        fecha_inicio_obj = datetime.datetime.strptime(fechas.split('-')[0], '%d/%m/%Y')
        fecha_fin_obj = datetime.datetime.strptime(fechas.split('-')[1], '%d/%m/%Y')
        duracion_estancia = (fecha_fin_obj - fecha_inicio_obj).days

        # Calcular el precio mínimo y máximo de la estancia completa
        precio_minimo_estancia = precio_minimo_por_dia * duracion_estancia
        precio_maximo_estancia = precio_maximo_por_dia * duracion_estancia

        # Devuelve la valoración del modelo en formato JSON
        return jsonify({
            'precio_maximo_por_dia': precio_maximo_por_dia,
            'precio_minimo_por_dia': precio_minimo_por_dia,
            'precio_maximo_estancia': precio_maximo_estancia,
            'precio_minimo_estancia': precio_minimo_estancia     })

    except Exception as e:
        # Captura qualquer exceção, loga e retorna uma resposta genérica ao cliente.
        print(f"Erro ao processar a requisição: {str(e)}", file=sys.stderr)
        return jsonify({'error': 'Erro interno no servidor'}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=3500)