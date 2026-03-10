class NodoAST:
    #Clase de los nodos del Arbol de sintaxis trivial
    pass

def traducirPy(self):
  #Traducción de C a Python
  raise NotImplementedError("Método traducirPy() no implementado en este Nodo")
def generarCodigo():
  #Traducción de c++ a Assembler
  raise NotImplementedError("Método generarCodigo() no implementado en este Nodo")

class NodoFuncion(NodoAST):
    #Nodo que representa la funcion
    def __init__(self, tipo, nombre, parametros, cuerpo):
      self.tipo = tipo
      self.nombre = nombre
      self.parametros = parametros
      self.cuerpo = cuerpo

    def traducirPy(self):
      params = ", ".join(p.traducirPy() for p in self.parametros)
      cuerpo = "\n  ".join(c.traducirPy() for c in self.cuerpo)
      return f"def {self.nombre[1]}({params}):\n  {cuerpo}"

    def traducirRuby(self):
      params = ", ".join(p.traducirPy() for p in self.parametros)
      cuerpo = "\n  ".join(c.traducirPy() for c in self.cuerpo)
      return f"def {self.nombre[1]}({params})\n  {cuerpo}"

class NodoParametro(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

    def traducirPy(self):
      return self.nombre[1]
    def traducirRuby(self):
      return self.nombre[1]

class NodoAsignacion(NodoAST):
    #Nodo que representa la asignacion
    def __init__(self, tipo, nombre, expresion):
        self.tipo = tipo
        self.nombre = nombre
        self.expresion = expresion

    def traducirPy(self):
      return f"{self.nombre[1]} = {self.expresion.traducirPy()}"
    def traducirRuby(self):
      return f"{self.nombre[1]} = {self.expresion.traducirPy()}"

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.derecha = derecha
        self.operador = operador

    def traducirPy(self):
      # operador es una tupla, no un nodo, y corregimos Derecha a derecha
      return f"{self.izquierda.traducirPy()} {self.operador[1]} {self.derecha.traducirPy()}"

class NodoRetorno(NodoAST):
    #Nodo para representar el retorno
    def __init__(self, expresion ):
        self.expresion = expresion

    def traducirPy(self):
      return f"return {self.expresion.traducirPy()}"

class NodoIdent(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre
    def traducirPy(self):
      return self.nombre[1]

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor
    def traducirPy(self):
        return self.valor[1]
    
class NodoPrograma(NodoAST):
   def __init__(self, funciones, main):
        
        self.funciones = funciones
        self.main = main

class NodoLlamadaFuncion():
  def __init__(self, nombref, argumentos):
    self.nombre_funcion = nombref
    self.argumentos = argumentos
  def traducirPy(self):
    args = ", ".join(a.traducirPy() for a in self.argumentos)
    return f"{self.nombre_funcion}({args})"
  
class NodoPrint(NodoAST):
  def __init__(self, expresion):
    self.expresion = expresion
  def traducirPy(self):
    return f"print({self.expresion.traducirPy()})"