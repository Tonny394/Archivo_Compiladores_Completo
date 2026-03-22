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

    def generarCodigo(self):
       codigo = ["Section .text", "global _start"]
       data = ["Section .bss"]
       for funcion in self.funciones: 
          codigo.append(funcion.generarCodigo())
          self.variables.append((funcion.cuerpo[0].tipo[1], funcion.cuerpo[0].nombre[1]))
          if len(funcion.parametros) > 0:
            for parametro in funcion.parametros:
                self.variables.append(parametro.tipo[1], parametro.nombre[1])
        
            #Genrar el punto de entrada del programa
            codigo.append("_statrt: ")
            codigo.append(self.main.generarCodigo())
            #Finalizar el programa 
            codigo.append("     mov eax, 1 ;syscall exit ")
            codigo.append("     xor ebx, ebx")
            codigo.append("     int 0x80")

            #Seccion de reserva de memoria para las variables
            for variable in self.variables:
                if variable[0] == "int":
                    data.append(f"  {variable[1]}:    resd 1")

            codigo = "\n".join(codigo)
            return "\n".join(data) + codigo     

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
    
    def generarCodigo(self):
        codigo = f"{self.nombre}: \n"
        if len(self.parametros) > 0: 
           # aqui se guarda en pila el registro ax a usar
           for parametro in self.parametros:
              codigo += "\n    pop     eax"
              codigo += f"\n    mov [{self.parametros[1]}], eax"
        
        codigo += "\n".join(c.generarCodigo() for c in self.cuerpo)
        codigo += "\n    ret"
        codigo += "\n"
        return codigo
              

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
    
    def generarCodigo(self):
        codigo = self.expresion.generarCodigo()
        codigo += f"\n    mov[{self.nombre[1]}, eax]"
        return codigo

class NodoOperacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.derecha = derecha
        self.operador = operador

    def traducirPy(self):
      return f"{self.izquierda.traducirPy()} {self.operador[1]} {self.derecha.traducirPy()}"
    def traducirRuby(self):
      return f"{self.izquierda.traducirRuby()} {self.operador[1]} {self.derecha.traducirRuby()}"
    
    def generarCodigo(self):
        coidigo = []
        coidigo.append(self.izquierda.generarCodigo())
        coidigo.append("   push     eax")
        coidigo.append(self.derecha.generarCodigo())
        coidigo.append("   mov   ebx, eax")
        coidigo.append("   pop   eax")
        if self.operador[1] == "+":
            coidigo.append("   add    eax, ebx")
        elif self.operador[1] == "-":
            coidigo.append("   sub   eax, ebx")
        elif self.operador[1] == "*":
            coidigo.append("   mul   eax, ebx")
        elif self.operador[1] == "/":
           coidigo.append("    div   eax, ebx")

        return "\n".join(coidigo)

class NodoRetorno(NodoAST):
    #Nodo para representar el retorno
    def __init__(self, expresion ):
        self.expresion = expresion

    def traducirPy(self):
      return f"return {self.expresion.traducirPy()}"
    def traducirRuby(self):
      return f"return {self.expresion.traducirRuby()}"
    
    def generarCodigo(self):
        return self.expresion.generarCodigo()

class NodoIdent(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre
    def traducirPy(self):
      return self.nombre[1]
    def traducirRuby(self):
      return self.nombre[1]
    
    def generarCodigo(self):
       return f"\n     mov   eax, {self.nombre[1]}"

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor
    def traducirPy(self):
        return self.valor[1]
    def traducirRuby(self):
       return self.valor[1]
    
    def generarCodigo(self):
       return f"\n     mov   eax, {self.valor[1]}"

    
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