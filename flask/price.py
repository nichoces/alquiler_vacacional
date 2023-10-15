import datetime
import holidays

def ajustar_precio(prediction, fechas):
    ES_holidays = holidays.ES()

    # Dividir el rango de fechas en "inicio" y "fin"
    fechas_split = fechas.split('-')

    # Obtener las fechas de inicio y fin
    fecha_inicio = datetime.datetime.strptime(fechas_split[0].strip(), '%d/%m/%Y')
    fecha_fin = datetime.datetime.strptime(fechas_split[1].strip(), '%d/%m/%Y')

    # Obtener los meses de inicio y fin
    mes_inicio = fecha_inicio.strftime('%B').lower()
    mes_fin = fecha_fin.strftime('%B').lower()

    # Calcular el factor de ajuste para el rango de meses
    factor_ajuste = 1.0  # Factor predeterminado
    meses_a_ajustar = {mes_inicio, mes_fin}

    if any(mes in meses_a_ajustar for mes in ['january', 'november', 'august']):
        factor_ajuste = 0.85  # Descuento del 15%
    elif any(mes in meses_a_ajustar for mes in ['june', 'october', 'december']):
        factor_ajuste = 1.15  # Recargo del 15%

    # Aplicar el factor de ajuste al precio
    precio_ajustado = prediction * factor_ajuste

    # Verificar si alguna de las fechas cae en un festivo y ajustar el precio en consecuencia
    for single_date in [fecha_inicio + datetime.timedelta(days=n) for n in range((fecha_fin - fecha_inicio).days + 1)]:
        if single_date in ES_holidays:
            # Si la fecha está en los festivos, aumentar el precio en un 20%
            precio_ajustado *= 1.2

    # Calcular el rango mínimo y máximo
    rango_minimo = precio_ajustado * 0.8

    rango_maximo = precio_ajustado * 1.2

    # Calcular la duración de la estancia en días
    duracion_estancia = (fecha_fin - fecha_inicio).days

    # Calcular el precio por estancia
    precio_por_estancia = precio_ajustado * duracion_estancia

    # Aplicar descuento del 10% si la estancia es de 7 días o más
    if duracion_estancia >= 7:
        precio_por_estancia *= 0.9

    # Calcular el rango mínimo y máximo de la estancia
    rango_minimo_estancia = precio_por_estancia * 0.8
    rango_maximo_estancia = precio_por_estancia * 1.2

    return {
        'precio_maximo_por_dia': round(rango_maximo, 2),
        'precio_minimo_por_dia': round(rango_minimo, 2),
        'precio_maximo_estancia': round(rango_maximo_estancia, 2),
        'precio_minimo_estancia': round(rango_minimo_estancia, 2)}