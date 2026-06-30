# -*- coding: utf-8 -*-

from collections import deque
from app.model.maze import Maze

class BFSSolver:
    """
    Clase BFSSolver
    ---------------
    Resuelve el laberinto utilizando el algoritmo Breadth-First Search (BFS) o Búsqueda en Anchura.
    BFS explora exhaustivamente el espacio de estados nivel por nivel, lo que garantiza encontrar
    el camino más corto (menor número de pasos) en grafos no ponderados.
    
    Complejidad Temporal: O(V + E) = O(N), donde N es el número total de celdas (N = cols * rows),
                         ya que visita cada celda y evalúa cada pared en el peor de los casos una sola vez.
    Complejidad Espacial: O(V) = O(N) para mantener la cola de nodos y las celdas exploradas.
    """

    @staticmethod
    def solve(maze: Maze) -> tuple:
        """
        Busca el camino solución desde la celda de inicio hasta la de fin.
        
        Parámetros:
            maze (Maze): El laberinto a resolver.
            
        Retorna:
            tuple: (path, explored)
                - path (list): Lista de diccionarios {'x': x, 'y': y} en orden de inicio a fin (o vacía si no hay solución).
                - explored (list): Lista de diccionarios {'x': x, 'y': y} en el orden en que fueron extraídos de la cola.
        """
        start = maze.get_start_cell()
        end = maze.get_end_cell()
        
        if not start or not end:
            return [], []
            
        queue = deque([start])
        visited = {start}
        explored = []
        parent = {}
        
        found = False
        
        while queue:
            current = queue.popleft()
            explored.append({'x': current.x, 'y': current.y})
            
            # Condición de parada al llegar al destino
            if current == end:
                found = True
                break
                
            # Evaluar vecinos ortogonales
            for neighbor, direction in maze.get_neighbors(current):
                # Validar si el pasillo está libre (sin pared)
                if not current.walls[direction]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        parent[neighbor] = current
                        queue.append(neighbor)
                        
        # Reconstruir el camino si se encontró solución
        path = []
        if found:
            current_path_node = end
            while current_path_node:
                path.append({'x': current_path_node.x, 'y': current_path_node.y})
                current_path_node = parent.get(current_path_node)
            path.reverse()  # Voltear para ir de inicio a fin
            
        return path, explored
