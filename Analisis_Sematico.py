class AnalizadorSemantico:
    def __init__(self):
        self.tablaSimbolos = {}

    def analizar(self, nodo):
        metodo = f"visistar_{type(nodo).__name__}"
        if hasattr(self, metodo):
            method = getattr(self, metodo)(nodo)
            return method
        else:
            raise Exception(f"No se ha implementado el analisis semantico para {type(nodo).__name__}")
    
    def visitar_NodoFuncion(self, nodo):
        if nodo.nombre[1] in self.tablaSimbolos:
            raise Exception(f"Error semantico: la funcion {nodo.nombre[1]} ya esta definida")
        self.tablaSimbolos[nodo.nombre[1]] = {"tipo": nodo.parametros[0].tipo[1], "parametro": nodo.parametros}

        for param in nodo.parametros:
            self.tablaSimbolos[param.nombre[1]] = {"tipo": param.tipo[1]}
        
        for instruccion in nodo.cuerpo:
            self.analizar(instruccion)

    def visitar_NodoAsignacion(self, nodo):
        tipo_exresion = self.analizar(nodo.expresion)
        self.tablaSimbolos[nodo.nombre[1]] = {"tipo": tipo_exresion}

    def visitar_NodoOperacion(self, nodo):
        tipo_izquierda = self.analizar(nodo.izquierda)
        tipo_derecha = self.analizar(nodo.derecha)

        if tipo_izquierda != tipo_derecha:
            raise Exception(f"Error semantico: Operacion entre tipos incompatibles ({tipo_izquierda} y ({tipo_derecha}))")
        else:
            return tipo_izquierda
        
    def visitar_NodoNumero(self, nodo):
        return "int" if "." not in nodo.valor[1] else "float"
    
    def visitar_NodoIdentificador(self, nodo):
        if nodo.nombre[1] not in self.tablaSimbolos:
            raise Exception(f"Error semantico: La variable {nodo.nombre[1]} no esta definida")
        
        return self.tablaSimbolos[nodo.nombre[1]]["tipo"]
    
    def visitar_NodoRetorno(self, nodo):
        return self.analizar(nodo.expresion)
    
    def visitar_NodoPrograma(self, nodo):
        for funcion in nodo.funciones:
            self.analizar(funcion)
        self.analizar(nodo.main)

