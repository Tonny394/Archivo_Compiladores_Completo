import re
import pandas as pd 
from PyPDF2 import PdfReader

#rutaAcceso = "C:\\ProyectosVS\\BusquedaPython\\Analisis Anual 2018 ETAS.pdf"
#archivo = PdfReader(rutaAcceso)

#datosPagina = archivo.pages[4]
#print("HolaS")
#print(repr(datosPagina.extract_text()))

#patron = r"\n(\d+\s\d+)\s(\p{L}+\s*\p{L}+\s*(\p{L}*,*\n*\s*)*)\d*(-\s\d*)*"
#datos = re.findall(patron, datosPagina)
#print(datos)

#etas = pd.DataFrame(datos, columns=["NO.", "SE", "Area de Salud", "ETA Reportada", "Fuentes de Codigo", "NO. de Casos"])

#etas = etas.astype({"Casos 2018" : "Int64"})

def Tokenizar(texto):
    tokens = []
    keywords = re.compile(r"\b(if|else|while|then)\b")
    identifier = re.compile(r"[a-zA-Z][a-zA-Z0-9]*")
    numbers = re.compile(r"\d+")
    operators = re.compile(r"[\+\-\*\/]")
    delimiter = re.compile(r"[()]|;")

    #Recorrer palabra por palabra y asignar tipo
    for word in texto.split():
        if keywords.match(word):
            tokens.append(("keyword", word))
        elif identifier.match(word):
            tokens.append(("identifier", word))
        elif numbers.match(word):
            tokens.append(("number", word))
        elif operators.match(word):
            tokens.append(("operator", word))
        elif delimiter.match(word):
            tokens.append(("delimiter", word))
        else:
            print("Unknown token " + word)
    return tokens

texto = "if x > 5 then (y = y + 1 ; else z = z -)"
token = Tokenizar(texto)
print(token)

table = pd.DataFrame(token, columns=["Type", "Value"])

table["Value"].unique()

resumen = pd.DataFrame(table["Type"].value_counts())

identifierFound = table[table["Type"] == "identifier"]["Value"].unique()
keyworFound = table[table["Type"] == "keyword"]["Value"].unique()
numberFound = table[table["Type"] == "number"]["Value"].unique()
operatorFound = table[table["Type"] == "operator"]["Value"].unique()
delimiterFound = table[table["Type"] == "delimiter"]["Value"].unique()

resumen["Found"] = [keyworFound, identifierFound, numberFound, delimiterFound, operatorFound]
resumen

table[table["Type"] == "identifier"]["Value"].to_list()

#Implementar analizar de los tokens
def Parse(tokens):
    #Función auxiliar para consumir cada token 
    def Consume(tipoEsperado):
        global tokenActual
        if tokenActual[0] == tipoEsperado:
            global indiceToken 
            tokenActual = token[indiceToken]
            indiceToken +=1
        else:
            raise Exception(f"Se esperaba {tipoEsperado}, pero se encontró un dato tipo {tokenActual}")
        
    #Reglas de producción como funciones
    def E():
        #Implementar la regla de producción de expresiones
        T()
        while tokenActual[0] in ["+", "-"]:
            operador = tokenActual[1]
            Consume("Operador")
            T()
    
    #Regla de consturccion de terminos
    def T():
        F()
        while tokenActual[0] in ["*", "/"]:
            operador = tokenActual[1]
            Consume("Operador")
            F()

    #Implementación de la regla de producción de factores
    def F():
        if tokenActual == "Identificador" :
            Consume("Identificador")
        elif tokenActual == "Number":
            Consume("Numero")

    #Inicialización  de variables 
    global tokenActual, indiceToken
    tokenActual = token[0]
    indiceToken[1]

    #Iniciar el analisis
    E()

    #Si se consumieron todos los tokens, el analisis fue exitoso 
    if indiceToken == len(token):
        return True
    else:
        raise Exception("Error de sintaxis")