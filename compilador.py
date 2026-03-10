import re
import pandas as pd
from PyPDF2 import PdfReader


token_patron = {
    "KEYWORD" : r'\b(if|else|while|for|return|int|float|bool|char|void)\b',
    "IDENTIFIER" : r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    "NUMBER" : r'\b\d+(\.\d+)?\b',
    "OPERATOR" : r'[\+\-\*\/=<>!]+',
    "DELIMITER" : r'[()\{\};,]',
    "WHITESPACE" : r'\s+',
}

def identificar_tokens(texto):
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)

    token_econtrado = []
    for match in patron_regex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":
                token_econtrado.append((valor, token))
                break
    return token_econtrado

# Implementar el analizador de los tokens
def parse(tokens):
    # Funcion auxiliar para consumir cada token
    def consume(tipo_esperado):
        global token_actual
        if token_actual[0] == tipo_esperado:
            global indice_token
            token_actual = tokens[indice_token]
            indice_token += 1
        else: # NO es el token esperado
            raise SyntaxError(f"Se esperaba {tipo_esperado} pero se encontro {token_actual[0]}")