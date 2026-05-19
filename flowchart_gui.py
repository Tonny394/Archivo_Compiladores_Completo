import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog

from compilador import identificarTokens
from tokens import Parse, imprimir_ast


class FlowchartGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Flowchart / Compilador")
        self.geometry("1280x780")
        self.minsize(1160, 700)
        self.configure(bg="#f0f0f0")

        self.nodes = {}
        self.connections = []
        self.node_counter = 0
        self.selected_node = None
        self.selected_connection = None
        self.connect_mode = False
        self.connect_source = None
        self.delete_node_mode = False
        self.delete_connection_mode = False
        self.drag_data = {"node_id": None, "x": 0, "y": 0}

        self.shape_defaults = {
            "Inicio/Fin": "main",
            "Proceso": "x = x + 1",
            "Decisión": "x > 0",
            "Entrada/Salida": "printf(\"texto\");",
            "Asignación": "int x = 0;",
            "Función": "int sumar(int a, int b)",
            "Llamada": "sumar(1, 2);",
            "Ciclo": "x < 10",
            "Comentario": "// Comentario",
            "Conector": "Conector",
            "Subproceso": "Subproceso",
        }

        self._build_top_bar()
        self._build_main_layout()

    def _build_top_bar(self):
        top_frame = tk.Frame(self, bg="#2c3e50", height=60)
        top_frame.pack(side="top", fill="x")

        title_label = tk.Label(
            top_frame,
            text="Compilador / Diseñador de Diagramas",
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Segoe UI", 16, "bold"),
        )
        title_label.pack(side="left", padx=20, pady=12)

        compile_button = ttk.Button(
            top_frame,
            text="Compilar",
            command=self._compile_flowchart,
        )
        compile_button.pack(side="right", padx=20, pady=12)

    def _build_main_layout(self):
        content_frame = tk.Frame(self, bg="#f0f0f0")
        content_frame.pack(side="top", fill="both", expand=True, padx=12, pady=12)

        left_panel = tk.Frame(content_frame, bg="#34495e", width=260)
        left_panel.pack(side="left", fill="y")

        left_title = tk.Label(
            left_panel,
            text="Formas / Funciones",
            bg="#34495e",
            fg="#ecf0f1",
            font=("Segoe UI", 12, "bold"),
        )
        left_title.pack(anchor="nw", padx=16, pady=(16, 8))

        self._build_shape_buttons(left_panel)

        tool_frame = tk.Frame(left_panel, bg="#34495e")
        tool_frame.pack(fill="x", padx=16, pady=(12, 8))

        connect_button = ttk.Button(tool_frame, text="Conectar", command=self._toggle_connect_mode)
        connect_button.pack(fill="x", pady=4)

        delete_button = ttk.Button(tool_frame, text="Eliminar nodo", command=self._toggle_delete_node_mode)
        delete_button.pack(fill="x", pady=4)

        delete_conn_button = ttk.Button(tool_frame, text="Eliminar conexión", command=self._toggle_delete_connection_mode)
        delete_conn_button.pack(fill="x", pady=4)

        clear_button = ttk.Button(tool_frame, text="Limpiar todo", command=self._clear_workspace)
        clear_button.pack(fill="x", pady=4)

        center_frame = tk.Frame(content_frame, bg="#f0f0f0")
        center_frame.pack(side="left", fill="both", expand=True, padx=(12, 0))

        canvas_frame = tk.Frame(center_frame, bg="#ffffff", bd=1, relief="solid")
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#ecf0f1", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, side="left")

        scrollbar_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar_y.set)

        self.canvas.bind("<Button-1>", self._on_canvas_click)

        self.code_frame = tk.Frame(center_frame, bg="#ffffff", bd=1, relief="solid")
        self.code_frame.pack(fill="x", pady=(10, 0))

        code_label = tk.Label(
            self.code_frame,
            text="Código generado",
            bg="#ffffff",
            fg="#2c3e50",
            font=("Segoe UI", 11, "bold"),
        )
        code_label.pack(anchor="nw", padx=10, pady=(10, 6))

        self.editor_text = tk.Text(
            self.code_frame,
            height=10,
            bg="#f7f9fa",
            fg="#2c3e50",
            font=("Consolas", 11),
            wrap="word",
            bd=0,
            padx=10,
            pady=10,
        )
        self.editor_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        right_panel = tk.Frame(content_frame, bg="#f0f0f0", width=380)
        right_panel.pack(side="right", fill="y", padx=(12, 0))

        self._build_detail_panel(right_panel)
        self._build_info_panel(
            right_panel,
            "Información del Código",
            "Aquí se mostrará el análisis del flujo y la sintaxis generada.",
            "code_info",
        )
        self._build_info_panel(
            right_panel,
            "Conversión al Código Diseñado",
            "Aquí aparecerá la conversión automática al código de destino.",
            "conversion_info",
        )
        self._build_info_panel(
            right_panel,
            "Información de Assembler",
            "Aquí aparecerá la información generada para assembler.",
            "assembler_info",
        )

        self.status_label = tk.Label(
            self,
            text="Selecciona un nodo o activa Conectar para unir dos nodos.",
            bg="#ecf0f0",
            fg="#2c3e50",
            anchor="w",
            padx=16,
        )
        self.status_label.pack(fill="x", side="bottom")

    def _build_shape_buttons(self, parent):
        categories = [
            ("Estructura", ["Inicio/Fin", "Proceso", "Decisión", "Entrada/Salida"]),
            ("Operaciones", ["Asignación", "Función", "Llamada", "Ciclo"]),
            ("Utilidades", ["Comentario", "Conector", "Subproceso"]),
        ]

        for category, items in categories:
            cat_label = tk.Label(
                parent,
                text=category,
                bg="#34495e",
                fg="#bdc3c7",
                font=("Segoe UI", 10, "bold"),
            )
            cat_label.pack(anchor="nw", padx=16, pady=(12, 4))

            for item in items:
                btn = ttk.Button(
                    parent,
                    text=item,
                    command=lambda text=item: self._add_node(text),
                )
                btn.pack(anchor="nw", fill="x", padx=16, pady=4)

    def _build_detail_panel(self, parent):
        frame = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid")
        frame.pack(fill="x", pady=8)

        title_label = tk.Label(
            frame,
            text="Detalle del Bloque",
            bg="#ffffff",
            fg="#2c3e50",
            font=("Segoe UI", 11, "bold"),
        )
        title_label.pack(anchor="nw", padx=12, pady=(12, 6))

        self.detail_text = tk.Text(
            frame,
            height=6,
            bg="#fbfbfb",
            fg="#2c3e50",
            font=("Consolas", 10),
            wrap="word",
            bd=0,
            padx=8,
            pady=8,
        )
        self.detail_text.insert("1.0", "Selecciona un bloque para ver sus detalles.")
        self.detail_text.config(state="disabled")
        self.detail_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        actions_frame = tk.Frame(frame, bg="#ffffff")
        actions_frame.pack(fill="x", padx=12, pady=(0, 12))

        view_button = ttk.Button(actions_frame, text="Ver bloque", command=self._open_expanded_view_for_selected)
        view_button.pack(side="left", expand=True, fill="x", padx=(0, 4))

        edit_button = ttk.Button(actions_frame, text="Editar bloque", command=self._edit_selected_block)
        edit_button.pack(side="left", expand=True, fill="x", padx=(4, 0))

        self.detail_text_widget = self.detail_text

    def _build_info_panel(self, parent, title, placeholder, attr_name):
        frame = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid")
        frame.pack(fill="x", pady=8)

        title_label = tk.Label(
            frame,
            text=title,
            bg="#ffffff",
            fg="#2c3e50",
            font=("Segoe UI", 11, "bold"),
        )
        title_label.pack(anchor="nw", padx=12, pady=(12, 6))

        text_widget = tk.Text(
            frame,
            height=8,
            bg="#fbfbfb",
            fg="#2c3e50",
            font=("Consolas", 10),
            wrap="word",
            bd=0,
            padx=8,
            pady=8,
        )
        text_widget.insert("1.0", placeholder)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        setattr(self, f"_{attr_name}_widget", text_widget)

    def _add_node(self, shape_type):
        x = 50 + (self.node_counter % 3) * 220
        y = 50 + (self.node_counter // 3) * 140
        label = self.shape_defaults.get(shape_type, shape_type)
        self._create_node(shape_type, x, y, label)
        self.node_counter += 1
        self.status_label.config(text=f"Nodo '{shape_type}' agregado. Haz doble clic para editarlo.")

    def _create_node(self, shape_type, x, y, label):
        width = 180
        height = 80
        node_id = f"node{len(self.nodes) + 1}"

        if shape_type == "Inicio/Fin":
            shape_id = self.canvas.create_oval(x, y, x + width, y + height, fill="#ffffff", outline="#2c3e50", width=2)
        elif shape_type == "Decisión":
            shape_id = self.canvas.create_polygon(
                x + width / 2, y,
                x + width, y + height / 2,
                x + width / 2, y + height,
                x, y + height / 2,
                fill="#ffffff",
                outline="#2c3e50",
                width=2,
            )
        elif shape_type == "Entrada/Salida":
            shape_id = self.canvas.create_polygon(
                x + 20, y,
                x + width, y,
                x + width - 20, y + height,
                x, y + height,
                fill="#ffffff",
                outline="#2c3e50",
                width=2,
            )
        elif shape_type == "Conector":
            radius = min(width, height) / 4
            shape_id = self.canvas.create_oval(
                x + width / 2 - radius,
                y + height / 2 - radius,
                x + width / 2 + radius,
                y + height / 2 + radius,
                fill="#ffffff",
                outline="#2c3e50",
                width=2,
            )
        elif shape_type == "Subproceso":
            shape_id = self.canvas.create_rectangle(x, y, x + width, y + height, fill="#ffffff", outline="#2c3e50", width=2, dash=(4, 4))
        else:
            shape_id = self.canvas.create_rectangle(x, y, x + width, y + height, fill="#ffffff", outline="#2c3e50", width=2)

        text_id = self.canvas.create_text(
            x + width / 2,
            y + height / 2 - 8,
            text=label,
            width=width - 20,
            font=("Segoe UI", 10),
            fill="#2c3e50",
        )

        button_width = 44
        button_height = 20
        button_x1 = x + width - button_width - 10
        button_y1 = y + height - button_height - 8
        button_x2 = button_x1 + button_width
        button_y2 = button_y1 + button_height

        view_rect_id = self.canvas.create_rectangle(
            button_x1,
            button_y1,
            button_x2,
            button_y2,
            fill="#2980b9",
            outline="#1c5980",
            width=1,
            tags=(node_id, f"view-{node_id}"),
        )
        view_text_id = self.canvas.create_text(
            (button_x1 + button_x2) / 2,
            (button_y1 + button_y2) / 2,
            text="VER",
            fill="#ffffff",
            font=("Segoe UI", 8, "bold"),
            tags=(node_id, f"view-{node_id}"),
        )

        self.canvas.addtag_withtag(node_id, shape_id)
        self.canvas.addtag_withtag(node_id, text_id)
        self.canvas.addtag_withtag(node_id, view_rect_id)
        self.canvas.addtag_withtag(node_id, view_text_id)
        self.canvas.addtag_withtag("shape", shape_id)
        self.canvas.addtag_withtag("shape", text_id)
        self.canvas.addtag_withtag("shape", view_rect_id)
        self.canvas.addtag_withtag("shape", view_text_id)

        self.canvas.tag_bind(node_id, "<ButtonPress-1>", self._on_node_press)
        self.canvas.tag_bind(node_id, "<B1-Motion>", self._on_node_motion)
        self.canvas.tag_bind(node_id, "<ButtonRelease-1>", self._on_node_release)
        self.canvas.tag_bind(node_id, "<Double-Button-1>", lambda event, nid=node_id: self._edit_node_text(nid))

        self.nodes[node_id] = {
            "shape_id": shape_id,
            "text_id": text_id,
            "view_rect_id": view_rect_id,
            "view_text_id": view_text_id,
            "type": shape_type,
            "label": label,
            "order": len(self.nodes),
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }

    def _on_canvas_click(self, event):
        if self.connect_mode or self.delete_node_mode or self.delete_connection_mode:
            return
        self._deselect_node()

    def _on_node_press(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return

        tags = self.canvas.gettags(item[0])
        view_tag = next((t for t in tags if t.startswith("view-")), None)
        conn_tag = next((t for t in tags if t == "connection"), None)
        node_tag = next((t for t in tags if t.startswith("node")), None)

        if conn_tag:
            conn = next((c for c in self.connections if c["line_id"] == item[0]), None)
            if conn:
                self._select_connection(conn)
            return

        if view_tag and node_tag:
            self._show_expanded_view(node_tag)
            return

        if self.delete_node_mode and node_tag:
            self._delete_node(node_tag)
            return

        if self.connect_mode and node_tag:
            self._connect_nodes(node_tag)
            return

        if node_tag:
            self._select_node(node_tag)
            self.drag_data["node_id"] = node_tag
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def _on_node_motion(self, event):
        node_id = self.drag_data["node_id"]
        if not node_id or self.connect_mode:
            return

        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(node_id, dx, dy)

        node = self.nodes[node_id]
        node["x"] += dx
        node["y"] += dy
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

        self._update_connections(node_id)

    def _on_node_release(self, event):
        self.drag_data["node_id"] = None

    def _on_connection_click(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return
        conn = next((c for c in self.connections if c["line_id"] == item[0]), None)
        if not conn:
            return

        if self.delete_connection_mode:
            self._delete_connection(conn)
            return

        self._select_connection(conn)

    def _select_node(self, node_id):
        self._deselect_connection()
        self._deselect_node()
        node = self.nodes.get(node_id)
        if not node:
            return

        self.canvas.itemconfig(node["shape_id"], outline="#2980b9", width=3)
        self.selected_node = node_id
        self._update_detail_panel(node_id)
        self.status_label.config(text=f"Nodo seleccionado: {node['type']} - {node['label']}")

    def _deselect_node(self):
        if not self.selected_node:
            return
        node = self.nodes.get(self.selected_node)
        if node:
            self.canvas.itemconfig(node["shape_id"], outline="#2c3e50", width=2)
        self.selected_node = None
        self._clear_detail_panel()
        self.status_label.config(text="Selecciona un nodo o activa Conectar para unir dos nodos.")

    def _select_connection(self, connection):
        self._deselect_node()
        self._deselect_connection()
        self.selected_connection = connection
        self.canvas.itemconfig(connection["line_id"], fill="#c0392b", width=3)
        self.status_label.config(text=f"Conexión seleccionada: {connection['source']} → {connection['target']}")

    def _deselect_connection(self):
        if not self.selected_connection:
            return
        self.canvas.itemconfig(self.selected_connection["line_id"], fill="#34495e", width=2)
        self.selected_connection = None

    def _update_connections(self, node_id):
        for conn in self.connections:
            if conn["source"] == node_id or conn["target"] == node_id:
                source = self.nodes[conn["source"]]
                target = self.nodes[conn["target"]]
                x1 = source["x"] + source["width"] / 2
                y1 = source["y"] + source["height"]
                x2 = target["x"] + target["width"] / 2
                y2 = target["y"]
                self.canvas.coords(conn["line_id"], x1, y1, x2, y2)

    def _update_detail_panel(self, node_id):
        node = self.nodes.get(node_id)
        if not node:
            return
        detail = (
            f"Tipo: {node['type']}\n"
            f"Contenido: {node['label']}\n"
            f"Posición: {int(node['x'])}, {int(node['y'])}\n"
            f"Conexiones: {len([c for c in self.connections if c['source'] == node_id or c['target'] == node_id])}"
        )
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", detail)
        self.detail_text.config(state="disabled")

    def _clear_detail_panel(self):
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", "Selecciona un bloque para ver sus detalles.")
        self.detail_text.config(state="disabled")

    def _update_info_widget(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def _open_expanded_view_for_selected(self):
        if not self.selected_node:
            messagebox.showwarning("Atención", "Selecciona un bloque primero.")
            return
        self._show_expanded_view(self.selected_node)

    def _edit_selected_block(self):
        if not self.selected_node:
            messagebox.showwarning("Atención", "Selecciona un bloque primero.")
            return
        self._edit_node_text(self.selected_node)

    def _toggle_connect_mode(self):
        self.connect_mode = not self.connect_mode
        self.delete_node_mode = False
        self.delete_connection_mode = False
        self.connect_source = None
        if self.connect_mode:
            self.status_label.config(text="Modo conectar activado: haz clic en el nodo de origen.")
        else:
            self.status_label.config(text="Modo conectar desactivado.")

    def _toggle_delete_node_mode(self):
        self.delete_node_mode = not self.delete_node_mode
        self.connect_mode = False
        self.delete_connection_mode = False
        self.connect_source = None
        if self.delete_node_mode:
            self.status_label.config(text="Modo eliminar nodo activado: haz clic en un nodo para borrar.")
        else:
            self.status_label.config(text="Modo eliminar nodo desactivado.")

    def _toggle_delete_connection_mode(self):
        self.delete_connection_mode = not self.delete_connection_mode
        self.connect_mode = False
        self.delete_node_mode = False
        self.connect_source = None
        if self.delete_connection_mode:
            self.status_label.config(text="Modo eliminar conexión activado: haz clic en una conexión para borrar.")
        else:
            self.status_label.config(text="Modo eliminar conexión desactivado.")

    def _connect_nodes(self, node_id):
        if self.connect_source is None:
            self.connect_source = node_id
            self.status_label.config(text=f"Origen seleccionado: {self.nodes[node_id]['type']}. Selecciona el destino.")
            return

        if self.connect_source == node_id:
            self.status_label.config(text="No puedes conectar un nodo consigo mismo. Selecciona otro nodo.")
            return

        source = self.nodes[self.connect_source]
        target = self.nodes[node_id]

        x1 = source["x"] + source["width"] / 2
        y1 = source["y"] + source["height"]
        x2 = target["x"] + target["width"] / 2
        y2 = target["y"]

        line_id = self.canvas.create_line(x1, y1, x2, y2, arrow="last", fill="#34495e", width=2, tags=("connection", f"conn{len(self.connections)+1}"))
        self.canvas.tag_bind(line_id, "<Button-1>", self._on_connection_click)
        self.connections.append({"source": self.connect_source, "target": node_id, "line_id": line_id})
        self.status_label.config(text=f"Conectado {self.connect_source} → {node_id}.")
        self.connect_source = None

    def _edit_node_text(self, node_id):
        node = self.nodes.get(node_id)
        if not node:
            return

        new_text = simpledialog.askstring("Editar texto", "Ingresa el texto del nodo:", initialvalue=node["label"], parent=self)
        if new_text is None:
            return

        self.canvas.itemconfig(node["text_id"], text=new_text)
        node["label"] = new_text
        if self.selected_node == node_id:
            self.status_label.config(text=f"Nodo seleccionado: {node['type']} - {new_text}")
            self._update_detail_panel(node_id)

    def _show_expanded_view(self, node_id):
        node = self.nodes.get(node_id)
        if not node:
            return

        modal = tk.Toplevel(self)
        modal.title(f"Bloque: {node['type']}")
        modal.geometry("460x320")
        modal.transient(self)
        modal.grab_set()

        title_label = tk.Label(modal, text=f"{node['type']} - Vista ampliada", font=("Segoe UI", 12, "bold"), bg="#f7f9fa", fg="#2c3e50")
        title_label.pack(fill="x", padx=12, pady=(12, 8))

        content_label = tk.Label(modal, text="Contenido del bloque:", font=("Segoe UI", 10), bg="#f7f9fa", fg="#2c3e50")
        content_label.pack(anchor="w", padx=12, pady=(0, 4))

        content_text = tk.Text(modal, height=10, bg="#ffffff", fg="#2c3e50", font=("Consolas", 11), wrap="word", bd=1, padx=10, pady=10)
        content_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        content_text.insert("1.0", node["label"])

        save_button = ttk.Button(modal, text="Guardar cambios", command=lambda: self._save_expanded_node(node_id, content_text, modal))
        save_button.pack(side="right", padx=12, pady=(0, 12))

    def _save_expanded_node(self, node_id, content_text, modal):
        new_label = content_text.get("1.0", "end").strip()
        if not new_label:
            messagebox.showwarning("Atención", "El contenido no puede estar vacío.")
            return

        node = self.nodes.get(node_id)
        if not node:
            return

        self.canvas.itemconfig(node["text_id"], text=new_label)
        node["label"] = new_label
        if self.selected_node == node_id:
            self._update_detail_panel(node_id)
            self.status_label.config(text=f"Nodo seleccionado: {node['type']} - {new_label}")
        modal.destroy()

    def _delete_selected_node(self):
        if not self.selected_node:
            messagebox.showwarning("Atención", "Selecciona primero un nodo para eliminar.")
            return

        self._delete_node(self.selected_node)

    def _delete_selected_connection(self):
        if not self.selected_connection:
            messagebox.showwarning("Atención", "Selecciona primero una conexión para eliminar.")
            return

        self._delete_connection(self.selected_connection)

    def _delete_node(self, node_id):
        node = self.nodes.pop(node_id, None)
        if not node:
            return

        self._deselect_node()
        self.canvas.delete(node_id)
        self.canvas.delete(node["shape_id"])
        self.canvas.delete(node["text_id"])
        self.canvas.delete(node["view_rect_id"])
        self.canvas.delete(node["view_text_id"])

        for conn in list(self.connections):
            if conn["source"] == node_id or conn["target"] == node_id:
                self.canvas.delete(conn["line_id"])
                self.connections.remove(conn)

        self.delete_node_mode = False
        self.status_label.config(text="Nodo eliminado.")

    def _delete_connection(self, connection):
        self.canvas.delete(connection["line_id"])
        self.connections = [c for c in self.connections if c["line_id"] != connection["line_id"]]
        self.selected_connection = None
        self.delete_connection_mode = False
        self.status_label.config(text="Conexión eliminada.")

    def _clear_workspace(self):
        for node_id, node in list(self.nodes.items()):
            self.canvas.delete(node_id)
            self.canvas.delete(node["shape_id"])
            self.canvas.delete(node["text_id"])
            self.canvas.delete(node["view_rect_id"])
            self.canvas.delete(node["view_text_id"])
        self.nodes.clear()
        self.node_counter = 0

        for conn in self.connections:
            self.canvas.delete(conn["line_id"])
        self.connections.clear()

        self.selected_node = None
        self.selected_connection = None
        self.editor_text.delete("1.0", "end")
        self._clear_detail_panel()
        self._update_info_widget(self._code_info_widget, "")
        self._update_info_widget(self._conversion_info_widget, "")
        self._update_info_widget(self._assembler_info_widget, "")
        self.status_label.config(text="Workspace limpio.")

    def _compile_flowchart(self):
        if not self.nodes:
            messagebox.showwarning("Atención", "No hay nodos en el diagrama. Agrega formas para crear código.")
            return

        source = self._generate_code_from_flowchart()
        self.editor_text.delete("1.0", "end")
        self.editor_text.insert("1.0", source)

        try:
            tokens = identificarTokens(source)
            parser = Parse(tokens)
            ast = parser.parsear()

            lexical_info = [f"{tok[0]}: '{tok[1]}'" for tok in tokens]
            code_info = (
                f"Tokens encontrados: {len(tokens)}\n"
                f"{', '.join(lexical_info)}\n\n"
                f"AST:\n{json.dumps(imprimir_ast(ast), indent=2, ensure_ascii=False)}"
            )
            self._update_info_widget(self._code_info_widget, code_info)

            conversion_info = (
                f"Python:\n{ast.traducirPy()}\n\n"
                f"Ruby:\n{ast.traducirRuby()}"
            )
            self._update_info_widget(self._conversion_info_widget, conversion_info)

            try:
                assembler_info = ast.generarCodigo()
            except Exception:
                assembler_info = "La generación de assembler no está disponible para este AST."
            self._update_info_widget(self._assembler_info_widget, assembler_info)
            self.status_label.config(text="Compilación completada.")
            messagebox.showinfo("Compilación", "La compilación se ha ejecutado con éxito.")
        except Exception as e:
            self._update_info_widget(self._code_info_widget, f"Error: {e}")
            self._update_info_widget(self._conversion_info_widget, "No se pudo generar la conversión.")
            self._update_info_widget(self._assembler_info_widget, "No se pudo generar assembler.")
            self.status_label.config(text="Error de compilación. Revisa el código generado.")
            messagebox.showerror("Error de compilación", str(e))

    def _generate_code_from_flowchart(self):
        lines = ["int main() {"]
        for node_id in sorted(self.nodes, key=lambda nid: (self.nodes[nid]["y"], self.nodes[nid]["x"])):
            node = self.nodes[node_id]
            label = node["label"].strip()
            if node["type"] == "Inicio/Fin":
                continue
            elif node["type"] == "Proceso":
                if not label.endswith(";"):
                    label += ";"
                lines.append(f"    {label}")
            elif node["type"] == "Asignación":
                if not label.endswith(";"):
                    label += ";"
                lines.append(f"    {label}")
            elif node["type"] == "Decisión":
                condition = label if label else "condicion"
                lines.append(f"    if ({condition}) {{")
                lines.append("        // TODO: Completa el bloque IF")
                lines.append("    }")
            elif node["type"] == "Entrada/Salida":
                if label.startswith("printf") or label.startswith("puts"):
                    lines.append(f"    {label}")
                else:
                    lines.append(f"    printf(\"{label}\");")
            elif node["type"] == "Función":
                if not label.endswith(";"):
                    lines.append(f"    // Función: {label}")
                else:
                    lines.append(f"    {label}")
            elif node["type"] == "Llamada":
                if not label.endswith(";"):
                    label += ";"
                lines.append(f"    {label}")
            elif node["type"] == "Ciclo":
                condition = label if label else "condicion"
                lines.append(f"    while ({condition}) {{")
                lines.append("        // TODO: Completa el ciclo")
                lines.append("    }")
            elif node["type"] == "Comentario":
                lines.append(f"    // {label}")
            elif node["type"] == "Conector":
                lines.append(f"    // Conector: {label}")
            elif node["type"] == "Subproceso":
                lines.append(f"    // Subproceso: {label}")
            else:
                lines.append(f"    {label}")

        lines.append("    return 0;")
        lines.append("}")
        return "\n".join(lines)


if __name__ == "__main__":
    app = FlowchartGUI()
    app.mainloop()
