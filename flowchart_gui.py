import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Toplevel
from compilador import identificarTokens
from tokens import Parse
from Parametros import *
import json

class FlowchartNode:
    def __init__(self, canvas, x, y, node_type, text=""):
        self.canvas = canvas
        self.node_type = node_type
        self.text = text
        self.x = x
        self.y = y
        self.width = 100
        self.height = 50
        self.id = None
        self.connections = []
        self.draw()

    def draw(self):
        if self.node_type == "start":
            self.id = self.canvas.create_oval(self.x - self.width//2, self.y - self.height//2,
                                              self.x + self.width//2, self.y + self.height//2,
                                              fill="lightgreen")
        elif self.node_type == "end":
            self.id = self.canvas.create_oval(self.x - self.width//2, self.y - self.height//2,
                                              self.x + self.width//2, self.y + self.height//2,
                                              fill="lightcoral")
        elif self.node_type == "process":
            self.id = self.canvas.create_rectangle(self.x - self.width//2, self.y - self.height//2,
                                                   self.x + self.width//2, self.y + self.height//2,
                                                   fill="lightblue")
        elif self.node_type == "decision":
            self.id = self.canvas.create_polygon(self.x, self.y - self.height//2,
                                                 self.x - self.width//2, self.y,
                                                 self.x, self.y + self.height//2,
                                                 self.x + self.width//2, self.y,
                                                 fill="lightyellow")
        self.text_id = self.canvas.create_text(self.x, self.y, text=self.text)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)

class FlowchartGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Constructor de Diagramas de Flujo - Compilador")
        self.root.geometry("1400x900")

        self.nodes = []
        self.selected_node = None
        self.dragging = False

        # Toolbar
        toolbar = tk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar, text="Inicio", command=lambda: self.add_node("start")).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Fin", command=lambda: self.add_node("end")).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Proceso", command=lambda: self.add_node("process")).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Decisión", command=lambda: self.add_node("decision")).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Generar Código", command=self.generate_code).pack(side=tk.LEFT, padx=10)
        tk.Button(toolbar, text="Limpiar", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)

        # Canvas
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def add_node(self, node_type):
        x, y = 200, 200
        text = ""
        if node_type == "process":
            text = "int x = 5;"
        elif node_type == "decision":
            text = "x > 0"
        node = FlowchartNode(self.canvas, x, y, node_type, text)
        self.nodes.append(node)

    def on_canvas_click(self, event):
        for node in self.nodes:
            if self.canvas.coords(node.id)[0] <= event.x <= self.canvas.coords(node.id)[2] and \
               self.canvas.coords(node.id)[1] <= event.y <= self.canvas.coords(node.id)[3]:
                self.selected_node = node
                self.dragging = True
                break

    def on_drag(self, event):
        if self.dragging and self.selected_node:
            dx = event.x - self.selected_node.x
            dy = event.y - self.selected_node.y
            self.selected_node.move(dx, dy)

    def on_release(self, event):
        self.dragging = False
        self.selected_node = None

    def clear_canvas(self):
        self.canvas.delete("all")
        self.nodes = []

    def generate_code(self):
        # Generar código C++ simple basado en los nodos
        code_lines = []
        for node in self.nodes:
            if node.node_type == "process" and node.text:
                code_lines.append(node.text)
            elif node.node_type == "decision" and node.text:
                code_lines.append(f"if ({node.text}) {{")
                code_lines.append("    // cuerpo del if")
                code_lines.append("}")

        if code_lines:
            cpp_code = "int main(){\n" + "\n".join("    " + line for line in code_lines) + "\n}"
        else:
            cpp_code = "int main(){\n    // Código vacío\n}"

        # Mostrar ventana con código C++
        self.show_code_window("Código C++ Generado", cpp_code)

        # Compilar y mostrar assembler
        try:
            tokens = identificarTokens(cpp_code)
            parser = Parse(tokens)
            ast = parser.parsear()
            assembler_code = ast.generarCodigo()
            self.show_code_window("Código Assembler", assembler_code)
        except Exception as e:
            messagebox.showerror("Error", f"Error en compilación: {str(e)}")

    def show_code_window(self, title, code):
        window = Toplevel(self.root)
        window.title(title)
        window.geometry("600x400")
        text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, code)
        text_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowchartGUI(root)
    root.mainloop()