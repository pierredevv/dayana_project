# -*- coding: utf-8 -*-

import random
from app.model.maze import Maze
from app.services.union_find import UnionFind

class KruskalGenerator:
    """
    Clase KruskalGenerator
    ----------------------
    Genera un laberinto perfecto basándose en el algoritmo de Kruskal para la construcción de
    un Árbol de Expansión Mínima (Minimum Spanning Tree - MST) sobre la cuadrícula del grafo.
    
    El flujo del algoritmo es:
    1. Tratar cada celda del laberinto como un subconjunto disjunto propio.
    2. Crear una lista de todas las paredes internas del laberinto.
    3. Mezclar aleatoriamente las paredes.
    4. Para cada pared de la lista:
       a. Determinar las dos celdas que divide la pared.
       b. Si las celdas se encuentran en conjuntos disjuntos (utilizando Union-Find):
          i. Derribar la pared que las separa.
          ii. Unir los dos conjuntos.
       c. Si ya pertenecen al mismo conjunto, omitir la pared para evitar ciclos.
       
    Complejidad Temporal: O(E log V) = O(N log N) con N = cols * rows, debido al ordenamiento/barajado inicial
                         de las aristas (paredes), y operaciones en UnionFind casi constantes O(alpha(N)).
    Complejidad Espacial: O(V) = O(N) para la estructura Disjoint-Set.
    """

    @staticmethod
    def generate(maze: Maze):
        """
        Modifica el laberinto proporcionado (objeto Maze) derribando paredes para crear
        un laberinto perfecto utilizando el algoritmo de Kruskal aleatorizado.
        
        Parámetros:
            maze (Maze): Instancia del laberinto a generar.
        """
        cols = maze.cols
        rows = maze.rows
        
        # Inicializar la estructura UnionFind con capacidad para todas las celdas
        uf = UnionFind(cols * rows)
        
        # Almacenaremos las paredes internas en forma de tuplas: (x1, y1, x2, y2)
        walls = []
        for y in range(rows):
            for x in range(cols):
                # Pared Este (adyacente a la derecha)
                if x < cols - 1:
                    walls.append((x, y, x + 1, y))
                # Pared Sur (adyacente hacia abajo)
                if y < rows - 1:
                    walls.append((x, y, x, y + 1))
                    
        # Mezclar aleatoriamente las paredes
        random.shuffle(walls)
        
        # Iterar por cada pared e intentar realizar la unión
        for x1, y1, x2, y2 in walls:
            # Obtener índices lineales únicos para Union-Find
            idx1 = y1 * cols + x1
            idx2 = y2 * cols + x2
            
            # Comprobar si pertenecen a componentes disjuntos y unirlos
            if uf.union(idx1, idx2):
                cell1 = maze.get_cell(x1, y1)
                cell2 = maze.get_cell(x2, y2)
                
                # Derribar la pared común
                maze.remove_walls_between(cell1, cell2)
                
        # Limpiar el estado de visitados por seguridad
        maze.reset_visited()
