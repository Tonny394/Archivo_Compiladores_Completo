from compilador import *
from tokens import * 

codigoFuente = """
int suma(int a, int b, int c){
    return a + b;
    cout << "1";
}

int main(){
    int hola = 3;
}
"""

# Análisis léxico
tokens = identificarTokens(codigoFuente)

print("========= Elementos ==========")
for elemento in tokens:
    print(f"{elemento}\n")

print("=======Analisis Sintactico ===========")
# Análisis sintáctico
try:
    print("Iniciando analisis sintactico")
    parser = Parse(tokens)
    arbol_ast = parser.parsear()
    print("Analisis sintactico exitoso")

    # Imprimir el AST
    print(json.dumps(imprimir_ast(arbol_ast), indent=1))

    print("========= Traducciones ===============")
    # Traducir a Python
    print("========= Python ===============")
    print(arbol_ast.traducirPy())
    #Traducir a ruby 
    print("========= Ruby ===============")
    print(arbol_ast.traducirRuby())
except SyntaxError as e:
    print(f"Error sintáctico: {e}")