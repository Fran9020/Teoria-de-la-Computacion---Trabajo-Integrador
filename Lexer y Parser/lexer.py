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
    F = auto()
    V = auto()
    C = auto()
    PLUS = auto()
    MINUS = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    EOF = auto()


SINGLE_CHAR_TOKENS = {
    "F": TokenType.F,
    "V": TokenType.V,
    "C": TokenType.C,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
}

WHITESPACE = {" ", "\t", "\n", "\r"}


# ============================================================
# TOKEN
# ============================================================

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

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

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.length = len(source)

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

        tokens = []

        while self.pos < self.length:

            char = self.source[self.pos]

            # Ignorar espacios en blanco
            if char in WHITESPACE:
                self.advance()
                continue

            # Token válido
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

            # Error léxico
            raise LexicalError(
                char,
                self.line,
                self.column
            )

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
