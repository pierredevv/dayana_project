# -*- coding: utf-8 -*-
"""
Laberinto Inteligente Web: Generación y Solución con Grafos
Especialidad: Algoritmos de Búsqueda y Estructuras de Datos

Requisitos de Instalación:
    pip install streamlit networkx matplotlib numpy

Para Ejecutar:
    streamlit run app.py
"""

import time
import random
from typing import List, Dict, Tuple, Optional, Set
import streamlit as st
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Laberinto Inteligente Web",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# ESTILOS CUSTOMIZADOS (Aesthetics & Premium Design)
# =====================================================================
st.markdown("""
    <style>
        /* Tipografía y fondo principal */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        /* Contenedores tipo tarjeta */
        .metric-card {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 15px 20px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: #1E88E5;
            margin: 5px 0;
        }
        
        .metric-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #B0BEC5;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Título del panel lateral */
        .sidebar-title {
            font-size: 1.4rem;
            font-weight: 800;
            background: linear-gradient(45deg, #1E88E5, #00E676);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# MÓDULO B: GENERACIÓN DEL LABERINTO (ALGORITMO DE GRAFOS)
# =====================================================================

def generar_laberinto_dfs(N: int, seed: Optional[int] = None) -> nx.Graph:
    """
    Genera un laberinto perfecto utilizando el algoritmo de DFS con Backtracking.
    Representa el laberinto como un grafo de NetworkX donde los nodos son las celdas (x, y)
    y las aristas representan la ausencia de paredes.

    Args:
        N: Tamaño del laberinto (N x N).
        seed: Semilla opcional para reproducibilidad.

    Returns:
        nx.Graph: Grafo no dirigido con el laberinto generado.
    """
    if seed is not None:
        random.seed(seed)
        
    G = nx.Graph()
    # Agregar todos los nodos correspondientes a las celdas
    for x in range(N):
        for y in range(N):
            G.add_node((x, y))
            
    visited: Set[Tuple[int, int]] = set()
    stack: List[Tuple[int, int]] = []
    
    # Comenzar desde la esquina superior izquierda
    start_cell = (0, 0)
    visited.add(start_cell)
    current = start_cell
    
    while len(visited) < N * N:
        x, y = current
        # Buscar vecinos ortogonales no visitados
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx_val, ny_val = x + dx, y + dy
            if 0 <= nx_val < N and 0 <= ny_val < N:
                neighbor = (nx_val, ny_val)
                if neighbor not in visited:
                    neighbors.append(neighbor)
                    
        if neighbors:
            # Elegir un vecino no visitado aleatoriamente
            next_cell = random.choice(neighbors)
            # Agregar la celda actual al stack para backtracking
            stack.append(current)
            # Romper la pared: añadir arista entre 'current' y 'next_cell'
            G.add_edge(current, next_cell)
            # Marcar la nueva celda como visitada y hacerla la actual
            visited.add(next_cell)
            current = next_cell
        elif stack:
            # Backtrack si no hay vecinos disponibles
            current = stack.pop()
        else:
            break
            
    return G


# =====================================================================
# MÓDULO C: BUSCADORES DE CAMINOS (SOLUCIÓN)
# =====================================================================

def resolver_bfs(
    G: nx.Graph,
    start: Tuple[int, int],
    end: Tuple[int, int]
) -> Tuple[Optional[List[Tuple[int, int]]], List[Tuple[int, int]]]:
    """
    Resuelve el laberinto utilizando Búsqueda en Anchura (BFS).
    Explora nivel por nivel y garantiza encontrar el camino más corto.

    Args:
        G: Grafo del laberinto.
        start: Nodo de inicio (0, 0).
        end: Nodo de fin (N-1, N-1).

    Returns:
        Tuple[List[Tuple], List[Tuple]]: 
            - Lista de nodos del camino solución (o None si no hay camino).
            - Lista ordenada de todos los nodos explorados durante la búsqueda.
    """
    from collections import deque
    
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    explored_order = []
    
    while queue:
        curr = queue.popleft()
        explored_order.append(curr)
        
        if curr == end:
            break
            
        for neighbor in G.neighbors(curr):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                queue.append(neighbor)
                
    if end not in parent:
        return None, explored_order
        
    # Reconstruir la ruta ganadora
    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    
    return path, explored_order


def resolver_dfs(
    G: nx.Graph,
    start: Tuple[int, int],
    end: Tuple[int, int]
) -> Tuple[Optional[List[Tuple[int, int]]], List[Tuple[int, int]]]:
    """
    Resuelve el laberinto utilizando Búsqueda en Profundidad (DFS).
    Explora lo más profundo posible antes de realizar backtracking.

    Args:
        G: Grafo del laberinto.
        start: Nodo de inicio (0, 0).
        end: Nodo de fin (N-1, N-1).

    Returns:
        Tuple[List[Tuple], List[Tuple]]: 
            - Lista de nodos del camino solución (o None si no hay camino).
            - Lista ordenada de todos los nodos explorados durante la búsqueda.
    """
    stack = [start]
    visited = {start}
    parent = {start: None}
    explored_order = []
    
    while stack:
        curr = stack.pop()
        explored_order.append(curr)
        
        if curr == end:
            break
            
        for neighbor in G.neighbors(curr):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                stack.append(neighbor)
                
    if end not in parent:
        return None, explored_order
        
    # Reconstruir la ruta ganadora
    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    
    return path, explored_order


# =====================================================================
# MÓDULO D: VISUALIZACIÓN WEB EFICIENTE
# =====================================================================

def generar_matriz_laberinto(N: int, G: nx.Graph) -> np.ndarray:
    """
    Convierte el grafo de NetworkX en una matriz de píxeles binarios.
    Cada celda del laberinto ocupa un pixel central, y las paredes se dibujan
    en los bordes e intersecciones intermedias.
    Tamaño resultante: (2N + 1) x (2N + 1)

    Args:
        N: Tamaño del laberinto.
        G: Grafo del laberinto.

    Returns:
        np.ndarray: Matriz binaria (0: Pared, 1: Camino).
    """
    # Inicializar con todo paredes (0 = negro)
    matrix = np.zeros((2 * N + 1, 2 * N + 1), dtype=int)
    
    # Habilitar los nodos (celdas) como caminos (1 = blanco)
    for x in range(N):
        for y in range(N):
            matrix[2 * y + 1, 2 * x + 1] = 1
            
    # Habilitar los pasillos entre nodos conectados (aristas)
    for (x1, y1), (x2, y2) in G.edges():
        wall_x = x1 + x2 + 1
        wall_y = y1 + y2 + 1
        matrix[wall_y, wall_x] = 1
        
    return matrix


def dibujar_laberinto(
    N: int,
    G: nx.Graph,
    solution_path: Optional[List[Tuple[int, int]]] = None,
    explored_nodes: Optional[List[Tuple[int, int]]] = None,
    algo_type: str = "BFS"
) -> plt.Figure:
    """
    Dibuja el laberinto utilizando Matplotlib, coloreando el punto de inicio,
    el punto de fin, los nodos explorados por el buscador y la ruta solución final.

    Args:
        N: Tamaño del laberinto.
        G: Grafo del laberinto.
        solution_path: Lista de nodos que componen la ruta ganadora.
        explored_nodes: Lista de nodos explorados por el algoritmo.
        algo_type: Nombre del algoritmo ("BFS" o "DFS").

    Returns:
        plt.Figure: Objeto de figura de Matplotlib listo para renderizarse.
    """
    matrix = generar_matriz_laberinto(N, G)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    # Renderizar la matriz base (Paredes en negro, caminos libres en blanco)
    ax.imshow(matrix, cmap='gray', origin='upper')
    
    # Personalizar colores según algoritmo
    explored_color = "#FFF59D" if algo_type == "BFS" else "#FFE0B2" # Amarillo claro vs Naranja claro
    
    # 1. Dibujar celdas exploradas (si existen)
    if explored_nodes:
        solution_set = set(solution_path) if solution_path else set()
        for x, y in explored_nodes:
            # No sobreescribir visualmente el inicio, el fin ni el camino final
            if (x, y) != (0, 0) and (x, y) != (N - 1, N - 1) and (x, y) not in solution_set:
                rect = plt.Rectangle(
                    (2 * x + 0.5, 2 * y + 0.5), 1, 1,
                    facecolor=explored_color, edgecolor=None, alpha=0.7
                )
                ax.add_patch(rect)
                
    # 2. Dibujar la ruta de solución final como una línea continua de flujo
    if solution_path:
        path_x = [2 * x + 1 for x, y in solution_path]
        path_y = [2 * y + 1 for x, y in solution_path]
        ax.plot(
            path_x, path_y,
            color="#2979FF", linewidth=5, linestyle="-",
            solid_capstyle="round", solid_joinstyle="round",
            label="Ruta de Solución"
        )
        
    # 3. Dibujar marcador de Inicio (Verde) y Salida (Rojo)
    ax.plot(1, 1, marker='s', color='#00E676', markersize=14, label='Inicio (0,0)', markeredgecolor='black')
    ax.plot(2 * N - 1, 2 * N - 1, marker='s', color='#FF1744', markersize=14, label=f'Salida ({N-1},{N-1})', markeredgecolor='black')
    
    # Estilizado y limpieza de ejes del gráfico
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=3, frameon=False, fontsize=11)
    
    plt.tight_layout()
    return fig


# =====================================================================
# MÓDULO D: ORQUESTADOR PRINCIPAL (STREAMLIT APP)
# =====================================================================

def main():
    # Banner Principal de Título
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🧩 Laberinto Inteligente Web</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #78909C;'>Generación procedimental y resolución de laberintos perfectos utilizando Teoría de Grafos</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Inicializar estado en Streamlit
    if "grid_size" not in st.session_state:
        st.session_state.grid_size = 20
    if "maze_graph" not in st.session_state:
        # Generar un laberinto por defecto al arrancar
        st.session_state.maze_graph = generar_laberinto_dfs(st.session_state.grid_size)
    if "solution_path" not in st.session_state:
        st.session_state.solution_path = None
    if "explored_nodes" not in st.session_state:
        st.session_state.explored_nodes = None
    if "metrics" not in st.session_state:
        st.session_state.metrics = None
        
    # Panel Lateral (Sidebar)
    st.sidebar.markdown("<div class='sidebar-title'>Panel de Control</div>", unsafe_allow_html=True)
    
    # Selector de tamaño del laberinto
    size = st.sidebar.slider(
        "Tamaño de Cuadrícula (N x N)",
        min_value=10,
        max_value=30,
        value=st.session_state.grid_size,
        step=1
    )
    
    # Si el usuario cambia el tamaño, reseteamos el laberinto generado
    if size != st.session_state.grid_size:
        st.session_state.grid_size = size
        st.session_state.maze_graph = generar_laberinto_dfs(size)
        st.session_state.solution_path = None
        st.session_state.explored_nodes = None
        st.session_state.metrics = None
        
    # Selector de Algoritmo
    algo = st.sidebar.selectbox(
        "Algoritmo de Solución",
        options=["BFS (Breadth-First Search)", "DFS (Depth-First Search)"]
    )
    
    st.sidebar.write("---")
    
    # Controles de Acción
    col_btn1, col_btn2 = st.sidebar.columns(2)
    
    with col_btn1:
        if st.button("🔄 Nuevo Laberinto", use_container_width=True):
            st.session_state.maze_graph = generar_laberinto_dfs(size)
            st.session_state.solution_path = None
            st.session_state.explored_nodes = None
            st.session_state.metrics = None
            st.rerun()
            
    with col_btn2:
        if st.button("🚀 Resolver", type="primary", use_container_width=True):
            start_time = time.perf_counter()
            
            # Definir inicio y fin
            inicio = (0, 0)
            fin = (size - 1, size - 1)
            
            # Ejecutar algoritmo seleccionado
            if "BFS" in algo:
                path, explored = resolver_bfs(st.session_state.maze_graph, inicio, fin)
                algo_name = "BFS"
            else:
                path, explored = resolver_dfs(st.session_state.maze_graph, inicio, fin)
                algo_name = "DFS"
                
            elapsed_time = (time.perf_counter() - start_time) * 1000  # En milisegundos
            
            # Guardar soluciones en estado
            st.session_state.solution_path = path
            st.session_state.explored_nodes = explored
            st.session_state.metrics = {
                "length": len(path) if path else 0,
                "explored": len(explored),
                "time": elapsed_time,
                "algo": algo_name
            }
            st.rerun()
            
    # Sección informativa en el Panel Lateral
    st.sidebar.write("")
    with st.sidebar.expander("ℹ️ Teoría de Grafos y Algoritmos", expanded=True):
        st.markdown("""
        **Representación en Grafos:**
        - **Celdas:** Cada coordenada `(x, y)` es un **nodo**.
        - **Paredes:** Si existe una **arista** entre dos nodos adyacentes, el muro ha sido removido y el camino está abierto.
        
        **Algoritmos:**
        - **BFS (Breadth-First Search):** Garantiza encontrar el camino más corto (menor número de celdas). Explora de manera expansiva, nivel por nivel (cola FIFO).
        - **DFS (Depth-First Search):** Explora de forma profunda antes de retroceder (pila LIFO). En laberintos con múltiples caminos puede ser ineficiente, pero en un laberinto perfecto (sin ciclos) llegará a la misma solución única explorando un conjunto de nodos diferente.
        """)
        
    # Layout Principal: Panel de Métricas y Lienzo del Laberinto
    col_plot, col_info = st.columns([2.5, 1])
    
    with col_plot:
        # Renderizado gráfico del Laberinto
        algo_name_drawn = st.session_state.metrics["algo"] if st.session_state.metrics else "BFS"
        fig = dibujar_laberinto(
            N=st.session_state.grid_size,
            G=st.session_state.maze_graph,
            solution_path=st.session_state.solution_path,
            explored_nodes=st.session_state.explored_nodes,
            algo_type=algo_name_drawn
        )
        st.pyplot(fig)
        
    with col_info:
        st.markdown("<h3 style='color: #1E88E5;'>Estadísticas de Búsqueda</h3>", unsafe_allow_html=True)
        st.write("Presiona **Resolver** en la barra lateral para ver los resultados de los algoritmos de búsqueda sobre la estructura de grafo actual.")
        
        if st.session_state.metrics:
            m = st.session_state.metrics
            
            # Mostrar métricas en formato de tarjetas CSS
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 10px;">
                    <div class="metric-card">
                        <div class="metric-title">Algoritmo Ejecutado</div>
                        <div class="metric-value" style="color: #00E676;">{m['algo']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Celdas en la Solución</div>
                        <div class="metric-value">{m['length']}</div>
                        <div style="font-size: 0.85rem; color: #90A4AE;">Longitud total de la ruta verde</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Nodos Explorados</div>
                        <div class="metric-value" style="color: #FFB300;">{m['explored']}</div>
                        <div style="font-size: 0.85rem; color: #90A4AE;">Celdas de la cuadrícula visitadas</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-title">Tiempo de Cómputo</div>
                        <div class="metric-value" style="color: #2979FF;">{m['time']:.2f} ms</div>
                        <div style="font-size: 0.85rem; color: #90A4AE;">Tiempo tomado en resolver el grafo</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Comparativa teórica según resultados
            st.write("")
            st.info(
                f"El resolvedor {m['algo']} exploró el {((m['explored'] / (size*size)) * 100):.1f}% del espacio de búsqueda total para encontrar el camino de salida."
            )
        else:
            # Estado inicial sin resolver
            st.markdown("""
                <div style="text-align: center; padding: 40px 20px; border: 2px dashed rgba(255,255,255,0.15); border-radius: 12px; margin-top: 10px;">
                    <p style="font-size: 1.2rem; color: #90A4AE;">Esperando Solución...</p>
                    <p style="font-size: 0.85rem; color: #78909C;">Seleccione un algoritmo en la barra lateral y haga clic en <b>Resolver</b></p>
                </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
