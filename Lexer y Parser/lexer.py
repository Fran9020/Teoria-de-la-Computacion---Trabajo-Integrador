"""
Lexer (Analizador Léxico) para el lenguaje SART-V
Sistema Automatizado de Reconocimiento Topológico Vascular

Alfabeto del lenguaje (Sigma):
    F  -> segmento vascular
    V  -> tejido sano
    C  -> tejido patológico
    +  -> orientación derecha
    -  -> orientación izquierda
    [  -> inicio de rama
    ]  -> fin de rama

Los espacios en blanco son ignorados.
"""

from enum import Enum, auto
from dataclasses import dataclass


# ============================================================
# TIPOS DE TOKENS
# ============================================================

class TokenType(Enum):
    """Enumeración de todos los tipos de token reconocidos por el lexer."""
    F = auto()          # Segmento vascular
    V = auto()          # Tejido sano
    C = auto()          # Tejido patológico (cancerígeno)
    PLUS = auto()       # Giro a la derecha (+)
    MINUS = auto()      # Giro a la izquierda (-)
    LBRACKET = auto()   # Inicio de rama ([)
    RBRACKET = auto()   # Fin de rama (])
    EOF = auto()        # Fin de la entrada


# Mapeo directo: cada carácter válido del alfabeto Σ se asocia a su TokenType.
# Si el carácter no está acá ni es whitespace, es un error léxico.
SINGLE_CHAR_TOKENS = {
    "F": TokenType.F,
    "V": TokenType.V,
    "C": TokenType.C,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
}

# Caracteres de espacio en blanco que el lexer ignora silenciosamente
WHITESPACE = {" ", "\t", "\n", "\r"}


# ============================================================
# TOKEN
# ============================================================

@dataclass
class Token:
    """Representa un token individual producido por el lexer."""
    type: TokenType   # Tipo del token (F, V, C, +, -, [, ], EOF)
    value: str        # Valor literal del carácter fuente
    line: int         # Línea donde aparece (para reportar errores)
    column: int       # Columna donde aparece (para reportar errores)

    def __repr__(self):
        return (
            f"Token({self.type.name}, "
            f"'{self.value}', "
            f"line={self.line}, "
            f"col={self.column})"
        )


# ============================================================
# ERROR LÉXICO
# ============================================================

class LexicalError(Exception):

    def __init__(self, char: str, line: int, column: int):
        self.char = char
        self.line = line
        self.column = column

        super().__init__(
            f"Error léxico en línea {line}, columna {column}: "
            f"carácter '{char}' no pertenece al alfabeto Σ"
        )


# ============================================================
# LEXER
# ============================================================

class Lexer:
    """
    Analizador léxico: recibe el código fuente como string y lo
    convierte en una lista de tokens. Recorre carácter a carácter,
    clasificándolos según el alfabeto Σ del lenguaje SART-V.
    """

    def __init__(self, source: str):
        self.source = source      # Código fuente completo
        self.pos = 0              # Posición actual en el string
        self.length = len(source) # Longitud total del fuente

        # Tracking de posición para mensajes de error
        self.line = 1
        self.column = 1

    def advance(self):
        """Avanza una posición actualizando línea y columna."""

        current = self.source[self.pos]

        self.pos += 1

        if current == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

    def tokenize(self) -> list[Token]:
        """Recorre todo el código fuente y devuelve la lista completa de tokens."""

        tokens = []

        # --- Bucle principal: consumir carácter por carácter ---
        while self.pos < self.length:

            char = self.source[self.pos]

            # Caso 1: Ignorar espacios en blanco (no generan token)
            if char in WHITESPACE:
                self.advance()
                continue

            # Caso 2: Carácter pertenece al alfabeto Σ → generar token
            if char in SINGLE_CHAR_TOKENS:

                token = Token(
                    SINGLE_CHAR_TOKENS[char],
                    char,
                    self.line,
                    self.column
                )

                tokens.append(token)

                self.advance()
                continue

            # Caso 3: Carácter no reconocido → error léxico
            raise LexicalError(
                char,
                self.line,
                self.column
            )

        # Al terminar el recorrido, agregar token EOF (marca fin de entrada)
        tokens.append(
            Token(
                TokenType.EOF,
                "",
                self.line,
                self.column
            )
        )

        return tokens


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
        """
    ]

    casos_invalidos = [

        "FFF[+FX][-FV]",

        "FFF[+F1][-FV]",

        "FFF[*FV][-FV]",
    ]

    print("========== CASOS VÁLIDOS ==========")

    for cadena in casos_validos:

        print("\nEntrada:")
        print(cadena)

        lexer = Lexer(cadena)

        tokens = lexer.tokenize()

        for token in tokens:
            print(" ", token)

    print("\n========== CASOS INVÁLIDOS ==========")

    for cadena in casos_invalidos:

        print("\nEntrada:")
        print(cadena)

        try:
            Lexer(cadena).tokenize()

        except LexicalError as e:
            print(" ", e)
