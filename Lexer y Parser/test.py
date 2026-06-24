"""
Casos de Prueba — Avance 4 (Testing)
Sistema Automatizado de Reconocimiento Topologico Vascular (SART-V)


Valida la capacidad del analizador (lexer + parser) para:
    - aceptar cadenas validas segun la gramatica L(G)
    - rechazar cadenas invalidas, reportando el error correspondiente(lexico o sintactico) con linea/columna


Cumple el requisito minimo: >= 8 casos validos, >= 3 invalidos.
Incluye ademas casos limite (borde del lenguaje).


Ejecucion:
    python3 test_sartv.py
"""


from lexer import Lexer, LexicalError
from parser import Parser, SyntaxErrorSARTV, parse, dibujar_ast




# ============================================================
# CASOS VALIDOS (>= 8 requeridos)
# ============================================================
# Cada caso: (id, cadena, descripcion)


CASOS_VALIDOS = [
    ("V01", "FFF[+FV][-FV]",
    "Vaso minimo, dos ramas hoja sanas (todo V)."),


    ("V02", "FFF[+FV][-FC]",
    "Vaso minimo, una rama sana y una patologica (mezcla V/C)."),


    ("V03", "FFF[+FC][-FC]",
    "Vaso minimo, ambas ramas patologicas (todo C)."),


    ("V04", "FFF[-FV][+FC]",
    "Vaso minimo, giros invertidos (-, +) respecto al orden tipico."),


    ("V05", "FFF[+FV[+FV][-FV]][-FC[-FC][+FC]]",
    "Cadena del Avance 1: bifurcacion en ambas ramas (caso recursivo "
    "en rama_1 y rama_2), profundidad 2."),


    ("V06", "FFF[+FV[+FV][-FC]][-FV]",
    "Bifurcacion solo en rama_1 (mixta sano/patologico); "
    "rama_2 es hoja. Profundidad asimetrica."),


    ("V07", "FFF[+FC[+FC[+FC][-FC]][-FC]][-FV]",
    "Anidamiento profundo (profundidad 3) en rama_1, "
    "simulando angiogenesis tumoral extendida; rama_2 hoja sana."),


    ("V08", "FFF [+FV] [-FC]",
    "Igual a V02 pero con espacios entre tokens: "
    "valida que el lexer ignora correctamente los espacios en blanco."),


    ("V09", """
        FFF
        [+FV]
        [-FC]
    """,
    "Igual a V02 pero con saltos de linea e indentacion: "
    "valida manejo de whitespace multilinea."),


    ("V10", "FFF[+FC[+FV][-FV]][-FC[+FC][-FV]]",
    "Caso limite: anidamiento simetrico en ambas ramas con "
    "tejidos mixtos en las hojas (V y C combinados)."),
]




# ============================================================
# CASOS INVALIDOS (>= 3 requeridos)
# ============================================================
# Cada caso: (id, cadena, descripcion, tipo_error_esperado)


CASOS_INVALIDOS = [
    ("I01", "FF[+FV][-FV]",
     "Tronco incompleto (solo 'FF', faltan 3 segmentos 'F').",
     "sintactico"),


    ("I02", "FFFF[+FV][-FV]",
     "Tronco con un segmento de mas ('FFFF').",
     "sintactico"),


    ("I03", "FFF[+FV]",
     "Falta la segunda rama obligatoria (rama_2).",
     "sintactico"),


    ("I04", "FFF[+FV][-FV][+FV]",
     "Tercera rama de mas a nivel raiz (la gramatica solo admite 2).",
     "lexico_o_sintactico"),


    ("I05", "FFF[+FV][-FC",
     "Corchete de cierre faltante (']' final ausente).",
     "sintactico"),


    ("I06", "FFF[+FV][-FX]",
     "Caracter 'X' no pertenece al alfabeto Sigma "
     "(token de tejido invalido).",
     "lexico"),


    ("I07", "FFF[*FV][-FV]",
     "Caracter '*' no pertenece a Sigma (giro invalido).",
     "lexico"),


    ("I08", "FFF[+FV][-FC]extra",
     "Texto sobrante despues de una cadena valida completa.",
     "lexico_o_sintactico"),


    ("I09", "[+FV][-FV]",
     "Falta el tronco 'FFF' al inicio de la cadena.",
     "sintactico"),


    ("I10", "FFF[+FV][-FC]]",
     "Corchete de cierre extra al final (desbalance de ']').",
     "lexico_o_sintactico"),
]




# ============================================================
# EJECUCION DE LA SUITE
# ============================================================


# --- Ejecutar todos los casos que DEBEN ser aceptados ---
def ejecutar_validos():
    print("=" * 70)
    print("CASOS VALIDOS (deben ser ACEPTADOS)")
    print("=" * 70)


    ok, fail = 0, 0
    for id_, cadena, desc in CASOS_VALIDOS:
        entrada_repr = repr(cadena.strip())
        try:
            ast = parse(cadena)  # Si no lanza excepción, fue aceptada (OK)
            print(f"[{id_}] OK   - {desc}")
            print(f"       entrada: {entrada_repr}")
            ok += 1
        except (LexicalError, SyntaxErrorSARTV) as e:
            print(f"[{id_}] FALLO - se esperaba ACEPTAR pero fue RECHAZADA")
            print(f"       entrada: {entrada_repr}")
            print(f"       error: {e}")
            fail += 1
        print()


    print(f"Resultado validos: {ok} OK / {fail} FALLOS "
        f"(total {len(CASOS_VALIDOS)})\n")
    return ok, fail




# --- Ejecutar todos los casos que DEBEN ser rechazados ---
def ejecutar_invalidos():
    print("=" * 70)
    print("CASOS INVALIDOS (deben ser RECHAZADOS)")
    print("=" * 70)


    ok, fail = 0, 0
    for id_, cadena, desc, tipo in CASOS_INVALIDOS:
        entrada_repr = repr(cadena)
        try:
            ast = parse(cadena)  # Si NO lanza excepción, es un fallo del test
            print(f"[{id_}] FALLO - se esperaba RECHAZAR pero fue ACEPTADA")
            print(f"       entrada: {entrada_repr}")
            print(f"       AST: {ast}")
            fail += 1
        except (LexicalError, SyntaxErrorSARTV) as e:
            print(f"[{id_}] OK   - {desc}")
            print(f"       entrada: {entrada_repr}")
            print(f"       rechazada ({type(e).__name__}): {e}")
            ok += 1
        print()


    print(f"Resultado invalidos: {ok} OK / {fail} FALLOS "
        f"(total {len(CASOS_INVALIDOS)})\n")
    return ok, fail




# --- Mostrar un ejemplo visual del AST en formato árbol de texto ---
def mostrar_ast_ejemplo():
    print("=" * 70)
    print("EJEMPLO DE AST (caso V05)")
    print("=" * 70)
    cadena = "FFF[+FV[+FV][-FV]][-FC[-FC][+FC]]"
    print(f"Entrada: {cadena}\n")
    ast = parse(cadena)
    dibujar_ast(ast)  # Imprime el árbol con conectores ├── └──
    print()




# --- Punto de entrada: ejecutar toda la suite y mostrar resumen ---
if __name__ == "__main__":
    ok_v, fail_v = ejecutar_validos()    # Correr casos válidos
    ok_i, fail_i = ejecutar_invalidos()  # Correr casos inválidos
    mostrar_ast_ejemplo()                # Mostrar ejemplo visual del AST

    # Resumen final con conteo de resultados
    print("=" * 70)
    print("RESUMEN GENERAL")
    print("=" * 70)
    total_ok = ok_v + ok_i
    total = len(CASOS_VALIDOS) + len(CASOS_INVALIDOS)
    print(f"Casos validos:   {ok_v}/{len(CASOS_VALIDOS)} correctos")
    print(f"Casos invalidos: {ok_i}/{len(CASOS_INVALIDOS)} correctos")
    print(f"TOTAL:           {total_ok}/{total} casos correctos")


    if fail_v == 0 and fail_i == 0:
        print("\nTodos los casos se comportaron como se esperaba.")
    else:
        print(f"\nATENCION: {fail_v + fail_i} caso(s) no se comportaron "
            f"como se esperaba. Revisar arriba.")
