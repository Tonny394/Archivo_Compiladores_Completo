class NodoAST:
    #Clase de los nodos del Arbol de sintaxis trivial
    def traducirPy(self):
    #Traducción de C a Python
        raise NotImplementedError("Método traducirPy() no implementado en este Nodo")
    def traducirRuby(self):
        raise NotImplementedError("Metodo traducirRuby() no implementado en este Nodo")
    def generarCodigo():
    #Traducción de c++ a Assembler
        raise NotImplementedError("Método generarCodigo() no implementado en este Nodo")

class NodoPrograma(NodoAST):
    def __init__(self, funciones, main):
       self.variables = []
       self.funciones = funciones
       self.main = main

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
      params = ", ".join(p.traducirRuby() for p in self.parametros)
      cuerpo = "\n  ".join(c.traducirRuby() for c in self.cuerpo)
      return f"def {self.nombre[1]}({params})\n  {cuerpo} \nend"

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
      return f"{self.nombre[1]} = {self.expresion.traducirRuby()}"

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.derecha = derecha
        self.operador = operador

    def traducirPy(self):
      return f"{self.izquierda.traducirPy()} {self.operador[1]} {self.derecha.traducirPy()}"
    def traducirRuby(self):
      return f"{self.izquierda.traducirRuby()} {self.operador[1]} {self.derecha.traducirRuby()}"

class NodoRetorno(NodoAST):
    #Nodo para representar el retorno
    def __init__(self, expresion ):
        self.expresion = expresion

    def traducirPy(self):
      return f"return {self.expresion.traducirPy()}"
    def traducirRuby(self):
      return f"return {self.expresion.traducirRuby()}"

class NodoIdent(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre
    def traducirPy(self):
      return self.nombre[1]
    def traducirRuby(self):
      return self.nombre[1]

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor
    def traducirPy(self):
        return self.valor[1]
    def traducirRuby(self):
       return self.valor[1]
    
class NodoInstruccion(NodoAST):
    def __init__(self, tipo, argumentos):
        self.tipo_instruccion = tipo
        self.argumentos_instruccion = argumentos

    def traducirPy(self):
        if self.tipo_instruccion[1] == 'cout':
            args = ", ".join(a.traducirPy() for a in self.argumentos_instruccion)
            return f"print({args})"
        return ""
    def traducirRuby(self):
        if self.tipo_instruccion[1] == 'cout':
            args = ", ".join(a.traducirRuby() for a in self.argumentos_instruccion)
            return f"puts \"{args}\""
        return ""
       

class NodoLlamadaFuncion():
  def __init__(self, nombref, argumentos):
    self.nombre_funcion = nombref
    self.argumentos = argumentos
  def traducirPy(self):
    args = ", ".join(a.traducirPy() for a in self.argumentos)
    return f"{self.nombre_funcion}({args})"
  def traducirRuby(self):
    args = ", ".join(a.traducirRuby() for a in self.argumentos)
    return f"{self.nombre_funcion}({args})"

class NodoString(NodoAST):
    def __init__(self, valor):
        self.valor = valor
    def traducirPy(self):
        return self.valor[1]
    def traducirRuby(self):
        return self.valor[1]

class NodoIf(NodoAST):
    def __init__(self, condicion, cuerpo_if, cuerpo_else=None):
        self.condicion = condicion
        self.cuerpo_if = cuerpo_if
        self.cuerpo_else = cuerpo_else

    def traducirPy(self):
        if_part = f"if {self.condicion.traducirPy()}:\n" + "\n".join(f"    {c.traducirPy()}" for c in self.cuerpo_if)
        if self.cuerpo_else:
            else_part = "\nelse:\n" + "\n".join(f"    {c.traducirPy()}" for c in self.cuerpo_else)
            return if_part + else_part
        return if_part

    def traducirRuby(self):
        if_part = f"if {self.condicion.traducirRuby()}\n" + "\n".join(f"    {c.traducirRuby()}" for c in self.cuerpo_if)
        if self.cuerpo_else:
            if_part += "\nelse\n" + "\n".join(f"    {c.traducirRuby()}" for c in self.cuerpo_else)
        if_part += "\nend"
        return if_part

class NodoWhile(NodoAST):
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo

    def traducirPy(self):
        return f"while {self.condicion.traducirPy()}:\n" + "\n".join(f"    {c.traducirPy()}" for c in self.cuerpo)

    def traducirRuby(self):
        return f"while {self.condicion.traducirRuby()}\n" + "\n".join(f"    {c.traducirRuby()}" for c in self.cuerpo) + "\nend"

class NodoFor(NodoAST):
    def __init__(self, init, cond, incr, cuerpo):
        self.init = init
        self.cond = cond
        self.incr = incr
        self.cuerpo = cuerpo

    def traducirPy(self):
        init_py = self.init.traducirPy() if self.init else ""
        cond_py = self.cond.traducirPy()
        incr_py = self.incr.traducirPy() if self.incr else ""
        cuerpo_py = "\n".join(f"    {c.traducirPy()}" for c in self.cuerpo)
        return f"{init_py}\nwhile {cond_py}:\n{cuerpo_py}\n    {incr_py}"

    def traducirRuby(self):
        init_py = self.init.traducirRuby() if self.init else ""
        cond_py = self.cond.traducirRuby()
        incr_py = self.incr.traducirRuby() if self.incr else ""
        cuerpo_py = "\n".join(f"    {c.traducirRuby()}" for c in self.cuerpo)
        return f"{init_py}\nwhile {cond_py}\n{cuerpo_py}\n    {incr_py}\nend"

class NodoPrint(NodoAST):
    def __init__(self, expresion, newline=False):
        self.expresion = expresion
        self.newline = newline

    def traducirPy(self):
        if self.newline:
            return f"print({self.expresion.traducirPy()})"
        else:
            return f"print({self.expresion.traducirPy()}, end='')"

    def traducirRuby(self):
        if self.newline:
            return f"puts {self.expresion.traducirRuby()}"
        else:
            return f"print {self.expresion.traducirRuby()}"