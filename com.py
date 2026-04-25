from compilador import *
from tokens import *

codigoFuente = """
int main(){
    float a = 3.5;
    float b = 2.5;
    float suma = a + b;
    float multiplicacion = a * b;
    float division = a / b;
    print(suma);
    print(multiplicacion);
    print(division);
}
"""

# Análisis léxico
tokens = identificarTokens(codigoFuente)

print("========= ANALIZADOR CON SOPORTE DE COMA FLOTANTE ==========")
print("\n Código fuente:")
print(codigoFuente)

print(" Elementos léxicos:")
for elemento in tokens:
    print(f"{elemento}")

print("\n Análisis sintáctico:")
# Análisis sintáctico
try:
    print("Iniciando análisis sintáctico...")
    parser = Parse(tokens)
    arbol_ast = parser.parsear()
    print(" Análisis sintáctico exitoso")

    # Imprimir el AST
    print("\n Árbol de Sintaxis Abstracta (AST):")
    print(json.dumps(imprimir_ast(arbol_ast), indent=2))

    print("\n========= TRADUCCIONES ==========")
    # Traducir a Python
    print(" Python:")
    print(arbol_ast.traducirPy())

    # Traducir a Ruby
    print("\n Ruby:")
    print(arbol_ast.traducirRuby())

except SyntaxError as e:
    print(f" Error sintáctico: {e}")