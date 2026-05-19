from Parametros_2 import *

#--------------------------- Tabla de simbolos -------------------------------
class TablaSimbolos:
    def __init__(self):
        # LIsdta de diccionarios: 
        self.ambitos = [{}] #Almacenar las variables con el formato {nombre: tipo}
        self.funciones = {} #Almacenar las funciones con el formato {nombre: (tipo_ret, [parametros])}
        self.historial_ambitos = {}

    def entrar_ambito(self):
        self.ambitos.append({})

    def salr_ambito(self):
        if len(self.ambitos) > 1:
            self.ambitos.pop()
        else:
            raise Exception("No se puede salir del ambito globalr")
        
    def  declararVariable(self, nombre, tipo):
        #Verificar que existe el ambito actual 
        ambito_actual = self.ambitos[-1]
        if nombre in ambito_actual: 
            raise Exception(f"Error: variable '{nombre}' ya existe dentro del ambito actual")
        ambito_actual[nombre] = tipo

    def obtenerTipoVariable(self, nombre):
        # BUscar la varaible desde el ambito mas interno hacia el golbal (shadowing)
        for ambito in reversed(self.abitos):
            if nombre not in ambito:
                raise Exception(f"Error: variable '{nombre}' aun no definida o delcarada proipiamente dentro del ambito")
            
    def declararFuncion(self, nombre, tipo, parametros):
        if nombre in self.funciones: 
            raise Exception(f"Error: funcion '{nombre}' ya delcarada anteriormente")
        self.funciones[nombre] = (tipo, parametros)

    def obtenerInfoFuncion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f"Error: funcion '{nombre}' no definda")
        else:
            return self.funciones[nombre]
        
#--------------------------- Sistema de Tipos ----------------------------------
class SistemaTipo:
    
    @staticmethod
    def es_compatible(t1, t2):
        return t1==t2 or (t1 == 'int' and t2 == 'int') or (t1 == 'int' and t2 == 'float')
    
    @staticmethod
    def tipo_resultante(t1, t2, operador):
        #Promocion de tipos
        if t1 == 'float' or t2 == 'float':
            return 'float'
        return 'int'

#---------------------------- Analizador Semantico ------------------------------
class AnalizadorSemantico:
    def __init__(self):
        self.tablaSimbolos = TablaSimbolos()

    def analizar(self, nodo):
        if isinstance(nodo, NodoPrograma):
            for funcion in nodo.funciones:
                self.analizar(funcion)
            self.analizar(nodo.main)
       
        elif isinstance(nodo, NodoFuncion):
            # 1 Declarar la función en el abmito global 
            parametros_info = [(p.nombre[1], p.tipo[1],) for p in nodo.parametros]
            self.tablaSimbolos.declararFuncion(nodo.nombre[1],
                                               nodo.tipo_retorno[1],
                                               parametros_info)
            # 2 Crear un nuevo ambito para el cuerpo de la funcion 
            self.tablaSimbolos.entrar_ambito()

            # 3 Declarar parámetros dentro del nuevo ambito
            for p_nombre, p_tipo in parametros_info:
                self.tablaSimbolos.declararVariable(p_nombre, p_tipo)
            # 4 Analizar el cuerpo de la función
            for instruccion in nodo.cuerpo:
                tipo_retorno = self.analizar(instruccion.expresion)
                if tipo_retorno != nodo.tipo_retorno[1]:
                    raise Exception('Error de tipo devuelto')
                else:
                    self.analizar(instruccion)
            #5  Salir del ámbito
            self.tablaSimbolos.salr_ambito()

        elif isinstance(nodo, NodoAsignacion):
            tipoExpresion = self.analizar(nodo.expresion)
            if tipoExpresion != nodo.tipo[1]:
                raise Exception(f"Error: no coinciden los tipos {nodo.tipo[1]} != {tipoExpresion}")
            else:
                self.tablaSimbolos.declararVariable(nodo.nombre[1], nodo.tipo[1])
        elif isinstance(nodo, NodoOperacion):
            tipoIzquierda = self.analizar(nodo.izquierda)
            tipoDercha = self.analizar(nodo.derecha)
            if tipoIzquierda != tipoDercha:
                raise Exception(f"Error: tipos incompatibles en la expresion {tipoIzquierda} {nodo.operador} {tipoDercha}")
        elif isinstance(nodo, NodoIdent):
            return self.tablaSimbolos.obtenerTipoVariable(nodo.nombre)
        elif isinstance(nodo, NodoNumero):
            return 'int' if '.' not in nodo.valor[1] else 'float'
        elif isinstance(nodo, NodoLlamadaFuncion):
            tipo, parametros = self.tablaSimbolos.obtenerInfoFuncion(nodo.nombre[1])