"""
Demostración de la funcionalidad del Constructor de Diagramas de Flujo
Sin interfaz gráfica - Prueba de lógica
"""

from compilador import identificarTokens
from tokens import Parse, imprimir_ast
from Analisis_Sematico import AnalisisSemantico
import json

def demonstrate_flow_to_code():
    """Demuestra cómo se generaría código a partir de un diagrama de flujo"""
    
    print("=" * 80)
    print("DEMOSTRACION: Constructor de Diagramas de Flujo - Compilador Integrado")
    print("=" * 80)
    
    # Simular nodos de un diagrama
    print("\n1. SIMULACION DE DIAGRAMA DE FLUJO")
    print("-" * 80)
    
    nodos = [
        {"tipo": "inicio", "texto": "inicio"},
        {"tipo": "proceso", "texto": "float a = 3.5"},
        {"tipo": "proceso", "texto": "int b = 2"},
        {"tipo": "proceso", "texto": "float suma = a + b"},
        {"tipo": "decision", "texto": "suma > 5.0"},
        {"tipo": "proceso", "texto": "float resultado = suma * 2"},
        {"tipo": "fin", "texto": "fin"},
    ]
    
    print("\nNodos del diagrama (en orden):")
    for i, nodo in enumerate(nodos, 1):
        print(f"  {i}. [{nodo['tipo'].upper()}] {nodo['texto']}")
    
    # Generar código a partir del diagrama
    print("\n2. GENERACION DE CODIGO FUENTE")
    print("-" * 80)
    
    code_lines = ["int main(){"]
    for nodo in nodos:
        if nodo["tipo"] == "proceso":
            code_lines.append(f"    {nodo['texto']};")
        elif nodo["tipo"] == "decision":
            code_lines.append(f"    if ({nodo['texto']}) {{")
            code_lines.append("        float resultado = suma * 2;")
            code_lines.append("    }")
    
    code_lines.append("}")
    codigo_fuente = "\n".join(code_lines)
    
    print("\nCodigo C++ generado:")
    print(codigo_fuente)
    
    # Análisis léxico
    print("\n3. ANALISIS LEXICO")
    print("-" * 80)
    
    tokens = identificarTokens(codigo_fuente)
    print(f"Total de tokens identificados: {len(tokens)}")
    print("\nPrimeros 15 tokens:")
    for i, token in enumerate(tokens[:15], 1):
        print(f"  {i}. {token}")
    
    # Análisis sintáctico
    print("\n4. ANALISIS SINTACTICO")
    print("-" * 80)
    
    try:
        parser = Parse(tokens)
        ast = parser.parsear()
        print("Analisis sintactico: EXITOSO")
        
        # Mostrar AST
        print("\nArbol de Sintaxis Abstracta (AST):")
        ast_json = imprimir_ast(ast)
        print(json.dumps(ast_json, indent=2))
        
    except Exception as e:
        print(f"Error sintactico: {e}")
        return
    
    # Análisis semántico
    print("\n5. ANALISIS SEMANTICO")
    print("-" * 80)
    
    try:
        analizador_semantico = AnalisisSemantico()
        analizador_semantico.analizar(ast)
        print("Analisis semantico: EXITOSO")
        
        print("\nTabla de Simbolos:")
        print("-" * 40)
        for simbolo, info in analizador_semantico.tabla_simbolos.items():
            print(f"  {simbolo}:")
            if isinstance(info, dict):
                for clave, valor in info.items():
                    if clave != 'Parametros':
                        print(f"    - {clave}: {valor}")
        
    except Exception as e:
        print(f"Error semantico: {e}")
    
    # Traducciones
    print("\n6. TRADUCCIONES")
    print("-" * 80)
    
    print("\nTraduccion a Python:")
    print("-" * 40)
    print(ast.traducirPy())
    
    print("\n\nTraduccion a Ruby:")
    print("-" * 40)
    print(ast.traducirRuby())
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print("""
Fases del Compilador Completadas:

1. ANALISIS LEXICO
   - Identifica y clasifica todos los tokens
   - Reconoce palabras clave, identificadores, numeros, operadores, etc.
   - Soporta numeros de coma flotante

2. ANALISIS SINTACTICO
   - Construye el Arbol de Sintaxis Abstracta (AST)
   - Valida la estructura gramatical del codigo
   - Detecta errores de sintaxis

3. ANALISIS SEMANTICO
   - Verifica consistencia de tipos
   - Mantiene tabla de simbolos
   - Detecta variables no declaradas
   - Valida tipos en operaciones aritmeticas

4. TRADUCCIONES
   - Convierte codigo C++ a Python equivalente
   - Convierte codigo C++ a Ruby equivalente
   - Preserva la logica del programa

INTERFAZ GRAFICA INTEGRADA:

- Crear nodos arrastrando formas
- Conectar nodos entre si
- Editar contenido de cada nodo
- Generar codigo automaticamente a partir del diagrama
- Visualizar todos los analisis en pestanas
- Resultados organizados y de facil acceso
    """)
    
    print("=" * 80)
    print("DEMOSTRACION COMPLETADA EXITOSAMENTE")
    print("=" * 80)

if __name__ == "__main__":
    demonstrate_flow_to_code()
