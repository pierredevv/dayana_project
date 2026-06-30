# -*- coding: utf-8 -*-
"""
Proyecto de Optimización de Rutas de Entrega para Flota Logística (VRP)
Especialidad: Investigación de Operaciones y Logística

Requisitos de Instalación:
    pip install ortools networkx matplotlib numpy

Autor: Ingeniero de Software Experto y Científico de Datos
"""

import random
import math
from typing import List, Dict, Tuple, Optional
import networkx as nx
import matplotlib.pyplot as plt

# Importar OR-Tools para optimización de ruteo
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


# =====================================================================
# MÓDULO A: GENERACIÓN Y SIMULACIÓN DE DATOS
# =====================================================================

def generar_datos_simulados(
    num_clientes: int = 15,
    deposito_coords: Tuple[float, float] = (50.0, 50.0),
    capacidad_vehiculo: int = 15,
    semilla: int = 42
) -> Dict:
    """
    Genera datos sintéticos y realistas para el problema de ruteo de vehículos (VRP).

    Args:
        num_clientes: Número de clientes a simular (por defecto 15).
        deposito_coords: Coordenadas (X, Y) del depósito central (por defecto (50.0, 50.0)).
        capacidad_vehiculo: Capacidad de carga máxima por vehículo (por defecto 15).
        semilla: Semilla aleatoria para asegurar la reproducibilidad de los resultados.

    Returns:
        Dict: Un diccionario con los datos del problema:
            - 'coordinates': Dict[int, Tuple[float, float]] con las coordenadas (X, Y) de cada nodo.
            - 'demands': List[int] con la demanda de paquetes de cada nodo (nodo 0 es el depósito con demanda 0).
            - 'num_vehicles': int con el número total de vehículos en la flota.
            - 'vehicle_capacity': int con la capacidad del vehículo.
    """
    random.seed(semilla)
    
    # Coordenadas: Nodo 0 es el depósito central
    coordinates: Dict[int, Tuple[float, float]] = {0: deposito_coords}
    
    # Generar coordenadas aleatorias en plano 2D (0 a 100) para los clientes (IDs: 1 a 15)
    for i in range(1, num_clientes + 1):
        x = round(random.uniform(0.0, 100.0), 2)
        y = round(random.uniform(0.0, 100.0), 2)
        coordinates[i] = (x, y)
        
    # Demandas: Depósito tiene demanda 0. Clientes tienen demandas entre 1 y 5 unidades.
    demands: List[int] = [0]
    for _ in range(num_clientes):
        demands.append(random.randint(1, 5))
        
    # Estimar el número de vehículos necesarios para asegurar factibilidad.
    # Total de demanda / capacidad de vehículo, con un margen de seguridad.
    demanda_total = sum(demands)
    vehiculos_minimos = math.ceil(demanda_total / capacidad_vehiculo)
    # Definimos una flota de vehículos con un pequeño margen para dar flexibilidad al solver
    num_vehicles = vehiculos_minimos + 2
    
    print("[INFO] Datos simulados exitosamente.")
    print(f"       Total de Clientes: {num_clientes}")
    print(f"       Demanda Total: {demanda_total} unidades")
    print(f"       Capacidad por Vehiculo: {capacidad_vehiculo} unidades")
    print(f"       Vehiculos en Flota Disponibles: {num_vehicles}")
    
    return {
        "coordinates": coordinates,
        "demands": demands,
        "num_vehicles": num_vehicles,
        "vehicle_capacity": capacidad_vehiculo
    }


# =====================================================================
# MÓDULO B: CONSTRUCCIÓN DEL GRAFO Y MATRIZ DE DISTANCIA
# =====================================================================

def construir_grafo_y_matriz(
    coordinates: Dict[int, Tuple[float, float]]
) -> Tuple[nx.DiGraph, List[List[int]]]:
    """
    Crea el grafo del sistema usando NetworkX y calcula la matriz de distancias
    en formato de lista de listas (escalada para OR-Tools).

    Args:
        coordinates: Coordenadas de los nodos (depósito y clientes).

    Returns:
        Tuple[nx.DiGraph, List[List[int]]]:
            - El grafo dirigido (NetworkX DiGraph) con pesos de distancia euclidiana.
            - La matriz de distancias en formato lista de listas de enteros.
    """
    G = nx.DiGraph()
    num_nodos = len(coordinates)
    
    # Agregar nodos al grafo con sus coordenadas
    for node_id, coords in coordinates.items():
        G.add_node(node_id, pos=coords)
        
    # Inicializar matriz de distancias
    # OR-Tools requiere valores enteros. Para no perder precisión decimal,
    # multiplicamos las distancias euclidianas por un factor de escala de 100.
    factor_escala = 100
    distance_matrix: List[List[int]] = [[0] * num_nodos for _ in range(num_nodos)]
    
    for i in range(num_nodos):
        for j in range(num_nodos):
            if i == j:
                distance_matrix[i][j] = 0
            else:
                x1, y1 = coordinates[i]
                x2, y2 = coordinates[j]
                # Distancia euclidiana
                dist = math.hypot(x1 - x2, y1 - y2)
                
                # Guardar en matriz como entero escalado
                distance_matrix[i][j] = int(round(dist * factor_escala))
                
                # Agregar arista en el grafo con peso real (sin escalar para visualización)
                G.add_edge(i, j, weight=round(dist, 2))
                
    return G, distance_matrix


# =====================================================================
# MÓDULO C: MOTOR DE OPTIMIZACIÓN (ALGORITMO)
# =====================================================================

def resolver_vrp(
    distance_matrix: List[List[int]],
    demands: List[int],
    vehicle_capacity: int,
    num_vehicles: int,
    depot_index: int = 0
) -> Optional[Dict]:
    """
    Resuelve el Problema de Enrutamiento de Vehículos (VRP) utilizando Google OR-Tools.

    Args:
        distance_matrix: Matriz de distancias (valores enteros escalados).
        demands: Lista de demandas por nodo.
        vehicle_capacity: Capacidad máxima de carga por vehículo.
        num_vehicles: Cantidad de vehículos en la flota.
        depot_index: Índice del depósito central (normalmente 0).

    Returns:
        Optional[Dict]: Diccionario con las rutas y estadísticas de la solución,
                        o None si no se encuentra solución factible.
    """
    # 1. Crear el administrador de índices del ruteador
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        num_vehicles,
        depot_index
    )
    
    # 2. Crear el modelo de ruteo
    routing = pywrapcp.RoutingModel(manager)
    
    # 3. Registrar el callback de distancias
    def distance_callback(from_index: int, to_index: int) -> int:
        """Retorna la distancia escalada entre dos índices."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]
        
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    
    # Definir el costo de viaje (distancia) para todos los vehículos
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # 4. Registrar el callback de demandas para la restricción de capacidad
    def demand_callback(from_index: int) -> int:
        """Retorna la demanda del nodo."""
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]
        
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    
    # Agregar la restricción de capacidad (acumulado <= capacidad por vehículo)
    capacity_dimension_name = 'Capacity'
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # Capacidad de holgura (slack) = 0
        [vehicle_capacity] * num_vehicles,  # Capacidad máxima idéntica para toda la flota
        True,  # Empezar el acumulador en 0 (comienza vacío en el depósito)
        capacity_dimension_name
    )
    
    # 5. Configurar los parámetros del buscador
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    
    # Estrategia heurística inicial rápida
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    
    # Metaheurística de búsqueda local para optimización global
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    
    # Límite de tiempo estricto de 3 segundos
    search_parameters.time_limit.seconds = 3
    
    # 6. Ejecutar el solucionador
    print("[INFO] Resolviendo el modelo VRP con OR-Tools...")
    solution = routing.SolveWithParameters(search_parameters)
    
    # 7. Procesar y extraer la solución
    if not solution:
        return None
        
    routes_data = {}
    total_distance_scaled = 0
    total_load = 0
    
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        route_distance = 0
        route_load = 0
        
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            route_load += demands[node]
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
        # Cerrar el lazo regresando al depósito
        route.append(manager.IndexToNode(index))
        
        # Consideramos la ruta activa solo si atiende a clientes (longitud > 2)
        if len(route) > 2:
            # Dividimos la distancia por 100.0 para revertir el escalado de OR-Tools
            real_distance = round(route_distance / 100.0, 2)
            routes_data[vehicle_id] = {
                "route": route,
                "distance": real_distance,
                "load": route_load
            }
            total_distance_scaled += route_distance
            total_load += route_load
            
    return {
        "routes": routes_data,
        "total_distance": round(total_distance_scaled / 100.0, 2),
        "total_load": total_load
    }


# =====================================================================
# MÓDULO D: ORQUESTADOR Y VISUALIZACIÓN
# =====================================================================

def formatear_nombre_nodo(node_id: int) -> str:
    """Retorna un nombre legible para el nodo (Depósito o Cliente X)."""
    return "Depósito" if node_id == 0 else f"Cliente {node_id}"


def visualizar_rutas(
    G: nx.DiGraph,
    routes: Dict[int, Dict],
    coordinates: Dict[int, Tuple[float, float]],
    capacity_limit: int,
    total_distance: float,
    total_load: int,
    depot_index: int = 0
):
    """
    Genera un gráfico en 2D interactivo con las rutas óptimas del sistema.

    Args:
        G: Grafo de NetworkX.
        routes: Rutas calculadas por el optimizador.
        coordinates: Coordenadas cartesianas de los nodos.
        depot_index: ID de nodo del depósito central.
    """
    fig, ax = plt.subplots(figsize=(12, 9))
    pos = coordinates
    
    # Dibujar depósito (Color rojo, tamaño grande)
    nx.draw_networkx_nodes(
        G, pos, nodelist=[depot_index],
        node_color='red', node_size=600,
        edgecolors='black', linewidths=2,
        label='Depósito Central (50, 50)', ax=ax
    )
    
    # Dibujar clientes (Color azul, tamaño estándar)
    clientes_nodos = [node for node in G.nodes if node != depot_index]
    nx.draw_networkx_nodes(
        G, pos, nodelist=clientes_nodos,
        node_color='#1f77b4', node_size=300,
        edgecolors='black', linewidths=1,
        label='Clientes', ax=ax
    )
    
    # Dibujar etiquetas de los IDs de los nodos
    nx.draw_networkx_labels(
        G, pos, font_color='white', font_size=9,
        font_weight='bold', ax=ax
    )
    
    # Intentar obtener colormap de forma compatible
    try:
        cmap = plt.colormaps['tab10']
    except AttributeError:
        # Fallback para versiones antiguas de Matplotlib
        cmap = plt.get_cmap('tab10')
        
    # Dibujar las aristas con flechas de dirección para cada vehículo
    for idx, (vehicle_id, data) in enumerate(routes.items()):
        route = data["route"]
        route_edges = [(route[i], route[i+1]) for i in range(len(route) - 1)]
        color = cmap(idx % 10)  # Evitar desborde si hay más de 10 vehículos activos
        
        nx.draw_networkx_edges(
            G, pos, edgelist=route_edges,
            edge_color=[color], width=2.5,
            arrows=True, arrowstyle='-|>', arrowsize=15,
            node_size=300,  # Asegura que las flechas se dibujen justo al borde del nodo
            label=f'Ruta Vehículo {vehicle_id} (Carga: {data["load"]}/{capacity_limit} u | Dist: {data["distance"]} km)',
            ax=ax
        )
        
    ax.set_title(
        "VRP: Optimización del Enrutamiento de la Flota Logística\n"
        f"Distancia Total Recorrida: {total_distance} km | Carga Total: {total_load} unidades",
        fontsize=14, fontweight='bold', pad=15
    )
    ax.set_xlabel("Coordenada X (km)", fontsize=11)
    ax.set_ylabel("Coordenada Y (km)", fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Posicionar la leyenda fuera del gráfico para que no tape los nodos
    ax.legend(loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0, fontsize=10)
    
    plt.tight_layout()
    plt.show()


def main():
    """Función principal que orquesta la ejecución del optimizador."""
    
    print("=" * 70)
    print("SISTEMA DE OPTIMIZACION DE RUTAS LOGISTICAS (VRP - OR-TOOLS)")
    print("=" * 70)
    
    # 1. Generar datos
    data = generar_datos_simulados(
        num_clientes=15,
        deposito_coords=(50.0, 50.0),
        capacidad_vehiculo=15,
        semilla=42
    )
    
    coordinates = data["coordinates"]
    demands = data["demands"]
    num_vehicles = data["num_vehicles"]
    capacity_limit = data["vehicle_capacity"]
    
    # 2. Construir Grafo y Matriz de Distancia
    G, distance_matrix = construir_grafo_y_matriz(coordinates)
    
    # 3. Resolver el problema con el Motor OR-Tools
    solucion = resolver_vrp(
        distance_matrix=distance_matrix,
        demands=demands,
        vehicle_capacity=capacity_limit,
        num_vehicles=num_vehicles,
        depot_index=0
    )
    
    # 4. Mostrar Resultados y Visualización
    if solucion:
        print("\n" + "=" * 70)
        print("SOLUCION ENCONTRADA CON EXITO")
        print("=" * 70)
        
        routes = solucion["routes"]
        total_dist_recorrida = solucion["total_distance"]
        total_carga_recorrida = solucion["total_load"]
        
        # Imprimir resumen de cada ruta en consola
        for vehicle_id, data_vehiculo in routes.items():
            ruta_formateada = " -> ".join(formatear_nombre_nodo(node) for node in data_vehiculo["route"])
            print(f"Ruta del vehiculo {vehicle_id}: {ruta_formateada}")
            print(f"   - Carga transportada: {data_vehiculo['load']}/{capacity_limit} unidades")
            print(f"   - Distancia recorrida: {data_vehiculo['distance']} km\n")
            
        print("-" * 70)
        print("RESUMEN GLOBAL:")
        print(f" * Distancia Total Recorrida por la Flota: {total_dist_recorrida} km")
        print(f" * Capacidad Total de Carga Entregada: {total_carga_recorrida} unidades")
        print(f" * Vehiculos Activos Utilizados: {len(routes)} de {num_vehicles}")
        print("=" * 70)
        
        # Lanzar visualización gráfica
        visualizar_rutas(G, routes, coordinates, capacity_limit, total_dist_recorrida, total_carga_recorrida, depot_index=0)
        
    else:
        print("\n[ERROR] No se pudo encontrar una solución factible para el problema actual.")
        print("Sugerencia: Aumente el número de vehículos en la flota o aumente la capacidad de carga.")


if __name__ == "__main__":
    main()
