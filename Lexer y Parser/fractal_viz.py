"""
Visualizacion Fractal del AST - SART-V
Sistema Automatizado de Reconocimiento Topologico Vascular


Recorre el AST generado por el Parser (capa de GRAMATICA, ya validada)
y lo interpreta mediante un modelo tipo turtle graphics (capa de
INTERPRETACION/SEMANTICA, separada de la gramatica) para generar
una imagen SVG de la red vascular.


Reglas de interpretacion:
    F           -> avanzar dibujando un segmento en la direccion actual
    + (en rama) -> la rama gira hacia la derecha respecto del padre
    - (en rama) -> la rama gira hacia la izquierda respecto del padre
    V (hoja)    -> el segmento final se dibuja en VERDE (tejido sano)
    C (hoja)    -> el segmento final se dibuja en ROJO (tejido patologico)


La longitud del segmento se reduce en cada nivel de profundidad,
generando el efecto de auto-similitud / fractal tipico de L-Systems,
sin que esto forme parte de la gramatica (que sigue siendo una GLC
secuencial estandar).
"""

import math
from parser import parse, Vaso, Rama, Tronco


# ============================================================
# PARAMETROS DEL DIBUJO
# ============================================================


# Parámetros geométricos del fractal (ajustables para cambiar el aspecto)
LONGITUD_INICIAL = 90      # longitud del tronco en píxeles
FACTOR_ESCALA = 0.72       # factor de reducción de longitud por cada nivel de profundidad
ANGULO = 28                # grados de desvío angular por cada giro ('+' o '-')
GROSOR_INICIAL = 6         # grosor de línea del tronco en píxeles
FACTOR_GROSOR = 0.7        # factor de reducción de grosor por cada nivel


# Paleta de colores para cada tipo de segmento vascular
COLOR_TRONCO = "#5b6b73"       # Gris-azulado: tronco principal
COLOR_SANO = "#2ecc71"         # Verde: tejido sano (V)
COLOR_PATOLOGICO = "#e74c3c"   # Rojo: tejido patológico/cancerígeno (C)
COLOR_RAMA_INTERNA = "#888888" # Gris: ramas intermedias que se siguen bifurcando




# ============================================================
# UTILIDADES GEOMETRICAS
# ============================================================


def punto_final(x, y, angulo_grados, longitud):
    """Devuelve el punto final de un segmento dado origen, angulo y longitud.


    Convencion: angulo 0 = hacia arriba (eje -Y en coordenadas SVG).
    """
    rad = math.radians(angulo_grados)
    nx = x + longitud * math.sin(rad)
    ny = y - longitud * math.cos(rad)
    return nx, ny




# ============================================================
# RECORRIDO RECURSIVO DEL AST -> LISTA DE SEGMENTOS SVG
# ============================================================


def recorrer_rama(rama: Rama, x, y, angulo, longitud, grosor, segmentos):
    """
    Procesa un nodo <rama> del AST de forma recursiva (turtle graphics).

    x, y      : punto de origen de esta rama (donde termina el padre)
    angulo    : direccion HEREDADA del padre (antes de aplicar el giro propio)
    longitud  : longitud del segmento de ESTE nivel
    grosor    : grosor de linea de ESTE nivel
    segmentos : lista acumuladora de (x1,y1,x2,y2,color,grosor)
    """
    # 1. Calcular el ángulo real: dirección heredada + giro propio
    delta = ANGULO if rama.giro == "+" else -ANGULO
    nuevo_angulo = angulo + delta

    # 2. Calcular el punto final del segmento con trigonometría
    x2, y2 = punto_final(x, y, nuevo_angulo, longitud)

    # 3a. Si es hoja: dibujar con color diagnóstico (V=verde, C=rojo)
    if rama.es_hoja():
        color = COLOR_SANO if rama.tejido.valor == "V" else COLOR_PATOLOGICO
        segmentos.append((x, y, x2, y2, color, grosor))
        return

    # 3b. Si es rama interna: dibujar en gris y recurrir a sub-ramas
    segmentos.append((x, y, x2, y2, COLOR_RAMA_INTERNA, grosor))

    # 4. Reducir escala (auto-similitud fractal) y procesar sub-ramas
    nueva_longitud = longitud * FACTOR_ESCALA
    nuevo_grosor = max(1.0, grosor * FACTOR_GROSOR)

    recorrer_rama(rama.primera_sub, x2, y2, nuevo_angulo, nueva_longitud, nuevo_grosor, segmentos)
    recorrer_rama(rama.segunda_sub, x2, y2, nuevo_angulo, nueva_longitud, nuevo_grosor, segmentos)




def recorrer_vaso(vaso: Vaso, x, y):
    """
    Punto de entrada del recorrido: procesa el nodo raíz <vaso>,
    dibuja el tronco vertical y delega las ramas.
    """
    segmentos = []

    # Dibujar el tronco (FFF) como un único segmento vertical (ángulo=0)
    x2, y2 = punto_final(x, y, 0, LONGITUD_INICIAL)
    segmentos.append((x, y, x2, y2, COLOR_TRONCO, GROSOR_INICIAL))

    # Escalar para el siguiente nivel de profundidad
    nueva_longitud = LONGITUD_INICIAL * FACTOR_ESCALA
    nuevo_grosor = max(1.0, GROSOR_INICIAL * FACTOR_GROSOR)

    # Procesar ambas ramas principales desde el extremo del tronco
    recorrer_rama(vaso.rama_1, x2, y2, 0, nueva_longitud, nuevo_grosor, segmentos)
    recorrer_rama(vaso.rama_2, x2, y2, 0, nueva_longitud, nuevo_grosor, segmentos)

    return segmentos




# ============================================================
# GENERACION DEL SVG
# ============================================================


def generar_svg(cadena: str, ancho=500, alto=500, titulo=None) -> str:
    """
    Función principal de este módulo: parsea la cadena, recorre el AST
    y devuelve un documento SVG completo como string.
    """
    # Parsear la cadena (si es inválida, se propaga la excepción)
    ast = parse(cadena)

    # Punto de origen: parte inferior-central del canvas (el árbol crece hacia arriba)
    x0, y0 = ancho / 2, alto - 30

    # Recorrer el AST y obtener la lista de segmentos a dibujar
    segmentos = recorrer_vaso(ast, x0, y0)

    # Convertir cada segmento en un elemento <line> de SVG
    lineas_svg = []
    for (x1, y1, x2, y2, color, grosor) in segmentos:
        lineas_svg.append(
            f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{grosor:.1f}" stroke-linecap="round" />'
        )

    # Título opcional en la parte superior del SVG
    titulo_svg = ""
    if titulo:
        titulo_svg = (
            f'  <text x="{ancho/2}" y="24" text-anchor="middle" '
            f'font-family="monospace" font-size="13" fill="#333">{titulo}</text>\n'
        )

    # Leyenda de colores (verde=sano, rojo=patológico)
    leyenda = f"""
  <g font-family="monospace" font-size="11" fill="#333">
    <circle cx="20" cy="{alto-46}" r="5" fill="{COLOR_SANO}" />
    <text x="32" y="{alto-42}">Tejido sano (V)</text>
    <circle cx="20" cy="{alto-26}" r="5" fill="{COLOR_PATOLOGICO}" />
    <text x="32" y="{alto-22}">Tejido patologico (C)</text>
  </g>
"""

    # Ensamblar el documento SVG completo
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" '
        f'viewBox="0 0 {ancho} {alto}">\n'
        f'  <rect width="{ancho}" height="{alto}" fill="#fafafa" />\n'
        f'{titulo_svg}'
        + "\n".join(lineas_svg) + "\n"
        + leyenda
        + "</svg>\n"
    )
    return svg
