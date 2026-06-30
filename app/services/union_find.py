# -*- coding: utf-8 -*-

class UnionFind:
    """
    Clase UnionFind (Disjoint-Set)
    ------------------------------
    Estructura de datos para manejar conjuntos disjuntos. Permite realizar operaciones de
    búsqueda ('find') y de unión ('union') de conjuntos eficientemente.
    Implementa optimización de unión por rango (Union by Rank) y compresión de caminos
    (Path Compression), fundamentales para el Algoritmo de Kruskal.
    
    Complejidad Temporal:
        - find: O(alpha(N)) casi constante, donde alpha es la inversa de la función de Ackermann.
        - union: O(alpha(N)) casi constante.
    Complejidad Espacial: O(N) para almacenar las estructuras de padres y rangos.
    """

    def __init__(self, size: int):
        """
        Inicializa la estructura UnionFind con N elementos, donde cada uno es su propio padre
        y el rango inicial es 0.
        """
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, i: int) -> int:
        """
        Encuentra el representante o raíz del conjunto que contiene al elemento 'i'.
        Implementa compresión de caminos, apuntando los nodos directamente a la raíz.
        """
        if self.parent[i] == i:
            return i
        # Compresión de caminos recursiva
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: int, j: int) -> bool:
        """
        Une los conjuntos que contienen a 'i' y a 'j'.
        Retorna True si la unión fue exitosa (pertenecían a conjuntos diferentes)
        y False si ya estaban en el mismo conjunto.
        """
        root_i = self.find(i)
        root_j = self.find(j)
        
        if root_i != root_j:
            # Unión por Rango
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            return True
        return False
