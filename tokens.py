from Parametros import *
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
        tipo_retorno = self.coincidir('KEYWORD') # Retorna int
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
        return NodoFuncion(tipo_retorno, nombre_funcion, parametros, cuerpo)

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
            if self.obtener_token()[1] == 'return':
                instrucciones.append(self.retorno())
            elif self.obtener_token()[1] == 'cout':
                instrucciones.append(self.impresionPantalla())
            elif self.obtener_token()[1] == 'if':
                instrucciones.append(self.if_statement())
            elif self.obtener_token()[1] == 'while':
                instrucciones.append(self.while_statement())
            elif self.obtener_token()[1] == 'for':
                instrucciones.append(self.for_statement())
            elif self.obtener_token()[1] in ['print', 'println']:
                instrucciones.append(self.print_statement())
            else:
                # Verificar si es una asignación con tipo o sin tipo
                if self.obtener_token() and self.obtener_token()[0] == 'KEYWORD':
                    # Es una asignación con tipo (int i = 0;)
                    instrucciones.append(self.asignacion())
                else:
                    # Es una asignación sin tipo (i = i + 1;)
                    instrucciones.append(self.expresion_asignacion())
        return instrucciones

    def asignacion(self):
        #Gramática pra la estructura de asignación
        tipo = self.coincidir('KEYWORD') #Se espera un tipo
        nombre = self.coincidir('IDENTIFIER')
        operador = self.coincidir('OPERATOR') #Se espera un operador =
        expresion = self.expresion()
        self.coincidir('DELIMITER')
        return NodoAsignacion(tipo, nombre, expresion)

    def retorno(self):
        self.coincidir('KEYWORD')
        expresion = self.expresion()
        self.coincidir('DELIMITER')
        return NodoRetorno(expresion)

    def expresion(self):
        izquierda = self.termino()
        while self.obtener_token() and self.obtener_token()[0] == "OPERATOR" and self.obtener_token()[1] in ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=']:
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
        keyword = self.coincidir("KEYWORD")  # cout
        self.coincidir("OPERATOR")           # <<
        expresion = self.expresion()
        self.coincidir("DELIMITER")          # ;
        return NodoInstruccion(keyword, [expresion])


    def llamadaFuncion(self):
        argumentos = []
        # Reglas para argumentos: (,IDENTIFIER | NUMBER)*
        sigue = True
        token = self.obtener_token()
        while sigue:
            sigue = False
            if token[0] == "NUMBER":
                argumento = NodoNumero(self.coincidir("NUMBER"))
            elif token[0] == "IDENTIFIER":
                argumento = NodoIdent(self.coincidir("IDENTIFIER"))
            else:
                raise SyntaxError(f"Error de sintaxis, se esperaba un IDENTIFICADOR|NUMERO pero se encontró: {token}")
            argumentos.append(argumento)
            if self.obtener_token() and self.obtener_token()[1] == ",":
                self.coincidir("DELIMITER") # Se espera una coma
                token = self.obtener_token()
                sigue = True
            return argumentos

    def expresion_asignacion(self):
        nombre = self.coincidir('IDENTIFIER')
        operador = self.coincidir('OPERATOR')  # =
        expresion = self.expresion()
        self.coincidir('DELIMITER')  # ;
        return NodoAsignacion(None, nombre, expresion)
    
    def expresion_asignacion_for(self):
        """Expresión de asignación para el for (sin consumir ;)"""
        nombre = self.coincidir('IDENTIFIER')
        operador = self.coincidir('OPERATOR')  # =
        expresion = self.expresion()
        return NodoAsignacion(None, nombre, expresion)

    def if_statement(self):
        self.coincidir('KEYWORD')  # if
        self.coincidir('DELIMITER')  # (
        cond = self.expresion()
        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # {
        cuerpo_if = self.cuerpo()
        self.coincidir('DELIMITER')  # }
        cuerpo_else = None
        if self.obtener_token() and self.obtener_token()[1] == 'else':
            self.coincidir('KEYWORD')  # else
            self.coincidir('DELIMITER')  # {
            cuerpo_else = self.cuerpo()
            self.coincidir('DELIMITER')  # }
        return NodoIf(cond, cuerpo_if, cuerpo_else)

    def while_statement(self):
        self.coincidir('KEYWORD')  # while
        self.coincidir('DELIMITER')  # (
        cond = self.expresion()
        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # {
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER')  # }
        return NodoWhile(cond, cuerpo)

    def for_statement(self):
        self.coincidir('KEYWORD')  # for
        self.coincidir('DELIMITER')  # (
        init = self.expresion_asignacion_for()
        self.coincidir('DELIMITER')  # ;
        cond = self.expresion()
        self.coincidir('DELIMITER')  # ;
        incr = self.expresion_asignacion_for()
        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # {
        cuerpo = self.cuerpo()
        self.coincidir('DELIMITER')  # }
        return NodoFor(init, cond, incr, cuerpo)

    def print_statement(self):
        keyword = self.coincidir('KEYWORD')  # print or println
        self.coincidir('DELIMITER')  # (
        expr = self.expresion()
        self.coincidir('DELIMITER')  # )
        self.coincidir('DELIMITER')  # ;
        if keyword[1] == 'print':
            return NodoPrint(expr)
        else:
            return NodoPrintln(expr)





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
      if nodo.tipo:
          return {
              "tipo": "asignacion",
              "tipo_var": nodo.tipo[1],
              "nombre": nodo.nombre[1],
              "expresion": imprimir_ast(nodo.expresion)
          }
      else:
          return {
              "tipo": "asignacion",
              "nombre": nodo.nombre[1],
              "expresion": imprimir_ast(nodo.expresion)
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
    elif isinstance(nodo, NodoIdent):
      return nodo.nombre[1]
    elif isinstance(nodo, NodoNumero):
      valor_str = nodo.valor[1]
      if '.' in valor_str:
        return float(valor_str)
      elif valor_str.isdigit():
        return int(valor_str)
      else:
        return valor_str
    elif isinstance(nodo, NodoString):
      return nodo.valor[1]
    elif isinstance(nodo, NodoIf):
      return {
          "tipo": "if",
          "condicion": imprimir_ast(nodo.condicion),
          "cuerpo_if": [imprimir_ast(c) for c in nodo.cuerpo_if],
          "cuerpo_else": [imprimir_ast(c) for c in nodo.cuerpo_else] if nodo.cuerpo_else else None
      }
    elif isinstance(nodo, NodoWhile):
      return {
          "tipo": "while",
          "condicion": imprimir_ast(nodo.condicion),
          "cuerpo": [imprimir_ast(c) for c in nodo.cuerpo]
      }
    elif isinstance(nodo, NodoFor):
      return {
          "tipo": "for",
          "init": imprimir_ast(nodo.init),
          "cond": imprimir_ast(nodo.cond),
          "incr": imprimir_ast(nodo.incr),
          "cuerpo": [imprimir_ast(c) for c in nodo.cuerpo]
      }
    elif isinstance(nodo, NodoPrint):
      return {
          "tipo": "print" if not nodo.newline else "println",
          "expresion": imprimir_ast(nodo.expresion)
      }
    elif isinstance(nodo, NodoInstruccion):
      return {
          "tipo": nodo.tipo_instruccion[1],
          "argumentos": [imprimir_ast(arg) for arg in nodo.argumentos_instruccion]
      }
    elif isinstance(nodo, NodoLlamadaFuncion):
      return {
          "tipo": "llamada_funcion",
          "nombre": nodo.nombre_funcion,
          "argumentos": [imprimir_ast(arg) for arg in nodo.argumentos]
      }
    return {}