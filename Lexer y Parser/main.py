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




def analizar(cadena: str):
    """
    Ejecuta lexer + parser sobre `cadena`.
    Devuelve (tokens, ast) si es aceptada.
    Lanza LexicalError o SyntaxErrorSARTV si es rechazada.
    """
    tokens = Lexer(cadena).tokenize()
    ast = Parser(tokens).parse()
    return tokens, ast




def mostrar_tokens(tokens) -> None:
    print("\n--- Tokens generados (analisis lexico) ---")
    for tok in tokens:
        if tok.type == TokenType.EOF:
            print(f"  {tok.type.name}")
        else:
            print(f"  {tok.type.name:<10} valor='{tok.value}'  "
                f"linea={tok.line} col={tok.column}")




def mostrar_ast(ast) -> None:
    print("\n--- AST generado (analisis sintactico) ---")
    dibujar_ast(ast)




def generar_imagen(cadena: str, archivo_salida: str) -> None:
    svg = generar_svg(cadena, titulo=cadena)
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"\n--- Visualizacion fractal generada ---")
    print(f"  Archivo SVG: {archivo_salida}")




def procesar(cadena: str, archivo_salida: str) -> bool:
    """
    Procesa una cadena de entrada mostrando cada etapa del pipeline.
    Devuelve True si la cadena fue ACEPTADA, False si fue RECHAZADA.
    """
    print(f"\nEntrada: {cadena!r}")


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


    print("\nResultado: CADENA ACEPTADA")
    mostrar_tokens(tokens)
    mostrar_ast(ast)
    generar_imagen(cadena, archivo_salida)
    return True




def modo_interactivo() -> None:
    print("=" * 60)
    print("SART-V - Analizador de Redes Vasculares (GLC secuencial)")
    print("=" * 60)
    print("Ingrese una cadena sobre el alfabeto Sigma = {F,V,C,+,-,[,]}")
    print("(o 'salir' para terminar)\n")


    contador = 1
    while True:
        try:
            cadena = input("Cadena> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFin.")
            break


        if cadena.lower() in ("salir", "exit", "quit", ""):
            print("Fin.")
            break


        archivo_salida = f"salida_{contador}.svg"
        procesar(cadena, archivo_salida)
        contador += 1
        print()




def main():
    args = sys.argv[1:]


    if not args:
        modo_interactivo()
        return


    cadena = args[0]
    archivo_salida = args[1] if len(args) > 1 else "salida.svg"


    aceptada = procesar(cadena, archivo_salida)
    sys.exit(0 if aceptada else 1)




if __name__ == "__main__":
    main()
