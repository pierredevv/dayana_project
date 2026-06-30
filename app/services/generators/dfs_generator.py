# -*- coding: utf-8 -*-

import random
from app.model.maze import Maze

class DFSGenerator:
    """
    Clase DFSGenerator
    ------------------
    Genera un laberinto perfecto utilizando el algoritmo Depth-First Search (DFS) con Backtracking.
    Un laberinto perfecto no contiene ciclos y tiene exactamente un único camino válido entre cualquier par de celdas.
    
    Implementa un enfoque iterativo mediante una pila (stack) explícita, evitando desbordamientos de la pila de llamadas
    de Python (recursion limit) para tamaños de cuadrículas grandes.
    
    Complejidad Temporal: O(V + E) = O(N), donde N es el número total de celdas (N = cols * rows). Cada celda es visitada
                         y procesada un número constante de veces.
    Complejidad Espacial: O(V) = O(N) para la pila de backtracking y el rastreo de visitados.
    """

    @staticmethod
    def generate(maze: Maze):
        """
        Modifica el laberinto proporcionado (objeto Maze) derribando paredes para crear
        un laberinto perfecto utilizando el recorrido DFS iterativo.
        
        Parámetros:
            maze (Maze): Instancia del laberinto a generar.
        """
        # Aseguramos un estado limpio de visitas
        maze.reset_visited()
        
        # Pila de backtracking
        stack = []
        
        # Celda inicial (esquina superior izquierda por defecto)
        current = maze.get_start_cell()
        current.visited = True
        
        total_cells = maze.cols * maze.rows
        visited_count = 1
        
        while visited_count < total_cells:
            # Obtener vecinos de la celda actual que no han sido visitados
            unvisited_neighbors = maze.get_unvisited_neighbors(current)
            
            if unvisited_neighbors:
                # Seleccionar un vecino no visitado al azar
                neighbor, _ = random.choice(unvisited_neighbors)
                
                # Derribar las paredes intermedias entre el actual y el vecino
                maze.remove_walls_between(current, neighbor)
                
                # Apilar la celda actual para futuros retornos
                stack.append(current)
                
                # Mover el puntero a la celda elegida y marcarla como visitada
                current = neighbor
                current.visited = True
                visited_count += 1
            elif stack:
                # Si no hay vecinos disponibles, retroceder (pop de la pila)
                current = stack.pop()
            else:
                # Salvaguarda en caso de anomalía estructural
                break
                
        # Limpiar el estado de visitados para posteriores llamadas o resoluciones
        maze.reset_visited()
