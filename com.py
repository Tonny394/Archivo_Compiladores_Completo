#git add .
#git commit -m "mensaje"
#git push


from html import parser
from compilador import * 
from tokens import *

def main():
    #Ejemplo
    codigo_fuente = """
    int suma(int a, int b) {
      return a + b;
    }
    """

    #Ejemplo 2
    codigo_fuenteDos = """
    int suma(int a, int b) {
      int c = a + b;
      printf(c);
      return c;
    }
    """
    tokensDos = identificar_tokens(codigo_fuenteDos)
    tokens = identificar_tokens(codigo_fuente) 
    arbol_astDos = None
  
    #Prueba sintáctica
    try:
        print("Iniciando analisis sintactico")
        parser = Parser(tokens)
        arbol_ast = parser.parsear()
        print("Analisis sintactico exitoso")
    except SyntaxError as e:
        print(f"Error sintáctico: {e}")

    try:
        print("Iniciando analisis sintactico")
        parser = Parser(tokensDos)
        arbol_astDos = parser.parsear()
        print("Analisis sintactico exitoso")
    except SyntaxError as e:
        print(f"Error sintáctico: {e}")

    print(json.dumps(imprimir_ast(arbol_ast), indent=1))
    
    
    nodoExp = NodoOperacion(NodoNumero(5),'+',NodoNumero(8))
    print(json.dumps(imprimir_ast(nodoExp), indent=1))
    if arbol_astDos:
      print(arbol_astDos.traducirPy())

main()