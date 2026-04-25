from compilador import *
from tokens import *
from Analisis_Sematico import AnalisisSemantico

codigoFuente = """
float calcular(float x, int y){
    float resultado = x + y;
    float entero = 5.0;
    float suma = resultado + entero;
    return suma;
}

int main(){
    float a = 3.5;
    int b = 2;
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

print("========= ANALIZADOR SINTACTICO Y SEMANTICO CON SOPORTE DE COMA FLOTANTE ==========")
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
    print("\n Analisis semantico:")
    # Análisis semántico
    try:
        analizador_semantico = AnalisisSemantico()
        analizador_semantico.analizar(arbol_ast)
        print(" Analisis semantico exitoso")
        
        print("\n Tabla de simbolos:")
        for simbolo, info in analizador_semantico.tabla_simbolos.items():
            print(f"  {simbolo}: {info}")
    
    except Exception as e:
        print(f" Error semantico: {e}")
    print("\n========= TRADUCCIONES ==========")
    # Traducir a Python
    print(" Python:")
    print(arbol_ast.traducirPy())

    # Traducir a Ruby
    print("\n Ruby:")
    print(arbol_ast.traducirRuby())

except SyntaxError as e:
    print(f" Error sintáctico: {e}")