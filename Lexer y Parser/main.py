"""
main.py - SART-V
Sistema Automatizado de Reconocimiento Topologico Vascular


Flujo completo para la demostracion en vivo:


    1. Lectura de la cadena de entrada (por argumento o por input()).
    2. Analisis lexico (Lexer)      -> tokens, o LexicalError.
    3. Analisis sintactico (Parser) -> AST, o SyntaxErrorSARTV.
    4. Si la cadena es ACEPTADA:
    - se muestra el AST como arbol de texto
    - se genera la visualizacion fractal en SVG


Uso:
    python3 main.py                          -> modo interactivo
    python3 main.py "FFF[+FV][-FC]"          -> cadena por argumento
    python3 main.py "FFF[+FV][-FC]" salida.svg   -> indica nombre de archivo SVG
"""


import sys


from lexer import Lexer, LexicalError, TokenType
from parser import Parser, SyntaxErrorSARTV, dibujar_ast
from fractal_viz import generar_svg




# --- Etapa 1+2 del pipeline: análisis léxico + sintáctico ---
def analizar(cadena: str):
    """
    Ejecuta lexer + parser sobre `cadena`.
    Devuelve (tokens, ast) si es aceptada.
    Lanza LexicalError o SyntaxErrorSARTV si es rechazada.
    """
    tokens = Lexer(cadena).tokenize()   # Análisis léxico → lista de tokens
    ast = Parser(tokens).parse()        # Análisis sintáctico → árbol AST
    return tokens, ast




# --- Salida formateada de los tokens generados por el lexer ---
def mostrar_tokens(tokens) -> None:
    print("\n--- Tokens generados (analisis lexico) ---")
    for tok in tokens:
        if tok.type == TokenType.EOF:
            print(f"  {tok.type.name}")
        else:
            print(f"  {tok.type.name:<10} valor='{tok.value}'  "
                f"linea={tok.line} col={tok.column}")




# --- Salida formateada del AST generado por el parser ---
def mostrar_ast(ast) -> None:
    print("\n--- AST generado (analisis sintactico) ---")
    dibujar_ast(ast)




# --- Generación del archivo SVG con la visualización fractal ---
def generar_imagen(cadena: str, archivo_salida: str) -> None:
    svg = generar_svg(cadena, titulo=cadena)  # Interpreta el AST y genera SVG
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"\n--- Visualizacion fractal generada ---")
    print(f"  Archivo SVG: {archivo_salida}")




# --- Pipeline completo: analizar → mostrar → generar imagen ---
def procesar(cadena: str, archivo_salida: str) -> bool:
    """
    Procesa una cadena de entrada mostrando cada etapa del pipeline.
    Devuelve True si la cadena fue ACEPTADA, False si fue RECHAZADA.
    """
    print(f"\nEntrada: {cadena!r}")

    # Intentar análisis léxico + sintáctico; capturar errores
    try:
        tokens, ast = analizar(cadena)
    except LexicalError as e:
        print("\nResultado: CADENA RECHAZADA (error lexico)")
        print(f"  {e}")
        return False
    except SyntaxErrorSARTV as e:
        print("\nResultado: CADENA RECHAZADA (error sintactico)")
        print(f"  {e}")
        return False

    # Si llegó acá, la cadena pertenece al lenguaje L(G)
    print("\nResultado: CADENA ACEPTADA")
    mostrar_tokens(tokens)                    # Mostrar tokens del lexer
    mostrar_ast(ast)                          # Mostrar árbol AST
    generar_imagen(cadena, archivo_salida)    # Generar visualización SVG
    return True




# --- Modo interactivo: el usuario ingresa cadenas por consola ---
def modo_interactivo() -> None:
    print("=" * 60)
    print("SART-V - Analizador de Redes Vasculares (GLC secuencial)")
    print("=" * 60)
    print("Ingrese una cadena sobre el alfabeto Sigma = {F,V,C,+,-,[,]}")
    print("(o 'salir' para terminar)\n")


    contador = 1
    while True:
        # Leer entrada del usuario
        try:
            cadena = input("Cadena> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFin.")
            break

        # Salir si el usuario lo indica o deja vacío
        if cadena.lower() in ("salir", "exit", "quit", ""):
            print("Fin.")
            break

        # Procesar la cadena y generar SVG numerado
        archivo_salida = f"salida_{contador}.svg"
        procesar(cadena, archivo_salida)
        contador += 1
        print()




# --- Punto de entrada principal: decide modo interactivo o por argumento ---
def main():
    args = sys.argv[1:]

    # Sin argumentos → modo interactivo (bucle de entrada)
    if not args:
        modo_interactivo()
        return

    # Con argumentos → procesar cadena directamente
    cadena = args[0]
    archivo_salida = args[1] if len(args) > 1 else "salida.svg"

    aceptada = procesar(cadena, archivo_salida)
    sys.exit(0 if aceptada else 1)  # Código de salida: 0=aceptada, 1=rechazada




if __name__ == "__main__":
    main()
