# -*- coding: utf-8 -*-

from app.model.maze import Maze

class DFSSolver:
    """
    Clase DFSSolver
    ---------------
    Resuelve el laberinto utilizando el algoritmo Depth-First Search (DFS) o Búsqueda en Profundidad.
    A diferencia de BFS, DFS explora una rama en profundidad lo máximo posible antes de retroceder.
    Por esta razón, en laberintos con múltiples caminos (o si no es un laberinto perfecto), no garantiza
    encontrar la ruta más corta, pero suele tener un consumo de memoria diferente y un orden de exploración lineal.
    
    Implementa un enfoque iterativo con una pila (stack) explícita.
    
    Complejidad Temporal: O(V + E) = O(N), donde N es el número total de celdas.
    Complejidad Espacial: O(V) = O(N) para la pila de búsqueda y el rastreo de visitas.
    """

    @staticmethod
    def solve(maze: Maze) -> tuple:
        """
        Busca el camino solución desde la celda de inicio hasta la de fin utilizando DFS.
        
        Parámetros:
            maze (Maze): El laberinto a resolver.
            
        Retorna:
            tuple: (path, explored)
                - path (list): Lista de diccionarios {'x': x, 'y': y} de inicio a fin.
                - explored (list): Lista de diccionarios {'x': x, 'y': y} en el orden de exploración (extraídos de la pila).
        """
        start = maze.get_start_cell()
        end = maze.get_end_cell()
        
        if not start or not end:
            return [], []
            
        stack = [start]
        visited = {start}
        explored = []
        parent = {}
        
        found = False
        
        while stack:
            current = stack.pop()
            explored.append({'x': current.x, 'y': current.y})
            
            # Condición de parada al llegar al destino
            if current == end:
                found = True
                break
                
            # Evaluar vecinos
            for neighbor, direction in maze.get_neighbors(current):
                # Si no hay pared entre la celda actual y la vecina
                if not current.walls[direction]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        parent[neighbor] = current
                        stack.append(neighbor)
                        
        # Reconstruir la ruta
        path = []
        if found:
            current_path_node = end
            while current_path_node:
                path.append({'x': current_path_node.x, 'y': current_path_node.y})
                current_path_node = parent.get(current_path_node)
            path.reverse()
            
        return path, explored
