from Parametros import *
from compilador import *
import json

# Analizador sintactico 
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual
        else:
            raise SyntaxError(f"Error sintactico: Se esperaba {tipo_esperado} pero se encontro {token_actual}")
        
    def parsear(self):
        # Punto de entrada: Se espera una funcion
        self.funcion()

    def funcion(self):
        # Gramatica para una funcion: int IDENTIFIER (int IDENTIFIER)
        tipo_retorno = self.coincidir('KEYWORD')  # Tipo de retorno (ej. int)
        nombre_funcion = self.coincidir('IDENTIFIER')  # Nombre de la funcion
        self.coincidir('KEYWORD')  # Tipo de retorno (ej. int)
        if nombre_funcion[1] == 'main':
            parametros = []  # main no tiene parametros
        else:
            parametros = self.parametros()  # Regla para los parametros
        self.coincidir('DELIMITER')  # se espera un )
        self.coincidir('DELIMITER')  # se espera un {
        cuerpo = self.cuerpo() # Regla para el cuerpo de la funcion
        self.coincidir('DELIMITER')  # se espera un }
        return NodoFuncion(tipo_retorno, nombre_funcion, parametros, cuerpo)  # Cuerpo no implementado

    def parametros(self):
        list_parametros = []
        # Reglas para parametros: int IDENTIFIER (, int IDENTIFIER)*
        tipo = self.coincidir('KEYWORD')  # Tipo del parametro
        nombre = self.coincidir('IDENTIFIER')  # Nombre del parametro
        list_parametros.append(NodoParametro(tipo, nombre))
        while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
            self.coincidir('DELIMITER')  # como se encontro una coma sirve para cambiar de token
            tipo = self.coincidir('KEYWORD')  # Tipo del parametro
            nombre = self.coincidir('IDENTIFIER')  # Nombre del parametro 
            list_parametros.append(NodoParametro(tipo, nombre))
        return list_parametros

    def cuerpo(self):
        #Gramática para el cuerpo: return IDENTIFIER OPERATOR IDENTIFIER;
        instrucciones = []
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != '}':
            if self.obtener_token_actual()[1] == 'return':
                instrucciones.append(self.retorno())
            elif self.obtener_token_actual()[1] == 'printf':
                instrucciones.append(self.sentencia_print())
            else:
                instrucciones.append(self.asignacion())
        return instrucciones
        
    def asignacion(self): 
        tipo = self.coincidir ('KEYWORD')
        nombre = self.coincidir ('IDENTIFIER')
        operador = self.coincidir ('OPERATOR')
        expresion = self.expresion()
        self.coincidir ('DELIMITER')  # se espera un ;
        return NodoAsignacion(tipo, nombre, operador, expresion)

    def retorno (self):
        self.coincidir ('KEYWORD')  # se espera return
        expresion = self.expresion()
        self.coincidir ('DELIMITER')  # se espera un ;
        return NodoRetorno (expresion)
    
    def expresion(self):
        izquierda = self.termino()
        while self.obtener_token_actual() and self.obtener_token_actual()[0] != 'OPERATOR':
            operador = self.coincidir('OPERATOR')
            derecha = self.termino()
            izquierda = NodoOperacion(operador, izquierda, derecha)
        return izquierda
    
    def termino(self):
        token = self.obtener_token_actual()
        if token [0] == 'NUMBER':
            return NodoNumero(self.coincidir('NUMBER'))
        elif token [0] == 'IDENTIFIER':
            identificador = self.coincidir('IDENTIFIER')
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == '(':
                self.coincidir('DELIMITER')  
                argumentos = self.llamadaFuncion()
                self.coincidir('DELIMITER')  
                return NodoLlamadaFuncion(identificador, argumentos)
            else:
                return NodoIdent(identificador)
        else:
            raise SyntaxError(f"Error sintactico: Se esperaba un numero o identificador pero se encontro {token}")
    
    def llamadaFuncion(self):
        argumentos = []
        sigue = True
        token = self.obtener_token_actual()
        while sigue:
            sigue = False
            if token [0] == 'NUMBER':
                argumentos.append(NodoNumero(self.coincidir('NUMBER')))
            elif token [0] == 'IDENTIFIER':
                argumentos.append(NodoIdent(self.coincidir('IDENTIFIER')))
            else:
                raise SyntaxError(f"Error sintactico: Se esperaba un numero o identificador pero se encontro {token}")
            if self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
                self.coincidir('DELIMITER')  # se espera una coma
                token = self.obtener_token_actual()
                sigue = True
        return argumentos
    
    def sentencia_print(self):
        self.coincidir('IDENTIFIER') # Se espera printf
        self.coincidir('DELIMITER') # Se espera (
        expresion = self.expresion()
        self.coincidir('DELIMITER') # Se espera )
        self.coincidir('DELIMITER') # Se espera ;
        return NodoPrint(expresion)

def imprimir_ast(nodo):
    if isinstance(nodo, NodoFuncion):
      return { "Funcion" : nodo.nombre,
               "Parametros" : [imprimir_ast(p) for p in nodo.parametros],
               "Cuerpo" : [imprimir_ast(c) for c in nodo.cuerpo]}
    elif(isinstance(nodo, NodoParametro)):
      return {"Parametro" : nodo.nombre, "Tipo" : nodo.tipo}
    elif(isinstance(nodo, NodoAsignacion)):
      return {"Asignación" : nodo.nombre, "Expresion" : imprimir_ast(nodo.expresion)}
    elif isinstance(nodo, NodoOperacion):
      return {"Operacion" : nodo.operador,
              "Izquierda" : imprimir_ast(nodo.izquierda),
              "Derecha" : imprimir_ast(nodo.derecha)}
    elif isinstance(nodo, NodoRetorno):
      return {"Retorno" : imprimir_ast(nodo.expresion)}
    elif isinstance(nodo, NodoIdent):
      return {"Identificador" : nodo.nombre}
    elif isinstance(nodo, NodoNumero):
      return {"Numero" : nodo.valor}
    elif isinstance(nodo, NodoPrint):
      return {"Print" : imprimir_ast(nodo.expresion)}
    return {}