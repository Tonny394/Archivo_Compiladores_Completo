#Analisis semantico
class AnalisisSemantico:

    def __init__(self):
        self.tabla_simbolos = {}

    def analizar(self, nodo):
        metodo = f'analizar_{type(nodo).__name__}'
        if hasattr(self, metodo):
            method = getattr(self, metodo)(nodo)
            return method
        else:
            raise Exception(f'No se ha implementado el método {metodo} para el nodo {type(nodo).__name__}')
    
    def analizar_NodoFuncion(self, nodo):
        if nodo.nombre[1] in self.tabla_simbolos:
            raise Exception(f'Error semántico: La función {nodo.nombre[1]} ya está definida')
        self.tabla_simbolos[nodo.nombre[1]] = {'Tipo': nodo.tipo[1], 'Parametros': nodo.parametros}
        for param in nodo.parametros:
            self.tabla_simbolos[param.nombre[1]] = {'Tipo': param.tipo[1]}
        for instruccion in nodo.cuerpo:
            self.analizar(instruccion)

    def analizar_NodoAsignacion(self, nodo):
        tipo_expresion = self.analizar(nodo.expresion)
        self.tabla_simbolos[nodo.nombre[1]] = {'Tipo': tipo_expresion}

    def analizar_NodoOperacion (self, nodo):
        tipo_izquierda = self.analizar(nodo.izquierda)
        tipo_derecha = self.analizar(nodo.derecha)
        
        # Permitir operaciones entre int y float (resultado es float)
        if (tipo_izquierda == 'int' and tipo_derecha == 'float') or (tipo_izquierda == 'float' and tipo_derecha == 'int'):
            return 'float'
        elif tipo_izquierda != tipo_derecha:
            raise Exception(f'Error semántico: Tipos incompatibles en la operación {nodo.operador}')
        return tipo_izquierda
        
    def analizar_NodoPrograma(self, nodo):
        for funcion in nodo.funciones:
            self.analizar(funcion)
        self.analizar(nodo.main)
    
    def analizar_NodoNumero(self, nodo):
        return 'int' if '.' not in str(nodo.valor[1]) else 'float'
    
    def analizar_NodoIdent(self, nodo):
        if nodo.nombre[1] not in self.tabla_simbolos:
            raise Exception(f'Error semántico: Variable {nodo.nombre[1]} no definida')
        return self.tabla_simbolos[nodo.nombre[1]]['Tipo']
    
    def analizar_NodoRetorno(self, nodo):
        return self.analizar(nodo.expresion)
    
    def analizar_NodoString(self, nodo):
        return 'string'
    
    def analizar_NodoPrint(self, nodo):
        self.analizar(nodo.expresion)
    
    def analizar_NodoPrintln(self, nodo):
        self.analizar(nodo.expresion)
    
    def analizar_NodoIf(self, nodo):
        self.analizar(nodo.condicion)
        for instruccion in nodo.cuerpo_if:
            self.analizar(instruccion)
        if nodo.cuerpo_else:
            for instruccion in nodo.cuerpo_else:
                self.analizar(instruccion)
    
    def analizar_NodoWhile(self, nodo):
        self.analizar(nodo.condicion)
        for instruccion in nodo.cuerpo:
            self.analizar(instruccion)
    
    def analizar_NodoFor(self, nodo):
        self.analizar(nodo.init)
        self.analizar(nodo.cond)
        self.analizar(nodo.incr)
        for instruccion in nodo.cuerpo:
            self.analizar(instruccion)
    
    def analizar_NodoInstruccion(self, nodo):
        # Para instrucciones como cout
        for arg in nodo.argumentos_instruccion:
            self.analizar(arg)
    