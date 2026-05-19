from Parametros_2 import *
import json

#Analizador sintáctico
class Parse:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual
        else:
            raise SyntaxError(f"Error sintáctico: Se esperaba {tipo_esperado} pero se encontró: {token_actual}")

    def parsear(self):
        #Punto de entrada: se espera una función
        return self.funcion()

    def programa(self):
        pass

    def funcion(self):
        #Gramatica para una función: int IDENTIFIER (ind IDENTIFIER) {Cuerpo}
        tipo = self.coincidir('KEYWORD') # Retorna int
        nombre_funcion = self.coincidir('IDENTIFIER')
        self.coincidir('DELIMITER')
        if nombre_funcion[1] == 'main':
            parametros = []
        else: 
            parametros = self.parametros()
        self.coincidir('DELIMITER')
        self.coincidir('DELIMITER')
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER')
        return NodoFuncion(tipo, nombre_funcion, parametros, cuerpo)

    def parametros(self):
        lista_parametros = []
        #Reglas para parámetros int IDENTIFIER(, int IDENTIFIER)*
        tipo = self.coincidir("KEYWORD") #Tipo de parámetro
        nombre = self.coincidir('IDENTIFIER')
        lista_parametros.append(NodoParametro(tipo, nombre))

        while self.obtener_token() and self.obtener_token()[1] == ',':
            self.coincidir("DELIMITER") #Se espera una ,
            tipo = self.coincidir("KEYWORD") #Tipo de parámetro
            nombre = self.coincidir('IDENTIFIER')
            lista_parametros.append(NodoParametro(tipo, nombre))
        return lista_parametros

    def cuerpo(self):
        instrucciones = []
        while self.obtener_token() and self.obtener_token()[1] != '}':
            tok = self.obtener_token()[1]
            if tok == 'return':
                instrucciones.append(self.retorno())
            elif tok in ('printf', 'puts'):
                instrucciones.append(self.impresionPantalla())
            elif tok == 'if':
                instrucciones.append(self.condicional())
            elif tok == 'while':
                instrucciones.append(self.cicloWhile())
            elif tok == 'for':
                instrucciones.append(self.cicloFor())
            elif tok == 'scanf':
                instrucciones.append(self.entradaUsuario())
            else:
                instrucciones.append(self.asignacion())
        return instrucciones

    def asignacion(self):
        # Gramática para la estructura de asignación con o sin tipo.
        token = self.obtener_token()
        if token and token[0] == 'KEYWORD':
            tipo = self.coincidir('KEYWORD')
            nombre = self.coincidir('IDENTIFIER')
            operador = self.coincidir('OPERATOR')
            if operador[1] != '=':
                raise SyntaxError(f"Error sintáctico: se esperaba '=' después del identificador en la asignación, pero se encontró: {operador}")
            expresion = self.expresion()
            self.coincidir('DELIMITER')
            return NodoAsignacion(tipo, nombre, expresion)
        elif token and token[0] == 'IDENTIFIER':
            nombre = self.coincidir('IDENTIFIER')
            operador = self.coincidir('OPERATOR')
            if operador[1] != '=':
                raise SyntaxError(f"Error sintáctico: se esperaba '=' después del identificador en la asignación, pero se encontró: {operador}")
            expresion = self.expresion()
            self.coincidir('DELIMITER')
            return NodoAsignacion(None, nombre, expresion)
        else:
            raise SyntaxError(f"Error sintáctico en asignación: se esperaba un tipo o un identificador, pero se encontró: {token}")

    def retorno(self):
        self.coincidir('KEYWORD')
        expresion = self.expresion()
        self.coincidir('DELIMITER')
        return NodoRetorno(expresion)

    def expresion(self):
        izquierda = self.termino()
        while self.obtener_token() and self.obtener_token()[0] == "OPERATOR":
            operador = self.coincidir("OPERATOR")
            derecha = self.termino()
            izquierda = NodoOperacion(izquierda, operador, derecha)
        return izquierda

    def termino(self):
        token = self.obtener_token()
        if token and token[0] == "NUMBER":
            return NodoNumero(self.coincidir("NUMBER"))
        elif token and token[0] == "STRING":        
            return NodoString(self.coincidir("STRING"))
        elif token and token[0] == "IDENTIFIER":
            identificador = self.coincidir("IDENTIFIER")
            if self.obtener_token() and self.obtener_token()[1] == "(":
                self.coincidir("DELIMITER")
                argumentos = self.llamadaFuncion()
                self.coincidir("DELIMITER")
                return NodoLlamadaFuncion(identificador[1], argumentos)
            else:
                return NodoIdent(identificador)
        else:
            raise SyntaxError(f"Expresión no válida: {token}")
    
    def impresionPantalla(self):
        keyword = self.coincidir("KEYWORD")   # consume 'printf' o 'puts'
        self.coincidir("DELIMITER")           # consume '('
        expresion = self.expresion()
        self.coincidir("DELIMITER")           # consume ')'
        self.coincidir("DELIMITER")           # consume ';'
        return NodoImprimir(keyword, [expresion])

    def condicional(self):
        self.coincidir("KEYWORD")        # consume 'if'
        self.coincidir("DELIMITER")      # consume '('
        condicion = self.expresion()     # la condición: x > 5, a == b, etc.
        self.coincidir("DELIMITER")      # consume ')'
        self.coincidir("DELIMITER")      # consume '{'
        cuerpo_if = self.cuerpo()
        self.coincidir("DELIMITER")      # consume '}'

        cuerpo_else = []
        if self.obtener_token() and self.obtener_token()[1] == 'else':
            self.coincidir("KEYWORD")    # consume 'else'
            self.coincidir("DELIMITER")  # consume '{'
            cuerpo_else = self.cuerpo()
            self.coincidir("DELIMITER")  # consume '}'

        return NodoCondicional(condicion, cuerpo_if, cuerpo_else)

    def cicloWhile(self):
        self.coincidir("KEYWORD")        # consume 'while'
        self.coincidir("DELIMITER")      # consume '('
        condicion = self.expresion()
        self.coincidir("DELIMITER")      # consume ')'
        self.coincidir("DELIMITER")      # consume '{'
        cuerpo = self.cuerpo()
        self.coincidir("DELIMITER")      # consume '}'
        return NodoWhile(condicion, cuerpo)
    
    def cicloFor(self):
        self.coincidir("KEYWORD")        # consume 'for'
        self.coincidir("DELIMITER")      # consume '('
        inicio = self.asignacion()       # int i = 0;  -- ya consume el ';'
        condicion = self.expresion()
        self.coincidir("DELIMITER")      # consume ';'
        incremento = self.incremento()   # i++ o i = i + 1
        self.coincidir("DELIMITER")      # consume ')'
        self.coincidir("DELIMITER")      # consume '{'
        cuerpo = self.cuerpo()
        self.coincidir("DELIMITER")      # consume '}'
        return NodoFor(inicio, condicion, incremento, cuerpo)

    def incremento(self):
        # Maneja i++ o i--
        nombre = self.coincidir("IDENTIFIER")
        operador = self.coincidir("OPERATOR")  # ++ o --
        return NodoIncremento(nombre, operador)
    
    def entradaUsuario(self):
        keyword = self.coincidir("KEYWORD")   # consume 'scanf'
        self.coincidir("DELIMITER")           # consume '('
        formato = self.expresion()            # el string de formato "%d"
        self.coincidir("DELIMITER")           # consume ','  -- ajusta si usas OPERATOR
        variable = self.coincidir("IDENTIFIER")
        self.coincidir("DELIMITER")           # consume ')'
        self.coincidir("DELIMITER")           # consume ';'
        return NodoEntrada(keyword, formato, variable)

    def llamadaFuncion(self):
        argumentos = []
        # Reglas para argumentos: IDENTIFIER|NUMBER (, IDENTIFIER|NUMBER)*
        while self.obtener_token() and self.obtener_token()[1] != ')':
            token = self.obtener_token()
            if token[0] == "NUMBER":
                argumento = NodoNumero(self.coincidir("NUMBER"))
            elif token[0] == "IDENTIFIER":
                argumento = NodoIdent(self.coincidir("IDENTIFIER"))
            else:
                raise SyntaxError(f"Error de sintaxis, se esperaba un IDENTIFICADOR|NUMERO pero se encontró: {token}")
            argumentos.append(argumento)
            if self.obtener_token() and self.obtener_token()[1] == ",":
                self.coincidir("DELIMITER") # Se espera una coma
            else:
                break
        return argumentos





import json

def imprimir_ast(nodo):
    if isinstance(nodo, NodoPrograma):
      return { 
          "programa" : "Noname",
          "funciones" : [imprimir_ast(f) for f in nodo.funciones],
          "main" : imprimir_ast(nodo.main) 
      }
    elif(isinstance(nodo, NodoFuncion)):
        return{
            "nombre" : nodo.nombre[1],
            "parametros" : [imprimir_ast(p) for p in nodo.parametros],
            "cuerpo" : [imprimir_ast(c) for c in nodo.cuerpo]
        }
    elif(isinstance(nodo, NodoParametro)):
      return {
          "id" : nodo.nombre[1],
          "tipo" : nodo.tipo[1]
      }
    elif(isinstance(nodo, NodoAsignacion)):
            # NodoAsignacion en este proyecto tiene 'nombre' y 'expresion'
            return {
                    "asignacion_a": nodo.nombre[1],
                    "valor": imprimir_ast(nodo.expresion)
            }
    elif isinstance(nodo, NodoOperacion):
      return {"Operacion" : nodo.operador,
              "Izquierda" : imprimir_ast(nodo.izquierda),
              "Derecha" : imprimir_ast(nodo.derecha)}
    elif isinstance(nodo, NodoRetorno):
      return {
          "tipo" : "return",
          "valor" : imprimir_ast(nodo.expresion)
      }
    elif isinstance(nodo, NodoImprimir):
      return {
          "imprimir" : nodo.tipo[1],
          "argumentos" : [imprimir_ast(arg) for arg in nodo.argumentos]
      }
    elif isinstance(nodo, NodoIdent):
      return nodo.nombre[1]
    elif isinstance(nodo, NodoNumero):
      return int(nodo.valor[1]) if nodo.valor[1].isdigit() else nodo.valor[1]
    elif isinstance(nodo, NodoString):
      return nodo.argumentos[1]
    return {}