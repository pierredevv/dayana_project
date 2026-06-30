# -*- coding: utf-8 -*-

import random
from app.model.maze import Maze

class PrimGenerator:
    """
    Clase PrimGenerator
    -------------------
    Genera un laberinto perfecto basado en el algoritmo de Prim simplificado para laberintos aleatorios.
    A diferencia de DFS, este algoritmo genera laberintos con pasillos más cortos y ramificaciones más frecuentes.
    
    El flujo del algoritmo es:
    1. Iniciar con todas las celdas marcadas como no visitadas (con todas sus paredes intactas).
    2. Elegir una celda inicial al azar, marcarla como visitada (dentro del laberinto).
    3. Añadir todos sus vecinos no visitados a un conjunto de "celdas frontera".
    4. Mientras queden celdas frontera:
       a. Seleccionar una celda frontera al azar.
       b. Encontrar sus vecinos que ya pertenecen al laberinto (visitados).
       c. Elegir un vecino visitado al azar y derribar la pared que los separa.
       d. Marcar la celda frontera como visitada (añadirla al laberinto).
       e. Añadir sus propios vecinos no visitados al conjunto de frontera.
       f. Retirar la celda procesada del conjunto de frontera.
       
    Complejidad Temporal: O(V log V) o simplificado O(N), donde N es el número total de celdas (N = cols * rows),
                         ya que cada celda entra y sale del conjunto de frontera exactamente una vez.
    Complejidad Espacial: O(V) = O(N) para almacenar las referencias del conjunto frontera y estados de visita.
    """

    @staticmethod
    def generate(maze: Maze):
        """
        Modifica el laberinto proporcionado (objeto Maze) derribando paredes para crear
        un laberinto perfecto utilizando el algoritmo de Prim aleatorio.
        
        Parámetros:
            maze (Maze): Instancia del laberinto a generar.
        """
        maze.reset_visited()
        
        # Conjunto de celdas frontera (celdas no visitadas adyacentes a celdas visitadas)
        frontier = set()
        
        # Seleccionar celda inicial (esquina superior izquierda por simplicidad)
        start = maze.get_start_cell()
        start.visited = True
        
        # Agregar los vecinos del inicio a la frontera
        for neighbor, _ in maze.get_neighbors(start):
            frontier.add(neighbor)
            
        while frontier:
            # Elegir una celda frontera al azar
            cell = random.choice(list(frontier))
            
            # Buscar sus vecinos que ya formen parte del laberinto (visitados)
            visited_neighbors = [n for n, _ in maze.get_neighbors(cell) if n.visited]
            
            if visited_neighbors:
                # Elegir un vecino visitado de forma aleatoria
                chosen_neighbor = random.choice(visited_neighbors)
                
                # Conectar la celda frontera con la celda elegida eliminando la pared
                maze.remove_walls_between(cell, chosen_neighbor)
                
            # Integrar la celda frontera al laberinto
            cell.visited = True
            
            # Agregar los vecinos no visitados de la celda procesada a la frontera
            for neighbor, _ in maze.get_neighbors(cell):
                if not neighbor.visited:
                    frontier.add(neighbor)
                    
            # Eliminar la celda del conjunto de frontera
            frontier.remove(cell)
            
        # Restablecer el estado de visitas para no interferir con el resolvedor
        maze.reset_visited()
