# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, jsonify
from app.controller.maze_controller import MazeController

# Definir el Blueprint para las rutas asociadas al laberinto
maze_bp = Blueprint('maze', __name__)

@maze_bp.route('/')
def index():
    """
    Ruta raíz. Renderiza e inicia la interfaz de usuario en el frontend.
    """
    return render_template('index.html')

@maze_bp.route('/api/generate', methods=['POST'])
def generate():
    """
    Endpoint de la API REST para generar un laberinto.
    Espera un JSON con la estructura:
    {
        "cols": int,
        "rows": int,
        "algorithm": str
    }
    """
    data = request.get_json() or {}
    
    cols = data.get('cols')
    rows = data.get('rows')
    algorithm = data.get('algorithm', 'dfs')
    
    # Validación básica de tipos en las variables recibidas
    try:
        if cols is None or rows is None:
            return jsonify({'error': 'Los parámetros "cols" (columnas) y "rows" (filas) son obligatorios.'}), 400
        cols = int(cols)
        rows = int(rows)
    except (ValueError, TypeError):
        return jsonify({'error': 'Los parámetros de dimensiones del laberinto deben ser números enteros válidos.'}), 400
        
    response, status_code = MazeController.generate_maze(cols, rows, algorithm)
    return jsonify(response), status_code

@maze_bp.route('/api/solve', methods=['POST'])
def solve():
    """
    Endpoint de la API REST para resolver un laberinto existente.
    Espera un JSON con la estructura:
    {
        "maze": dict,  # Datos serializados del laberinto
        "algorithm": str
    }
    """
    data = request.get_json() or {}
    
    maze_data = data.get('maze')
    algorithm = data.get('algorithm')
    
    if not maze_data:
        return jsonify({'error': 'El parámetro "maze" con los datos del laberinto es obligatorio.'}), 400
    if not algorithm:
        return jsonify({'error': 'El parámetro "algorithm" indicando el método de resolución es obligatorio.'}), 400
        
    response, status_code = MazeController.solve_maze(maze_data, algorithm)
    return jsonify(response), status_code
