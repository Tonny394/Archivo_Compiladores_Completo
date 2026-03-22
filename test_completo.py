from compilador import *
from tokens import *
import json

# Código fuente con todas las instrucciones: if, else, while, for, print, println
codigoFuente = """
int main(){
    int x = 5;
    
    if (x > 3) {
        print(x);
    }
    else {
        print(0);
    }
    
    int i = 0;
    while (i < 3) {
        println(i);
        i = i + 1;
    }
    
    for (i = 0; i < 5; i = i + 1) {
        int result = i * 2;
    }
}
"""

print("========= Elementos Léxicos ==========")
# Análisis léxico
tokens = identificarTokens(codigoFuente)

for elemento in tokens:
    print(f"{elemento}")

print("\n=======Análisis Sintáctico ===========")
# Análisis sintáctico
try:
    print("Iniciando análisis sintáctico...")
    parser = Parse(tokens)
    arbol_ast = parser.parsear()
    print("✓ Análisis sintáctico exitoso\n")

    # Imprimir el AST
    print("========= Árbol de Sintaxis Abstracta (AST) ===============")
    print(json.dumps(imprimir_ast(arbol_ast), indent=2))

    print("\n========= Traducciones ===============")
    
    # Traducir a Python
    print("\n========= Traducción a Python ===============")
    print(arbol_ast.traducirPy())
    
    # Traducir a Ruby
    print("\n========= Traducción a Ruby ===============")
    print(arbol_ast.traducirRuby())
    
except SyntaxError as e:
    print(f"❌ Error sintáctico: {e}")
