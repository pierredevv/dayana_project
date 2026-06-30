# -*- coding: utf-8 -*-

import heapq
from app.model.maze import Maze

class AStarSolver:
    """
    Clase AStarSolver
    -----------------
    Resuelve el laberinto utilizando el algoritmo de búsqueda heurística A* (A-Estrella).
    Utiliza la distancia Manhattan como función heurística admisible, lo que asegura que
    el algoritmo encontrará el camino más corto de forma más eficiente (explorando menos nodos)
    que BFS en la mayoría de los casos.
    
    Función de evaluación: f(n) = g(n) + h(n)
        - g(n): Costo real acumulado desde el inicio hasta el nodo n (1 por celda).
        - h(n): Estimación heurística del costo desde n hasta el destino (distancia Manhattan).
        
    Complejidad Temporal: O(E log V) = O(N log N) con N = cols * rows, debido a las operaciones
                         de inserción y extracción en la cola de prioridad (min-heap).
    Complejidad Espacial: O(V) = O(N) para las estructuras del heap, de costos (g_score) y padres.
    """

    @staticmethod
    def solve(maze: Maze) -> tuple:
        """
        Busca el camino solución desde la celda de inicio hasta la de fin utilizando el algoritmo A*.
        
        Parámetros:
            maze (Maze): El laberinto a resolver.
            
        Retorna:
            tuple: (path, explored)
                - path (list): Lista de diccionarios {'x': x, 'y': y} con el camino óptimo.
                - explored (list): Lista de diccionarios {'x': x, 'y': y} con el orden de celdas visitadas.
        """
        start = maze.get_start_cell()
        end = maze.get_end_cell()
        
        if not start or not end:
            return [], []
            
        # Función heurística: Distancia Manhattan entre la celda actual y la de destino
        def get_manhattan_distance(cell_a, cell_b) -> int:
            return abs(cell_a.x - cell_b.x) + abs(cell_a.y - cell_b.y)
            
        # Cola de prioridad (min-heap): almacena tuplas (f_score, counter, cell)
        # El contador 'counter' evita colisiones en el ordenamiento si los f_score coinciden,
        # previniendo que Python intente comparar directamente los objetos Cell.
        open_set = []
        counter = 0
        heapq.heappush(open_set, (get_manhattan_distance(start, end), counter, start))
        
        # Tabla de costos mínimos g(n)
        g_score = {start: 0}
        
        parent = {}
        explored = []
        visited = set()
        
        found = False
        
        while open_set:
            # Extraer la celda con el menor f_score
            f, _, current = heapq.heappop(open_set)
            
            # Si ya se procesó de forma definitiva esta celda, se ignora (evita duplicados en el heap)
            if current in visited:
                continue
                
            visited.add(current)
            explored.append({'x': current.x, 'y': current.y})
            
            # Condición de parada al llegar al destino
            if current == end:
                found = True
                break
                
            # Evaluar vecinos transitables
            for neighbor, direction in maze.get_neighbors(current):
                if not current.walls[direction]:
                    # El costo de moverse a cualquier celda adyacente es 1
                    tentative_g = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        g_score[neighbor] = tentative_g
                        parent[neighbor] = current
                        counter += 1
                        
                        f_score = tentative_g + get_manhattan_distance(neighbor, end)
                        heapq.heappush(open_set, (f_score, counter, neighbor))
                        
        # Reconstruir la ruta
        path = []
        if found:
            current_path_node = end
            while current_path_node:
                path.append({'x': current_path_node.x, 'y': current_path_node.y})
                current_path_node = parent.get(current_path_node)
            path.reverse()
            
        return path, explored
