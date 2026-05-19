class NodoAST:
    #Clase de los nodos del Arbol de sintaxis trivial
    def traducirPy(self):
    #Traducción de C a Python
        raise NotImplementedError("Método traducirPy() no implementado en este Nodo")
    def traducirRuby(self):
        raise NotImplementedError("Metodo traducirRuby() no implementado en este Nodo")
    def generarCodigo(self):
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
    
    def optimizar(self):
        if isinstance(self.izquierda, NodoOperacion):
            self.izquierda.optimizar()
        else:
            izquierda = self.izquierda

        if isinstance(self.derecha, NodoOperacion):
            self.derecha.optimizar()
        else:
            derecha = self.derecha

        #Si ambos nodos son números evaluamos la operación
        if isinstance(izquierda, NodoNumero) and isinstance(derecha, NodoNumero):
            izq = int(izquierda.valor[1])
            der = der(derecha.valor[1])
            if self.operador[1] == "+":
               valor = izq + der
            elif self.operador == "-":
                valor = izq - der
            elif self.operador == "*":
                valor = izq * der 
            elif self.operador == "/":
                if der != 0:
                    valor = izq / der
                else:
                    raise Exception ("Error: Es matematicamente imposible dividir un numero entre 0") 
            return NodoNumero(('NUMBER', str(valor))) 

        #Simplificacion algebraica
        if isinstance(derecha, NodoNumero) and int(derecha.valor[1]) == "1" and self.operador[1] == "*":
            return izquierda
        if isinstance(izquierda, NodoNumero) and int(izquierda.valor[1]) == "1" and self.operador[1] == "*":
            return derecha
        if isinstance(derecha, NodoNumero) and int(derecha.valor[1]) == "0" and self.operador[1] == "+":
            return izquierda
        if isinstance(izquierda, NodoNumero) and int(izquierda.valor[1]) == "0" and self.operador[1] == "+":
            return derecha
        if isinstance(derecha, NodoNumero) and int(derecha.valor[1]) == "0" and self.operador[1] == "/":
            raise Exception("Error: Es matematicamente imposible dividir un numero entre 0")
        if izquierda.valor[1] == derecha.valor[1] and self.operador[1] == "/":
            return 1
        
        # SI no se puede optimizar mas se devuelve la expresion 
        return NodoOperacion(izquierda, self.operador[1], derecha)
    
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
    
class NodoString(NodoAST):
    def __init__(self, argumentos):
        self.argumentos = argumentos

    def traducirPy(self):
       return self.argumentos[1]
    
    def traducirRuby(self):
       return self.argumentos[1]
    
    def generarCodigo(self):
       raise NotImplementedError("Strings en ensamblador aun no implementado")
    
class NodoCondicional(NodoAST):
    def __init__(self, condicion, cuerpo_if, cuerpo_else):
        self.condicion = condicion
        self.cuerpo_if = cuerpo_if
        self.cuerpo_else = cuerpo_else  # puede ser [] si no hay else

    def traducirPy(self):
        condicion = self.condicion.traducirPy()
        cuerpo_if = "\n    ".join(c.traducirPy() for c in self.cuerpo_if)
        resultado = f"if {condicion}:\n    {cuerpo_if}"
        if self.cuerpo_else:
            cuerpo_else = "\n    ".join(c.traducirPy() for c in self.cuerpo_else)
            resultado += f"\nelse:\n    {cuerpo_else}"
        return resultado

    def traducirRuby(self):
        condicion = self.condicion.traducirRuby()
        cuerpo_if = "\n    ".join(c.traducirRuby() for c in self.cuerpo_if)
        resultado = f"if {condicion}\n    {cuerpo_if}"
        if self.cuerpo_else:
            cuerpo_else = "\n    ".join(c.traducirRuby() for c in self.cuerpo_else)
            resultado += f"\nelse\n    {cuerpo_else}"
        resultado += "\nend"
        return resultado
    
class NodoImprimir(NodoAST):
    def __init__(self, tipo, argumentos):
        self.tipo = tipo          # el token 'printf' o 'puts'
        self.argumentos = argumentos  # lista de nodos

    def traducirPy(self):
        args = ", ".join(a.traducirPy() for a in self.argumentos)
        return f"print({args})"

    def traducirRuby(self):
        args = " ".join(a.traducirRuby() for a in self.argumentos)
        return f"puts {args}"
 
    
class NodoWhile(NodoAST):
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo

    def traducirPy(self):
        condicion = self.condicion.traducirPy()
        cuerpo = "\n    ".join(c.traducirPy() for c in self.cuerpo)
        return f"while {condicion}:\n    {cuerpo}"

    def traducirRuby(self):
        condicion = self.condicion.traducirRuby()
        cuerpo = "\n    ".join(c.traducirRuby() for c in self.cuerpo)
        return f"while {condicion}\n    {cuerpo}\nend"

class NodoFor(NodoAST):
    def __init__(self, inicio, condicion, incremento, cuerpo):
        self.inicio = inicio
        self.condicion = condicion
        self.incremento = incremento
        self.cuerpo = cuerpo

    def traducirPy(self):
        # En Python no hay for estilo C, se convierte a while
        inicio = self.inicio.traducirPy()
        condicion = self.condicion.traducirPy()
        incremento = self.incremento.traducirPy()
        cuerpo = "\n    ".join(c.traducirPy() for c in self.cuerpo)
        return f"{inicio}\nwhile {condicion}:\n    {cuerpo}\n    {incremento}"

    def traducirRuby(self):
        inicio = self.inicio.traducirRuby()
        condicion = self.condicion.traducirRuby()
        incremento = self.incremento.traducirRuby()
        cuerpo = "\n    ".join(c.traducirRuby() for c in self.cuerpo)
        return f"{inicio}\nwhile {condicion}\n    {cuerpo}\n    {incremento}\nend"

class NodoIncremento(NodoAST):
    def __init__(self, nombre, operador):
        self.nombre = nombre
        self.operador = operador

    def traducirPy(self):
        # i++ -> i += 1  |  i-- -> i -= 1
        if self.operador[1] == '++':
            return f"{self.nombre[1]} += 1"
        elif self.operador[1] == '--':
            return f"{self.nombre[1]} -= 1"

    def traducirRuby(self):
        if self.operador[1] == '++':
            return f"{self.nombre[1]} += 1"
        elif self.operador[1] == '--':
            return f"{self.nombre[1]} -= 1"

class NodoEntrada(NodoAST):
    def __init__(self, tipo, formato, variable):
        self.tipo = tipo
        self.formato = formato
        self.variable = variable

    def traducirPy(self):
        # scanf("%d", &x) -> x = int(input())
        return f"{self.variable[1]} = int(input())"

    def traducirRuby(self):
        # scanf("%d", &x) -> x = gets.chomp.to_i
        return f"{self.variable[1]} = gets.chomp.to_i"   

class NodoLlamadaFuncion():
  def __init__(self, nombref, argumentos):
    self.nombre_funcion = nombref
    self.argumentos = argumentos
  def traducirPy(self):
    args = ", ".join(a.traducirPy() for a in self.argumentos)
    return f"{self.nombre_funcion}({args})"
  
  def generarCodigo(self):
      codigo = []
      for arg in reversed(self.argumentos): #Apilamos argumentos en orden inverso
          codigo.append(arg.generarCodigo())
          codigo.append("   push  eax   ;pasar argumento a la pila ")

          codigo.append(f"   call {self.nombre_funcion} ;Llamar a la funcion {self.nombre_funcion}")
          codigo.append(f"   add eps, {len(self.argumentos) * 4} ; Limpiar pila de argumnetos")
          return "\n".join(codigo)