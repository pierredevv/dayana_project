# -*- coding: utf-8 -*-

class Cell:
    """
    Clase Cell
    ----------
    Representa una celda individual en la cuadrícula del laberinto (un nodo del grafo).
    Cada celda tiene coordenadas (x, y), un estado de paredes (Norte, Sur, Este, Oeste)
    y un estado de 'visitado' para facilitar el rastreo en los algoritmos de generación
    y resolución de laberintos.
    
    Atributos:
        x (int): Coordenada en el eje horizontal (columna).
        y (int): Coordenada en el eje vertical (fila).
        walls (dict): Estado de las cuatro paredes de la celda (True si existe pared, False si está derribada).
        visited (bool): Estado de visita de la celda durante los recorridos.
    """

    def __init__(self, x: int, y: int):
        """
        Inicializa una nueva celda en la posición (x, y) con todas sus paredes activas.
        
        Complejidad Temporal: O(1)
        Complejidad Espacial: O(1)
        """
        self.x = x
        self.y = y
        self.walls = {
            'N': True,  # Norte (arriba)
            'S': True,  # Sur (abajo)
            'E': True,  # Este (derecha)
            'W': True   # Oeste (izquierda)
        }
        self.visited = False

    def remove_wall(self, direction: str):
        """
        Derriba la pared en la dirección indicada ('N', 'S', 'E', 'W').
        
        Complejidad Temporal: O(1)
        Complejidad Espacial: O(1)
        """
        if direction in self.walls:
            self.walls[direction] = False

    def add_wall(self, direction: str):
        """
        Levanta la pared en la dirección indicada.
        
        Complejidad Temporal: O(1)
        Complejidad Espacial: O(1)
        """
        if direction in self.walls:
            self.walls[direction] = True

    def reset(self):
        """
        Reinicia el estado de visita de la celda.
        
        Complejidad Temporal: O(1)
        Complejidad Espacial: O(1)
        """
        self.visited = False

    def to_dict(self) -> dict:
        """
        Convierte el estado de la celda a un diccionario serializable para la API JSON.
        
        Complejidad Temporal: O(1)
        Complejidad Espacial: O(1)
        """
        return {
            'x': self.x,
            'y': self.y,
            'walls': self.walls,
            'visited': self.visited
        }
