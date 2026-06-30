# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple
from app.model.cell import Cell

class Grid:
    """
    Clase Grid
    ----------
    Representa la cuadrícula o matriz bidimensional de celdas que compone el laberinto.
    Maneja la inicialización de nodos, indexación de coordenadas, localización de
    células vecinas y la eliminación de paredes entre celdas adyacentes.
    
    Atributos:
        cols (int): Número de columnas de la cuadrícula.
        rows (int): Número de filas de la cuadrícula.
        grid (List[List[Cell]]): Matriz 2D conteniendo objetos de la clase Cell.
    """

    def __init__(self, cols: int, rows: int):
        """
        Inicializa la cuadrícula con las dimensiones especificadas y rellena la matriz con objetos Cell.
        
        Complejidad Temporal: O(rows * cols)
        Complejidad Espacial: O(rows * cols) para almacenar las celdas.
        """
        self.cols = cols
        self.rows = rows
        self.grid = [[Cell(x, y) for x in range(cols)] for y in range(rows)]

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """
        Retorna la celda en las coordenadas (x, y) si se encuentra dentro de los límites de la cuadrícula.
        En caso contrario, retorna None.
        
        Complejidad Temporal: O(1)
        Complejidad Espacial: O(1)
        """
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[y][x]
        return None

    def get_neighbors(self, cell: Cell) -> List[Tuple[Cell, str]]:
        """
        Obtiene todos los vecinos ortogonales válidos de una celda, junto con la dirección en la que se encuentran
        respecto a la celda original ('N', 'S', 'E', 'W').
        
        Complejidad Temporal: O(1)
        Complejidad Espacial: O(1)
        """
        neighbors = []
        # Direcciones: (delta_x, delta_y, dirección)
        directions = [
            (0, -1, 'N'),  # Norte
            (0, 1, 'S'),   # Sur
            (1, 0, 'E'),   # Este
            (-1, 0, 'W')   # Oeste
        ]
        
        for dx, dy, direction in directions:
            nx, ny = cell.x + dx, cell.y + dy
            neighbor = self.get_cell(nx, ny)
            if neighbor:
                neighbors.append((neighbor, direction))
                
        return neighbors

    def get_unvisited_neighbors(self, cell: Cell) -> List[Tuple[Cell, str]]:
        """
        Obtiene los vecinos ortogonales que aún no han sido visitados (útil para generación).
        
        Complejidad Temporal: O(1)
        Complejidad Espacial: O(1)
        """
        return [(n, d) for n, d in self.get_neighbors(cell) if not n.visited]

    def remove_walls_between(self, cell_a: Cell, cell_b: Cell):
        """
        Derriba las paredes colindantes entre dos celdas adyacentes A y B.
        
        Complejidad Temporal: O(1)
        Complejidad Espacial: O(1)
        """
        dx = cell_b.x - cell_a.x
        dy = cell_b.y - cell_a.y

        if dx == 1:  # B está al Este de A
            cell_a.remove_wall('E')
            cell_b.remove_wall('W')
        elif dx == -1:  # B está al Oeste de A
            cell_a.remove_wall('W')
            cell_b.remove_wall('E')
        elif dy == 1:  # B está al Sur de A
            cell_a.remove_wall('S')
            cell_b.remove_wall('N')
        elif dy == -1:  # B está al Norte de A
            cell_a.remove_wall('N')
            cell_b.remove_wall('S')

    def reset_visited(self):
        """
        Restablece el estado de visita ('visited') de todas las celdas en la cuadrícula a False.
        
        Complejidad Temporal: O(rows * cols)
        Complejidad Espacial: O(1)
        """
        for row in self.grid:
            for cell in row:
                cell.reset()

    def to_list(self) -> List[List[dict]]:
        """
        Representa la cuadrícula como una lista bidimensional de diccionarios.
        
        Complejidad Temporal: O(rows * cols)
        Complejidad Espacial: O(rows * cols) para la estructura de retorno.
        """
        return [[cell.to_dict() for cell in row] for row in self.grid]
