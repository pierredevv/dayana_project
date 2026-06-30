# -*- coding: utf-8 -*-

from app.model.grid import Grid

class Maze(Grid):
    """
    Clase Maze
    ----------
    Hereda de la clase Grid. Modela el laberinto completo agregando la definición
    del punto de inicio (start) y el punto final (end) del camino. Proporciona además
    métodos de serialización específicos para la comunicación con la API.
    
    Atributos:
        cols (int): Número de columnas del laberinto.
        rows (int): Número de filas del laberinto.
        start_x (int): Coordenada X (columna) del punto de inicio.
        start_y (int): Coordenada Y (fila) del punto de inicio.
        end_x (int): Coordenada X (columna) del punto final.
        end_y (int): Coordenada Y (fila) del punto final.
    """

    def __init__(self, cols: int, rows: int, start_x: int = 0, start_y: int = 0, end_x: int = None, end_y: int = None):
        """
        Inicializa un laberinto con sus dimensiones y define los puntos de inicio y fin.
        Por defecto, el inicio es la esquina superior izquierda (0, 0) y el fin la esquina
        inferior derecha (cols - 1, rows - 1).
        
        Complejidad Temporal: O(rows * cols) debido a la inicialización de Grid.
        Complejidad Espacial: O(rows * cols)
        """
        super().__init__(cols, rows)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x if end_x is not None else cols - 1
        self.end_y = end_y if end_y is not None else rows - 1

    def get_start_cell(self):
        """Retorna la celda de inicio del laberinto."""
        return self.get_cell(self.start_x, self.start_y)

    def get_end_cell(self):
        """Retorna la celda de destino del laberinto."""
        return self.get_cell(self.end_x, self.end_y)

    def to_dict(self) -> dict:
        """
        Serializa el estado del laberinto a un diccionario estructurado para transferirse vía JSON.
        
        Complejidad Temporal: O(rows * cols)
        Complejidad Espacial: O(rows * cols) para la representación en diccionario.
        """
        return {
            'cols': self.cols,
            'rows': self.rows,
            'start': {'x': self.start_x, 'y': self.start_y},
            'end': {'x': self.end_x, 'y': self.end_y},
            'grid': self.to_list()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Maze':
        """
        Reconstruye una instancia de Maze a partir de un diccionario (por ejemplo, para resolver
        un laberinto enviado desde el frontend).
        
        Complejidad Temporal: O(rows * cols)
        Complejidad Espacial: O(rows * cols)
        """
        cols = data['cols']
        rows = data['rows']
        start = data['start']
        end = data['end']
        grid_data = data['grid']
        
        maze = cls(cols, rows, start['x'], start['y'], end['x'], end['y'])
        
        for y in range(rows):
            for x in range(cols):
                cell = maze.get_cell(x, y)
                cell_data = grid_data[y][x]
                cell.walls = cell_data['walls'].copy()
                cell.visited = cell_data.get('visited', False)
                
        return maze
