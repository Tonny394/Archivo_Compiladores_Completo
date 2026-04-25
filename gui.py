import tkinter as tk
from tkinter import scrolledtext, messagebox
from compilador import identificarTokens
from tokens import Parse
from Parametros import *
import json

def imprimir_ast(nodo):
    if isinstance(nodo, NodoPrograma):
        return {
            "programa": "Noname",
            "funciones": [imprimir_ast(f) for f in nodo.funciones],
            "main": imprimir_ast(nodo.main)
        }
    elif isinstance(nodo, NodoFuncion):
        return {
            "nombre": nodo.nombre[1],
            "parametros": [imprimir_ast(p) for p in nodo.parametros],
            "cuerpo": [imprimir_ast(c) for c in nodo.cuerpo]
        }
    elif isinstance(nodo, NodoParametro):
        return {
            "id": nodo.nombre[1],
            "tipo": nodo.tipo[1]
        }
    elif isinstance(nodo, NodoAsignacion):
        return {
            "op": nodo.operador[1],
            "izq": imprimir_ast(nodo.nombre),
            "der": imprimir_ast(nodo.expresion)
        }
    elif isinstance(nodo, NodoOperacion):
        return {
            "Operacion": nodo.operador,
            "Izquierda": imprimir_ast(nodo.izquierda),
            "Derecha": imprimir_ast(nodo.derecha)
        }
    elif isinstance(nodo, NodoRetorno):
        return {
            "tipo": "return",
            "valor": imprimir_ast(nodo.expresion)
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
    elif isinstance(nodo, NodoInstruccion):
        return {
            "tipo": "cout",
            "argumentos": [imprimir_ast(a) for a in nodo.argumentos_instruccion]
        }
    return {}

class CompiladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador C++ a Python/Ruby/Assembler")
        self.root.geometry("1200x800")

        # Área de entrada de código
        tk.Label(root, text="Código Fuente:").pack(pady=5)
        self.code_input = scrolledtext.ScrolledText(root, width=100, height=10)
        self.code_input.pack(pady=5)
        self.code_input.insert(tk.END, '''int suma(int a, int b, int c){
    return a + b;
    cout << "1";
}

int main(){
    int hola = 3;
}''')

        # Botón para ejecutar
        self.run_button = tk.Button(root, text="Ejecutar Análisis", command=self.run_analysis)
        self.run_button.pack(pady=10)

        # Área de resultados
        results_frame = tk.Frame(root)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Tokens
        tk.Label(results_frame, text="Tokens Léxicos:").grid(row=0, column=0, sticky="nw")
        self.tokens_output = scrolledtext.ScrolledText(results_frame, width=40, height=15)
        self.tokens_output.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # AST
        tk.Label(results_frame, text="Árbol de Sintaxis Abstracta (AST):").grid(row=0, column=1, sticky="nw")
        self.ast_output = scrolledtext.ScrolledText(results_frame, width=40, height=15)
        self.ast_output.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # Python
        tk.Label(results_frame, text="Traducción a Python:").grid(row=2, column=0, sticky="nw")
        self.python_output = scrolledtext.ScrolledText(results_frame, width=40, height=10)
        self.python_output.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

        # Ruby
        tk.Label(results_frame, text="Traducción a Ruby:").grid(row=2, column=1, sticky="nw")
        self.ruby_output = scrolledtext.ScrolledText(results_frame, width=40, height=10)
        self.ruby_output.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

        # Assembler
        tk.Label(results_frame, text="Traducción a Assembler:").grid(row=4, column=0, columnspan=2, sticky="nw")
        self.assembler_output = scrolledtext.ScrolledText(results_frame, width=80, height=10)
        self.assembler_output.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Configurar expansión
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_rowconfigure(3, weight=1)
        results_frame.grid_rowconfigure(5, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_columnconfigure(1, weight=1)

    def run_analysis(self):
        codigo = self.code_input.get("1.0", tk.END).strip()
        if not codigo:
            messagebox.showerror("Error", "Ingrese código fuente")
            return

        try:
            # Análisis léxico
            tokens = identificarTokens(codigo)
            self.tokens_output.delete("1.0", tk.END)
            for token in tokens:
                self.tokens_output.insert(tk.END, f"{token}\n")

            # Análisis sintáctico
            parser = Parse(tokens)
            arbol_ast = parser.parsear()

            # Mostrar AST
            self.ast_output.delete("1.0", tk.END)
            self.ast_output.insert(tk.END, json.dumps(imprimir_ast(arbol_ast), indent=2))

            # Traducciones
            self.python_output.delete("1.0", tk.END)
            self.python_output.insert(tk.END, arbol_ast.traducirPy())

            self.ruby_output.delete("1.0", tk.END)
            self.ruby_output.insert(tk.END, arbol_ast.traducirRuby())

            self.assembler_output.delete("1.0", tk.END)
            self.assembler_output.insert(tk.END, arbol_ast.generarCodigo())

        except Exception as e:
            messagebox.showerror("Error", f"Error en el análisis: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CompiladorGUI(root)
    root.mainloop()