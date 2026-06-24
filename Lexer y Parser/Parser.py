Código del parser


"""
Parser (Analizador Sintáctico) para el lenguaje SART-V
Sistema Automatizado de Reconocimiento Topológico Vascular

Gramática GLC secuencial (la que define la cátedra "ok" como adaptación
de la idea de L-System a una Gramática Libre de Contexto tradicional):

    <vaso>   ::= <tronco> "[" <rama> "]" "[" <rama> "]"
    <tronco> ::= "F" "F" "F"
    <rama>   ::= <giro> "F" <tejido>
                | <giro> "F" <tejido> "[" <rama> "]" "[" <rama> "]"
    <giro>   ::= "+" | "-"
    <tejido> ::= "V" | "C"

Estrategia: Parser Recursivo Descendente (Recursive Descent Parser).
Cada no-terminal de la gramática se traduce en un método de la clase Parser.

Notar que las dos alternativas de <rama> comparten el prefijo
"<giro> F <tejido>". Por lo tanto NO hace falta "adivinar" qué alternativa
tomar antes de empezar: se consume siempre el prefijo común, y AL FINAL
se mira (lookahead de 1 token) si el siguiente token es "[". Si lo es,
hay sub-ramas (segunda alternativa); si no, la rama termina ahí (primera
alternativa). Esto es lo que hace que la gramática sea LL(1).
"""

from dataclasses import dataclass, field
from typing import Optional, List

# Reutilizamos el lexer ya hecho por la cátedra/equipo.
from lexer import Lexer, Token, TokenType


# ============================================================
# NODOS DEL AST (Árbol Sintáctico Abstracto)
# ============================================================

@dataclass
class Tejido:
    """Nodo hoja: V (sano) o C (cancerígeno)."""
    valor: str  # "V" o "C"

    def __repr__(self):
        return f"Tejido({self.valor})"


@dataclass
class Rama:
    """
    Nodo <rama>.

    giro:   "+" o "-"  -> ESTA es la dirección geométrica real de ESTA rama.
    tejido: nodo Tejido (V o C)
    primera_sub / segunda_sub: sub-ramas opcionales (None si la rama es
        una hoja). Los nombres "primera"/"segunda" indican solamente el
        ORDEN en que aparecen en el texto (cuál corchete se abrió primero),
        NO una dirección izquierda/derecha. La dirección de cada sub-rama
        está, a su vez, en su propio campo `giro`.
    """
    giro: str
    tejido: Tejido
    primera_sub: Optional["Rama"] = None
    segunda_sub: Optional["Rama"] = None

    def es_hoja(self) -> bool:
        return self.primera_sub is None and self.segunda_sub is None

    def __repr__(self):
        if self.es_hoja():
            return f"Rama({self.giro}F{self.tejido.valor})"
        return (f"Rama({self.giro}F{self.tejido.valor}, "
                f"1ra={self.primera_sub}, 2da={self.segunda_sub})")


@dataclass
class Tronco:
    """Nodo <tronco>. Siempre 'FFF', no necesita datos adicionales."""

    def __repr__(self):
        return "Tronco(FFF)"


@dataclass
class Vaso:
    """
    Nodo raíz <vaso>.

    rama_1 / rama_2: igual que en Rama, estos nombres indican el ORDEN
    de aparición en el texto (primer corchete / segundo corchete),
    NO una dirección izquierda/derecha. La dirección real de cada una
    está en su propio campo `giro`.
    """
    tronco: Tronco
    rama_1: Rama
    rama_2: Rama

    def __repr__(self):
        return f"Vaso(tronco={self.tronco}, rama_1={self.rama_1}, rama_2={self.rama_2})"


# ============================================================
# ERROR SINTÁCTICO
# ============================================================

class SyntaxErrorSARTV(Exception):
    """
    Análogo a LexicalError, pero para errores de sintaxis.
    Se lanza cuando el token actual no es el esperado por la gramática.
    """

    def __init__(self, esperado: str, token: Token):
        self.esperado = esperado
        self.token = token
        super().__init__(
            f"Error sintáctico en línea {token.line}, columna {token.column}: "
            f"se esperaba {esperado} pero se encontró "
            f"'{token.value}' (token {token.type.name})"
        )


# ============================================================
# PARSER RECURSIVO DESCENDENTE
# ============================================================

class Parser:
    """
    Recibe una lista de tokens (producida por el Lexer) y construye
    el AST si la cadena pertenece al lenguaje L(G). Si no pertenece,
    lanza SyntaxErrorSARTV indicando dónde y qué se esperaba.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------
    # Utilidades básicas de navegación
    # ------------------------------------------------------
    def current(self) -> Token:
        """Token actual (lookahead de 1)."""
        return self.tokens[self.pos]

    def advance(self) -> Token:
        """Consume el token actual y avanza al siguiente."""
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def check(self, *tipos: TokenType) -> bool:
        """¿El token actual es de alguno de estos tipos?"""
        return self.current().type in tipos

    def expect(self, tipo: TokenType, descripcion: str) -> Token:
        """
        Consume el token actual SI Y SOLO SI es del tipo esperado.
        Si no, lanza un error sintáctico.
        """
        if self.current().type != tipo:
            raise SyntaxErrorSARTV(descripcion, self.current())
        return self.advance()

    # ------------------------------------------------------
    # Punto de entrada
    # ------------------------------------------------------
    def parse(self) -> Vaso:
        """
        <vaso> ::= <tronco> "[" <rama> "]" "[" <rama> "]"
        Punto de entrada de la gramática (axioma).
        Al final exige EOF: si quedan tokens sin consumir, la cadena
        tiene "basura" extra y debe rechazarse.
        """
        vaso = self.parse_vaso()
        self.expect(TokenType.EOF, "fin de cadena (EOF)")
        return vaso

    # ------------------------------------------------------
    # <vaso> ::= <tronco> "[" <rama> "]" "[" <rama> "]"
    # ------------------------------------------------------
    def parse_vaso(self) -> Vaso:
        tronco = self.parse_tronco()

        self.expect(TokenType.LBRACKET, "'[' (inicio de la 1ra rama)")
        rama_1 = self.parse_rama()
        self.expect(TokenType.RBRACKET, "']' (fin de la 1ra rama)")

        self.expect(TokenType.LBRACKET, "'[' (inicio de la 2da rama)")
        rama_2 = self.parse_rama()
        self.expect(TokenType.RBRACKET, "']' (fin de la 2da rama)")

        return Vaso(tronco=tronco, rama_1=rama_1, rama_2=rama_2)

    # ------------------------------------------------------
    # <tronco> ::= "F" "F" "F"
    # ------------------------------------------------------
    def parse_tronco(self) -> Tronco:
        self.expect(TokenType.F, "'F' (1er segmento del tronco)")
        self.expect(TokenType.F, "'F' (2do segmento del tronco)")
        self.expect(TokenType.F, "'F' (3er segmento del tronco)")
        return Tronco()

    # ------------------------------------------------------
    # <rama> ::= <giro> "F" <tejido>
    #          | <giro> "F" <tejido> "[" <rama> "]" "[" <rama> "]"
    #
    # Las dos alternativas comparten el prefijo "<giro> F <tejido>".
    # Se consume ese prefijo siempre, y luego se decide con
    # lookahead(1) si hay sub-ramas o no.
    # ------------------------------------------------------
    def parse_rama(self) -> Rama:
        giro = self.parse_giro()
        self.expect(TokenType.F, "'F' (segmento de la rama)")
        tejido = self.parse_tejido()

        primera_sub: Optional[Rama] = None
        segunda_sub: Optional[Rama] = None

        # Lookahead: si lo que sigue es '[', esta rama se bifurca de nuevo.
        if self.check(TokenType.LBRACKET):
            self.advance()  # consume '['
            primera_sub = self.parse_rama()
            self.expect(TokenType.RBRACKET, "']' (fin de la 1ra sub-rama)")

            self.expect(TokenType.LBRACKET, "'[' (inicio de la 2da sub-rama)")
            segunda_sub = self.parse_rama()
            self.expect(TokenType.RBRACKET, "']' (fin de la 2da sub-rama)")

        # Si no es '[', no hacemos nada más: la rama es una hoja
        # (primera alternativa de la producción).

        return Rama(giro=giro, tejido=tejido,
                     primera_sub=primera_sub, segunda_sub=segunda_sub)

    # ------------------------------------------------------
    # <giro> ::= "+" | "-"
    # ------------------------------------------------------
    def parse_giro(self) -> str:
        if self.check(TokenType.PLUS):
            return self.advance().value
        if self.check(TokenType.MINUS):
            return self.advance().value
        raise SyntaxErrorSARTV("'+' o '-' (operador de ángulo)", self.current())

    # ------------------------------------------------------
    # <tejido> ::= "V" | "C"
    # ------------------------------------------------------
    def parse_tejido(self) -> Tejido:
        if self.check(TokenType.V):
            return Tejido(self.advance().value)
        if self.check(TokenType.C):
            return Tejido(self.advance().value)
        raise SyntaxErrorSARTV("'V' o 'C' (tejido sano o patológico)", self.current())


# ============================================================
# VISUALIZACIÓN DEL AST (árbol de texto)
# ============================================================

def _etiqueta(nodo) -> str:
    """
    Devuelve una etiqueta corta y legible para un nodo del AST,
    usada como texto de cada "caja" del árbol dibujado.
    """
    if isinstance(nodo, Vaso):
        return "Vaso"
    if isinstance(nodo, Tronco):
        return "Tronco (FFF)"
    if isinstance(nodo, Rama):
        tipo = "hoja" if nodo.es_hoja() else "bifurcación"
        return f"Rama [{nodo.giro}F{nodo.tejido.valor}]  ({tipo})"
    if isinstance(nodo, Tejido):
        nombre = "sano" if nodo.valor == "V" else "patológico"
        return f"Tejido {nodo.valor} ({nombre})"
    return repr(nodo)


def _hijos(nodo) -> List[tuple]:
    """
    Devuelve la lista de hijos de un nodo como tuplas (nombre_rama, nodo_hijo).
    'nombre_rama' es la etiqueta que indica QUÉ representa ese hijo dentro
    del padre (ej: "tronco", "rama_1", "1ra sub-rama", etc.).
    Los hijos con valor None (sub-ramas inexistentes en una hoja) se omiten.
    """
    hijos = []

    if isinstance(nodo, Vaso):
        hijos.append(("tronco", nodo.tronco))
        hijos.append(("rama_1", nodo.rama_1))
        hijos.append(("rama_2", nodo.rama_2))

    elif isinstance(nodo, Rama):
        hijos.append(("tejido", nodo.tejido))
        if nodo.primera_sub is not None:
            hijos.append(("1ra sub-rama", nodo.primera_sub))
        if nodo.segunda_sub is not None:
            hijos.append(("2da sub-rama", nodo.segunda_sub))

    # Tronco y Tejido son nodos hoja: no tienen hijos.

    return hijos


def dibujar_ast(nodo, prefijo: str = "", nombre_rama: Optional[str] = None, es_ultimo: bool = True) -> None:
    """
    Imprime el AST como un árbol de texto, con conectores tipo:

        Vaso
        ├── tronco: Tronco (FFF)
        ├── rama_1: Rama [+FV]  (bifurcación)
        │   ├── tejido: Tejido V (sano)
        │   ├── 1ra sub-rama: Rama [+FV]  (hoja)
        │   │   └── tejido: Tejido V (sano)
        │   └── 2da sub-rama: Rama [-FV]  (hoja)
        │       └── tejido: Tejido V (sano)
        └── rama_2: ...

    Es una función RECURSIVA: cada nodo se dibuja a sí mismo y delega
    el dibujo de sus hijos llamándose de nuevo, igual que el parser
    se llama a sí mismo para construir el árbol.

    `nombre_rama=None` identifica al nodo RAÍZ: se imprime sin conector
    ni prefijo. Todos los demás nodos (los que sí tienen un padre)
    reciben un `nombre_rama` (ej: "tronco", "rama_1", "1ra sub-rama")
    y se dibujan con su conector "├── " o "└── ".
    """
    if nombre_rama is None:
        # Nodo raíz: se imprime "pelado", sin conector ni prefijo.
        print(_etiqueta(nodo))
    else:
        conector = "└── " if es_ultimo else "├── "
        print(f"{prefijo}{conector}{nombre_rama}: {_etiqueta(nodo)}")

    hijos = _hijos(nodo)

    # El prefijo que heredan los NIETOS depende de si ESTE nodo fue
    # el último hijo de su padre (no se dibuja más "│" en esa columna)
    # o no (se sigue dibujando "│" para conectar con el siguiente hermano).
    if nombre_rama is None:
        nuevo_prefijo = ""  # los hijos del root arrancan sin indentación previa
    else:
        extension = "    " if es_ultimo else "│   "
        nuevo_prefijo = prefijo + extension

    for i, (nombre_hijo, hijo) in enumerate(hijos):
        ultimo_hijo = (i == len(hijos) - 1)
        dibujar_ast(hijo, nuevo_prefijo, nombre_hijo, ultimo_hijo)


# ============================================================
# FUNCIÓN DE CONVENIENCIA
# ============================================================

def parse(cadena: str) -> Vaso:
    """Atajo: tokeniza y parsea una cadena de entrada en un solo paso."""
    tokens = Lexer(cadena).tokenize()
    return Parser(tokens).parse()


# ============================================================
# PRUEBAS
# ============================================================

if __name__ == "__main__":
    casos_validos = [
        "FFF[+FV][-FV]",
        "FFF[+FV][-FC]",
        "FFF[+FV[+FV][-FV]][-FC[-FC][+FC]]",
        """
        FFF
        [+FV]
        [-FC]
        """,
    ]

    casos_invalidos = [
        "FF[+FV][-FV]",        # tronco con solo 2 F -> error sintáctico
        "FFF[+FV][-FV]extra",  # sobra texto después del vaso -> error (EOF)
        "FFF[+FV]",            # falta la segunda rama -> error sintáctico
        "FFF[*FV][-FV]",       # '*' no es un giro válido (y de hecho
                               # tampoco pasa el lexer: error léxico)
    ]

    print("========== CASOS VÁLIDOS ==========")
    for cadena in casos_validos:
        print("\nEntrada:", repr(cadena.strip()))
        try:
            ast = parse(cadena)
            print("  ACEPTADA. AST:")
            print("   ", ast)
        except SyntaxErrorSARTV as e:
            print("  RECHAZADA:", e)

    print("\n========== CASOS INVÁLIDOS ==========")
    for cadena in casos_invalidos:
        print("\nEntrada:", repr(cadena.strip()))
        try:
            ast = parse(cadena)
            print("  ACEPTADA (inesperado). AST:")
            print("   ", ast)
        except SyntaxErrorSARTV as e:
            print("  RECHAZADA:", e)
        except Exception as e:
            print("  ERROR (léxico u otro):", e)

    print("\n========== ÁRBOL (AST) DE UN CASO CON SUB-RAMAS ==========")
    cadena_ejemplo = "FFF[+FV[+FV][-FV]][-FC[-FC][+FC]]"
    print("\nEntrada:", cadena_ejemplo, "\n")
    ast = parse(cadena_ejemplo)
    dibujar_ast(ast)

Salida del parser:

Vaso
├── tronco: Tronco (FFF)
├── rama_1: Rama [+FV]  (bifurcación)
│   ├── tejido: Tejido V (sano)
│   ├── 1ra sub-rama: Rama [+FV]  (hoja)
│   │   └── tejido: Tejido V (sano)
│   └── 2da sub-rama: Rama [-FV]  (hoja)
│       └── tejido: Tejido V (sano)
└── rama_2: Rama [-FC]  (bifurcación)
    ├── tejido: Tejido C (patológico)
    ├── 1ra sub-rama: Rama [-FC]  (hoja)
    │   └── tejido: Tejido C (patológico)
    └── 2da sub-rama: Rama [+FC]  (hoja)
        └── tejido: Tejido C (patológico)
