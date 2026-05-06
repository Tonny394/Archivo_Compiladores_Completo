import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, Toplevel
from compilador import identificarTokens
from tokens import Parse, imprimir_ast
from Analisis_Sematico import AnalisisSemantico
from Parametros import *
import json

class FlowchartNode:
    counter = 0
    
    def __init__(self, canvas, x, y, node_type, text=""):
        FlowchartNode.counter += 1
        self.id_num = FlowchartNode.counter
        self.canvas = canvas
        self.node_type = node_type
        self.text = text
        self.x = x
        self.y = y
        self.width = 120
        self.height = 60
        self.id = None
        self.text_id = None
        self.connections = []
        self.is_selected = False
        self.draw()

    def draw(self):
        if self.node_type == "inicio":
            self.id = self.canvas.create_oval(self.x - self.width//2, self.y - self.height//2,
                                              self.x + self.width//2, self.y + self.height//2,
                                              fill="lightgreen", width=2, outline="black")
        elif self.node_type == "fin":
            self.id = self.canvas.create_oval(self.x - self.width//2, self.y - self.height//2,
                                              self.x + self.width//2, self.y + self.height//2,
                                              fill="lightcoral", width=2, outline="black")
        elif self.node_type == "proceso":
            self.id = self.canvas.create_rectangle(self.x - self.width//2, self.y - self.height//2,
                                                   self.x + self.width//2, self.y + self.height//2,
                                                   fill="lightblue", width=2, outline="black")
        elif self.node_type == "decision":
            self.id = self.canvas.create_polygon(self.x, self.y - self.height//2,
                                                 self.x - self.width//2, self.y,
                                                 self.x, self.y + self.height//2,
                                                 self.x + self.width//2, self.y,
                                                 fill="lightyellow", width=2, outline="black")
        
        self.text_id = self.canvas.create_text(self.x, self.y, text=self.text, width=100, justify=tk.CENTER)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        self.canvas.tag_raise(self.text_id)
        self.update_connections()

    def update_connections(self):
        for conn_id, target_node in self.connections:
            self.canvas.delete(conn_id)
            new_conn = self.canvas.create_line(self.x, self.y, target_node.x, target_node.y,
                                               arrows=tk.LAST, width=2, fill="black")
            idx = self.connections.index((conn_id, target_node))
            self.connections[idx] = (new_conn, target_node)

    def connect_to(self, target_node):
        conn = self.canvas.create_line(self.x, self.y, target_node.x, target_node.y,
                                       arrows=tk.LAST, width=2, fill="black")
        self.connections.append((conn, target_node))

    def select(self):
        self.is_selected = True
        self.canvas.itemconfig(self.id, width=3, outline="red")

    def deselect(self):
        self.is_selected = False
        self.canvas.itemconfig(self.id, width=2, outline="black")

    def contains_point(self, x, y):
        coords = self.canvas.coords(self.id)
        return coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]

    def set_text(self, text):
        self.text = text
        self.canvas.itemconfig(self.text_id, text=text)

class FlowchartGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Constructor de Diagramas de Flujo - Compilador Integrado")
        self.root.geometry("1600x900")

        self.nodes = []
        self.selected_node = None
        self.connecting_from = None
        self.dragging = False
        self.ast = None
        self.tabla_simbolos = {}

        # Toolbar principal
        toolbar = tk.Frame(root, bg="lightgray", height=50)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(toolbar, text="Crear Nodo:", bg="lightgray", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Inicio", command=lambda: self.add_node("inicio"), bg="lightgreen").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Fin", command=lambda: self.add_node("fin"), bg="lightcoral").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Proceso", command=lambda: self.add_node("proceso"), bg="lightblue").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Decision", command=lambda: self.add_node("decision"), bg="lightyellow").pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="|", bg="lightgray").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="Conectar", command=self.start_connection, bg="lightyellow").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Editar", command=self.edit_selected, bg="lightcyan").pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Eliminar", command=self.delete_selected, bg="lightpink").pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="|", bg="lightgray").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="Generar y Analizar", command=self.generate_and_analyze, bg="lightgreen", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Limpiar", command=self.clear_canvas, bg="lightgray").pack(side=tk.LEFT, padx=2)

        # Contenedor principal con canvas y panel de información
        main_container = tk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas para el diagrama
        canvas_frame = tk.LabelFrame(main_container, text="Diagrama de Flujo", font=("Arial", 10, "bold"))
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.canvas = tk.Canvas(canvas_frame, bg="white", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # Panel de información con tabs
        info_frame = tk.LabelFrame(main_container, text="Informacion de Analisis", font=("Arial", 10, "bold"))
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.notebook = ttk.Notebook(info_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab: Código Fuente
        self.code_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, height=10)
        self.notebook.add(self.code_tab, text="Codigo Fuente")

        # Tab: AST
        self.ast_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, height=10)
        self.notebook.add(self.ast_tab, text="AST")

        # Tab: Tabla de Símbolos
        self.symbols_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, height=10)
        self.notebook.add(self.symbols_tab, text="Tabla de Simbolos")

        # Tab: Python
        self.python_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, height=10)
        self.notebook.add(self.python_tab, text="Python")

        # Tab: Ruby
        self.ruby_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, height=10)
        self.notebook.add(self.ruby_tab, text="Ruby")

        # Mensajes de estado
        self.status_label = tk.Label(root, text="Listo. Presione 'Generar y Analizar' para procesar el diagrama.", bg="lightgray")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def add_node(self, node_type):
        x = 300 + len(self.nodes) * 50
        y = 200 + (len(self.nodes) % 3) * 100
        
        text_map = {
            "inicio": "inicio",
            "fin": "fin",
            "proceso": "x = 5",
            "decision": "x > 0"
        }
        
        node = FlowchartNode(self.canvas, x, y, node_type, text_map[node_type])
        self.nodes.append(node)
        self.status_label.config(text=f"Nodo '{node_type}' creado. Total de nodos: {len(self.nodes)}")

    def start_connection(self):
        if self.selected_node:
            self.connecting_from = self.selected_node
            self.status_label.config(text=f"Conectando desde: {self.connecting_from.text}. Haz clic en otro nodo para conectar.")
        else:
            messagebox.showwarning("Advertencia", "Selecciona un nodo primero")

    def edit_selected(self):
        if self.selected_node:
            new_text = simpledialog.askstring("Editar Nodo", "Nuevo texto:", initialvalue=self.selected_node.text)
            if new_text:
                self.selected_node.set_text(new_text)
                self.status_label.config(text=f"Nodo editado: {new_text}")
        else:
            messagebox.showwarning("Advertencia", "Selecciona un nodo primero")

    def delete_selected(self):
        if self.selected_node:
            self.canvas.delete(self.selected_node.id)
            self.canvas.delete(self.selected_node.text_id)
            self.nodes.remove(self.selected_node)
            self.selected_node = None
            self.status_label.config(text=f"Nodo eliminado. Total de nodos: {len(self.nodes)}")
        else:
            messagebox.showwarning("Advertencia", "Selecciona un nodo primero")

    def on_canvas_click(self, event):
        # Si estamos conectando
        if self.connecting_from:
            for node in self.nodes:
                if node.contains_point(event.x, event.y) and node != self.connecting_from:
                    self.connecting_from.connect_to(node)
                    self.status_label.config(text=f"Conectado: {self.connecting_from.text} -> {node.text}")
                    self.connecting_from = None
                    return
            self.connecting_from = None
        
        # Si no estamos conectando, seleccionar nodo
        for node in self.nodes:
            node.deselect()
        
        for node in self.nodes:
            if node.contains_point(event.x, event.y):
                node.select()
                self.selected_node = node
                self.dragging = True
                self.last_x = event.x
                self.last_y = event.y
                return
        
        self.selected_node = None

    def on_drag(self, event):
        if self.dragging and self.selected_node:
            dx = event.x - getattr(self, 'last_x', event.x)
            dy = event.y - getattr(self, 'last_y', event.y)
            self.selected_node.move(dx, dy)
            self.last_x = event.x
            self.last_y = event.y

    def on_release(self, event):
        self.dragging = False

    def on_right_click(self, event):
        for node in self.nodes:
            if node.contains_point(event.x, event.y):
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Editar", command=lambda: self.quick_edit(node))
                menu.add_command(label="Conectar", command=lambda: self.quick_connect(node))
                menu.add_command(label="Eliminar", command=lambda: self.quick_delete(node))
                menu.post(event.x_root, event.y_root)
                return

    def quick_edit(self, node):
        new_text = simpledialog.askstring("Editar Nodo", "Nuevo texto:", initialvalue=node.text)
        if new_text:
            node.set_text(new_text)

    def quick_connect(self, node):
        self.connecting_from = node
        self.status_label.config(text=f"Conectando desde: {node.text}. Haz clic en otro nodo.")

    def quick_delete(self, node):
        self.canvas.delete(node.id)
        self.canvas.delete(node.text_id)
        self.nodes.remove(node)
        if self.selected_node == node:
            self.selected_node = None
        self.status_label.config(text=f"Nodo eliminado. Total: {len(self.nodes)}")

    def generate_and_analyze(self):
        if not self.nodes:
            messagebox.showwarning("Advertencia", "No hay nodos para analizar")
            return

        try:
            code = self.generate_code_from_diagram()
            self.analyze_code(code)
            self.status_label.config(text="Analisis completado exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el analisis: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")

    def generate_code_from_diagram(self):
        code_lines = ["int main(){"]
        
        for node in self.nodes:
            if node.node_type == "inicio":
                pass
            elif node.node_type == "fin":
                pass
            elif node.node_type == "proceso":
                code_lines.append(f"    {node.text};")
            elif node.node_type == "decision":
                code_lines.append(f"    if ({node.text}) {{")
                code_lines.append("    }")
        
        code_lines.append("}")
        
        return "\n".join(code_lines)

    def analyze_code(self, code):
        # Limpiar tabs
        self.code_tab.config(state=tk.NORMAL)
        self.code_tab.delete(1.0, tk.END)
        self.code_tab.insert(tk.END, code)
        self.code_tab.config(state=tk.DISABLED)

        # Análisis léxico
        tokens = identificarTokens(code)

        # Análisis sintáctico
        parser = Parse(tokens)
        self.ast = parser.parsear()

        # Mostrar AST
        self.ast_tab.config(state=tk.NORMAL)
        self.ast_tab.delete(1.0, tk.END)
        ast_json = imprimir_ast(self.ast)
        self.ast_tab.insert(tk.END, json.dumps(ast_json, indent=2))
        self.ast_tab.config(state=tk.DISABLED)

        # Análisis semántico
        try:
            analizador_semantico = AnalisisSemantico()
            analizador_semantico.analizar(self.ast)
            self.tabla_simbolos = analizador_semantico.tabla_simbolos

            self.symbols_tab.config(state=tk.NORMAL)
            self.symbols_tab.delete(1.0, tk.END)
            for simbolo, info in self.tabla_simbolos.items():
                self.symbols_tab.insert(tk.END, f"{simbolo}: {info}\n")
            self.symbols_tab.config(state=tk.DISABLED)
        except Exception as e:
            self.symbols_tab.config(state=tk.NORMAL)
            self.symbols_tab.delete(1.0, tk.END)
            self.symbols_tab.insert(tk.END, f"Error semantico: {str(e)}")
            self.symbols_tab.config(state=tk.DISABLED)

        # Traducciones
        self.python_tab.config(state=tk.NORMAL)
        self.python_tab.delete(1.0, tk.END)
        self.python_tab.insert(tk.END, self.ast.traducirPy())
        self.python_tab.config(state=tk.DISABLED)

        self.ruby_tab.config(state=tk.NORMAL)
        self.ruby_tab.delete(1.0, tk.END)
        self.ruby_tab.insert(tk.END, self.ast.traducirRuby())
        self.ruby_tab.config(state=tk.DISABLED)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.nodes = []
        self.selected_node = None
        self.connecting_from = None
        self.status_label.config(text="Lienzo limpiado")

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowchartGUI(root)
    root.mainloop()
