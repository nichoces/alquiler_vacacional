import datetime
import holidays

ES_holidays = holidays.ES()

# Función para ajustar el precio según las fechas
def ajustar_precio(prediction, fecha):
    # Dividir el rango de fechas en "inicio" y "fin"
    fechas_split = fecha.split('-')

    # Obtener los meses de inicio y fin
    mes_inicio = datetime.datetime.strptime(fechas_split[0], '%d/%m/%Y').strftime('%B').lower()
    mes_fin = datetime.datetime.strptime(fechas_split[1], '%d/%m/%Y').strftime('%B').lower()

    # Calcular el factor de ajuste para el rango de meses
    factor_ajuste = 1.0  # Factor predeterminado
    meses_a_ajustar = set([mes_inicio, mes_fin])

    if any(mes in meses_a_ajustar for mes in ['enero', 'noviembre', 'agosto']):
        factor_ajuste = 0.85  # Descuento del 15%
    elif any(mes in meses_a_ajustar for mes in ['junio', 'octubre', 'diciembre']):
        factor_ajuste = 1.15  # Recargo del 15%

    # Aplicar el factor de ajuste al precio
    precio_ajustado = prediction * factor_ajuste

    # Obtener el año actual
    año_actual = datetime.datetime.now().year

    # Verifica si el año es el año actual
    if datetime.datetime.strptime(fechas_split[0], '%d/%m/%Y').year == año_actual:
        # Obtén los festivos del año actual
        festivos = ES_holidays.get(año_actual)
        
        # Convierte las fechas del rango a objetos datetime
        fecha_inicio = datetime.datetime.strptime(fechas_split[0], '%d/%m/%Y')
        fecha_fin = datetime.datetime.strptime(fechas_split[1], '%d/%m/%Y')

        # Verifica si alguna de las fechas cae en un festivo y ajusta el precio en consecuencia
        for single_date in [fecha_inicio + datetime.timedelta(days=n) for n in range((fecha_fin - fecha_inicio).days + 1)]:
            if single_date in festivos:
                # Si la fecha está en los festivos, aumenta el precio en un 10%
                precio_ajustado *= 1.1



    return precio_ajustado