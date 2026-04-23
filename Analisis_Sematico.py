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
    
    def vistar_NodoFuncion(self, nodo):
        if nodo.nombre in self.tabla_simbolos:
            raise Exception(f'Error semántico: La función {nodo.nombre} ya está definida')
        self.tabla_simbolos[nodo.nombre[1]] = {'Tipo': nodo.parametros[0].tipo[1], 'Parametros': nodo.parametros}
        for param in nodo.parametros:
            self.tabla_simbolos[param.nombre[1]] = {'Tipo': param.tipo[1]}
        for instruccion in nodo.cuerpo:
            self.analizar(instruccion)

    def visitar_NodoAsignacion(self, nodo):
        tipo_expresion = self.analizar(nodo.expresion)
        self.tabla_simbolos[nodo.nombre[1]] = {'Tipo': tipo_expresion}

    def visitar_NodoOperacion (self, nodo):
        tipo_izquierda = self.analizar(nodo.izquierda)
        tipo_derecha = self.analizar(nodo.derecha)
        if tipo_izquierda != tipo_derecha:
            raise Exception(f'Error semántico: Tipos incompatibles en la operación {nodo.operador}')
        return tipo_izquierda
        
    def visitar_NodoPrograma(self, nodo):
        for funcion in nodo.funciones:
            self.analizar(funcion)
        self.analizar(nodo.main)
    
    def visitar_NodoNumero(self, nodo):
        return 'int' if '.' not in nodo.valor else 'float'
    
    def visitar_NodoIndentificador(self, nodo):
        if nodo.nombre[1] not in self.tabla_simbolos:
            raise Exception(f'Error semántico: Variable {nodo.nombre[1]} no definida')
        return self.tabla_simbolos[nodo.nombre[1]]['Tipo']
    
    def visitar_NodoRetorno(self, nodo):
        return self.analizar(nodo.expresion)
    