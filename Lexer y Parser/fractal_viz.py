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


LONGITUD_INICIAL = 90      # longitud del tronco (px)
FACTOR_ESCALA = 0.72       # reduccion de longitud por nivel
ANGULO = 28                # grados de desvio por '+'/'-'
GROSOR_INICIAL = 6         # grosor de linea del tronco (px)
FACTOR_GROSOR = 0.7        # reduccion de grosor por nivel


COLOR_TRONCO = "#5b6b73"   # gris-azulado: tejido base
COLOR_SANO = "#2ecc71"     # verde: V
COLOR_PATOLOGICO = "#e74c3c"  # rojo: C
COLOR_RAMA_INTERNA = "#888888"  # ramas que se siguen bifurcando (no hoja)




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
    Procesa un nodo <rama> del AST.


    x, y      : punto de origen de esta rama (donde termina el padre)
    angulo    : direccion HEREDADA del padre (antes de aplicar el giro propio)
    longitud  : longitud del segmento de ESTE nivel
    grosor    : grosor de linea de ESTE nivel
    segmentos : lista acumuladora de (x1,y1,x2,y2,color,grosor)
    """
    # Aplicar el giro propio de esta rama respecto a la direccion heredada
    delta = ANGULO if rama.giro == "+" else -ANGULO
    nuevo_angulo = angulo + delta


    x2, y2 = punto_final(x, y, nuevo_angulo, longitud)


    if rama.es_hoja():
        # Hoja: el color depende del tejido (V=verde, C=rojo)
        color = COLOR_SANO if rama.tejido.valor == "V" else COLOR_PATOLOGICO
        segmentos.append((x, y, x2, y2, color, grosor))
        return


    # Rama interna (se bifurca de nuevo): dibujada en gris,
    # las hojas de sus sub-ramas son las que llevan el color diagnostico
    segmentos.append((x, y, x2, y2, COLOR_RAMA_INTERNA, grosor))


    # Las sub-ramas heredan la direccion de ESTA rama (nuevo_angulo),
    # parten desde (x2, y2), y reducen longitud/grosor (auto-similitud)
    nueva_longitud = longitud * FACTOR_ESCALA
    nuevo_grosor = max(1.0, grosor * FACTOR_GROSOR)


    recorrer_rama(rama.primera_sub, x2, y2, nuevo_angulo, nueva_longitud, nuevo_grosor, segmentos)
    recorrer_rama(rama.segunda_sub, x2, y2, nuevo_angulo, nueva_longitud, nuevo_grosor, segmentos)




def recorrer_vaso(vaso: Vaso, x, y):
    """
    Procesa el nodo raiz <vaso>: dibuja el tronco (siempre vertical,
    angulo=0) y luego ambas ramas principales partiendo de su extremo.
    """
    segmentos = []


    # Tronco: 3 segmentos F -> se dibuja como un unico segmento
    # de longitud LONGITUD_INICIAL, en direccion vertical (angulo=0)
    x2, y2 = punto_final(x, y, 0, LONGITUD_INICIAL)
    segmentos.append((x, y, x2, y2, COLOR_TRONCO, GROSOR_INICIAL))


    nueva_longitud = LONGITUD_INICIAL * FACTOR_ESCALA
    nuevo_grosor = max(1.0, GROSOR_INICIAL * FACTOR_GROSOR)


    # rama_1 y rama_2 parten del extremo del tronco, heredando angulo=0
    recorrer_rama(vaso.rama_1, x2, y2, 0, nueva_longitud, nuevo_grosor, segmentos)
    recorrer_rama(vaso.rama_2, x2, y2, 0, nueva_longitud, nuevo_grosor, segmentos)


    return segmentos




# ============================================================
# GENERACION DEL SVG
# ============================================================


def generar_svg(cadena: str, ancho=500, alto=500, titulo=None) -> str:
    """
    Parsea `cadena` (debe ser valida segun la gramatica), recorre el
    AST resultante, y devuelve un documento SVG (como string) con la
    representacion fractal de la red vascular.
    """
    ast = parse(cadena)  # si la cadena es invalida, lanza LexicalError/SyntaxErrorSARTV


    # Punto de origen: parte inferior-central del canvas, el arbol crece hacia arriba
    x0, y0 = ancho / 2, alto - 30


    segmentos = recorrer_vaso(ast, x0, y0)


    lineas_svg = []
    for (x1, y1, x2, y2, color, grosor) in segmentos:
        lineas_svg.append(
            f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{grosor:.1f}" stroke-linecap="round" />'
        )


    titulo_svg = ""
    if titulo:
        titulo_svg = (
            f'  <text x="{ancho/2}" y="24" text-anchor="middle" '
            f'font-family="monospace" font-size="13" fill="#333">{titulo}</text>\n'
        )


    leyenda = f"""
  <g font-family="monospace" font-size="11" fill="#333">
    <circle cx="20" cy="{alto-46}" r="5" fill="{COLOR_SANO}" />
    <text x="32" y="{alto-42}">Tejido sano (V)</text>
    <circle cx="20" cy="{alto-26}" r="5" fill="{COLOR_PATOLOGICO}" />
    <text x="32" y="{alto-22}">Tejido patologico (C)</text>
  </g>
"""


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
