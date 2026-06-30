# -*- coding: utf-8 -*-

import time
from app.model.maze import Maze
from app.services.generators import DFSGenerator, PrimGenerator, KruskalGenerator
from app.services.solvers import BFSSolver, DFSSolver, AStarSolver

class MazeController:
    """
    Clase MazeController
    --------------------
    Controlador central de la aplicación. Orquesta los procesos de creación
    y resolución de laberintos. Valida las peticiones recibidas del frontend,
    selecciona las estrategias algorítmicas adecuadas, calcula estadísticas de
    ejecución y formatea los datos resultantes en estructuras JSON compatibles.
    """

    # Diccionario de mapeo de algoritmos de generación
    GENERATORS = {
        'dfs': DFSGenerator,
        'prim': PrimGenerator,
        'kruskal': KruskalGenerator
    }

    # Diccionario de mapeo de algoritmos de resolución
    SOLVERS = {
        'bfs': BFSSolver,
        'dfs': DFSSolver,
        'astar': AStarSolver
    }

    @classmethod
    def generate_maze(cls, cols: int, rows: int, algorithm: str) -> tuple:
        """
        Orquesta la generación de un laberinto en base a las dimensiones y algoritmo dados.
        
        Parámetros:
            cols (int): Columnas del laberinto.
            rows (int): Filas del laberinto.
            algorithm (str): Código del algoritmo ('dfs', 'prim', 'kruskal').
            
        Retorna:
            tuple: (dict_respuesta, status_code)
        """
        # Validación de rango de tamaño
        if cols <= 0 or rows <= 0:
            return {'error': 'El ancho y el alto del laberinto deben ser números mayores que cero.'}, 400
        if cols > 100 or rows > 100:
            return {'error': 'Dimensiones del laberinto limitadas a un máximo de 100x100 por estabilidad del navegador.'}, 400

        # Validación del algoritmo
        generator_class = cls.GENERATORS.get(algorithm.lower())
        if not generator_class:
            return {'error': f"El algoritmo de generación '{algorithm}' no es soportado por el sistema."}, 400

        try:
            # Instanciar modelo de laberinto
            maze = Maze(cols, rows)
            
            # Medir tiempo de ejecución en milisegundos con alta precisión
            start_time = time.perf_counter()
            generator_class.generate(maze)
            end_time = time.perf_counter()
            
            elapsed_ms = (end_time - start_time) * 1000

            response = {
                'maze': maze.to_dict(),
                'stats': {
                    'generation_time_ms': round(elapsed_ms, 3)
                }
            }
            return response, 200

        except Exception as e:
            return {'error': f'Error interno durante el proceso de generación: {str(e)}'}, 500

    @classmethod
    def solve_maze(cls, maze_data: dict, algorithm: str) -> tuple:
        """
        Orquesta la resolución del laberinto provisto en formato de diccionario.
        
        Parámetros:
            maze_data (dict): Diccionario que contiene la estructura serializada del laberinto.
            algorithm (str): Algoritmo de resolución a emplear ('bfs', 'dfs', 'astar').
            
        Retorna:
            tuple: (dict_respuesta, status_code)
        """
        # Validación del algoritmo de resolución
        solver_class = cls.SOLVERS.get(algorithm.lower())
        if not solver_class:
            return {'error': f"El algoritmo de resolución '{algorithm}' no es soportado por el sistema."}, 400

        if not maze_data or 'grid' not in maze_data:
            return {'error': 'La estructura de datos del laberinto proporcionada es inválida o está vacía.'}, 400

        try:
            # Reconstruir el objeto Maze desde la representación JSON
            maze = Maze.from_dict(maze_data)
            
            # Medir tiempo de resolución
            start_time = time.perf_counter()
            path, explored = solver_class.solve(maze)
            end_time = time.perf_counter()
            
            elapsed_ms = (end_time - start_time) * 1000

            # Caso en el que no exista camino factible (manejo de errores de laberinto sin solución)
            if not path:
                return {
                    'error': 'El laberinto no tiene una solución viable (inicio inaccesible al fin).',
                    'path': [],
                    'explored': explored,
                    'stats': {
                        'solve_time_ms': round(elapsed_ms, 3),
                        'visited_nodes': len(explored),
                        'path_length': 0
                    }
                }, 200

            response = {
                'path': path,
                'explored': explored,
                'stats': {
                    'solve_time_ms': round(elapsed_ms, 3),
                    'visited_nodes': len(explored),
                    'path_length': len(path)
                }
            }
            return response, 200

        except Exception as e:
            return {'error': f'Error interno durante el proceso de resolución: {str(e)}'}, 500
