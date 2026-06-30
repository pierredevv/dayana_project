# Generador y Solucionador de Laberintos (MazeCraft AI)

Este es un proyecto académico desarrollado en Python utilizando el patrón de diseño **Modelo-Vista-Controlador (MVC)**. La aplicación web genera laberintos perfectos utilizando diferentes algoritmos de teoría de grafos y árboles de expansión mínima (MST), y posteriormente los resuelve encontrando el camino óptimo entre un punto inicial y final, visualizando todo el proceso de exploración e interactuando en tiempo real desde el navegador.

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para instalar y ejecutar el proyecto en tu entorno local:

### Requisitos Previos
* **Python 3.8 o superior** instalado en tu sistema.
* Administrador de paquetes de Python (`pip`).

### Pasos
1. **Clonar o descargar** este repositorio en tu máquina local.
2. **Abrir una terminal** (consola/Powershell) en la carpeta raíz del proyecto.
3. **Crear un entorno virtual** (opcional pero recomendado):
   ```bash
   python -m venv venv
   ```
4. **Activar el entorno virtual**:
   * En Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * En macOS / Linux:
     ```bash
     source venv/bin/activate
     ```
5. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Iniciar el servidor web**:
   ```bash
   python main.py
   ```
7. **Acceder a la aplicación**: Abre tu navegador web y navega a [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## 🛠️ Estructura del Proyecto (Patrón MVC)

El código fuente está estrictamente separado de acuerdo al patrón de diseño arquitectónico **Model-View-Controller**:

* **`main.py`**: Punto de entrada principal. Configura y arranca el servidor web Flask.
* **`app/model/` (Modelo)**:
  * `cell.py`: Modela el nodo individual del grafo (celda con sus 4 paredes y estados de visita).
  * `grid.py`: Estructura bidimensional de celdas. Define la topología del grafo y vecindades.
  * `maze.py`: Representa el laberinto total, controlando el punto de inicio/fin y su serialización a JSON.
* **`app/controller/` (Controlador)**:
  * `maze_controller.py`: Recibe las peticiones de la API, valida los parámetros, invoca la lógica de los servicios y calcula estadísticas.
  * `routes.py`: Define los endpoints HTTP de la API REST (`/api/generate` y `/api/solve`).
* **`app/services/` (Servicios Algorítmicos)**:
  * `generators/`: Contiene los generadores de laberintos (`dfs_generator.py`, `prim_generator.py`, `kruskal_generator.py`).
  * `solvers/`: Contiene los resolvedores de laberintos (`bfs_solver.py`, `dfs_solver.py`, `astar_solver.py`).
  * `union_find.py`: Estructura Disjoint-Set para comprobar/evitar ciclos en Kruskal.
* **`app/templates/` & `app/static/` (Vista)**:
  * `index.html`: Estructura e interfaz de usuario del frontend.
  * `style.css`: Estilos visuales modernos (Dark Mode, transiciones, adaptabilidad responsiva).
  * `maze_renderer.js`: Controla el lienzo HTML5 `<canvas>`, realiza llamadas fetch asíncronas a la API y anima paso a paso las búsquedas de caminos.

---

## 🧠 Algoritmos Implementados

### 1. Algoritmos de Generación de Laberintos

Los tres algoritmos implementados garantizan la creación de **laberintos perfectos** (laberintos sin ciclos ni celdas inaccesibles, donde existe exactamente una sola ruta simple entre cualquier par de celdas).

#### A. DFS - Backtracking Recursivo (Iterativo)
* **Descripción**: Se inicia en una celda y se explora lo más profundo posible visitando vecinos no descubiertos al azar y derribando la pared intermedia. Al llegar a un callejón sin salida, retrocede utilizando una pila (*stack*) para buscar rutas alternativas.
* **Complejidad Temporal**: $\mathcal{O}(V + E) = \mathcal{O}(N)$ donde $N$ es el número total de celdas. Visita cada nodo un número constante de veces.
* **Complejidad Espacial**: $\mathcal{O}(V) = \mathcal{O}(N)$ para la pila explícita utilizada en el retroceso.
* **Características**: Produce caminos muy largos y sinuosos, con pocas bifurcaciones cortas.

#### B. Algoritmo de Prim Aleatorio (Árbol de Expansión Mínima)
* **Descripción**: Comienza con una celda en el laberinto y agrega sus vecinos no visitados a un conjunto frontera. Elige un nodo frontera al azar, lo conecta al laberinto derribando la pared hacia un vecino visitado adyacente y actualiza la frontera con los nuevos vecinos del nodo integrado.
* **Complejidad Temporal**: $\mathcal{O}(V \log V) = \mathcal{O}(N \log N)$ debido a la inserción y selección aleatoria del conjunto frontera.
* **Complejidad Espacial**: $\mathcal{O}(V) = \mathcal{O}(N)$ para almacenar el conjunto frontera.
* **Características**: Produce pasillos considerablemente más cortos y múltiples bifurcaciones rápidas.

#### C. Algoritmo de Kruskal Aleatorio (Union-Find)
* **Descripción**: Inicializa cada celda como un conjunto aislado. Se crea una lista con todas las paredes internas del laberinto y se mezclan aleatoriamente. Para cada pared, si las celdas adyacentes pertenecen a conjuntos distintos (comprobado eficientemente mediante la estructura *Union-Find*), la pared se derriba y los conjuntos se unen. Si ya pertenecen al mismo conjunto, la pared se mantiene para evitar bucles.
* **Complejidad Temporal**: $\mathcal{O}(E \log V) = \mathcal{O}(N \log N)$ debido al barajado de la lista de aristas (paredes). La búsqueda y unión toman tiempo casi constante gracias a las optimizaciones de compresión de caminos y rango.
* **Complejidad Espacial**: $\mathcal{O}(V) = \mathcal{O}(N)$ para registrar los conjuntos disjuntos.
* **Características**: Patrón visual muy homogéneo, de textura fractal equilibrada.

---

### 2. Algoritmos de Resolución de Laberintos

#### A. BFS (Búsqueda en Anchura)
* **Descripción**: Explora de forma radial todos los caminos posibles nivel por nivel partiendo desde el inicio. Utiliza una cola (*queue* FIFO). Al ser un grafo no ponderado, **garantiza encontrar el camino más corto**.
* **Complejidad Temporal**: $\mathcal{O}(V + E) = \mathcal{O}(N)$ ya que visita cada celda y pared transitable a lo sumo una vez.
* **Complejidad Espacial**: $\mathcal{O}(V) = \mathcal{O}(N)$ para mantener la cola de nodos y el mapa de padres para reconstruir la ruta.

#### B. DFS (Búsqueda en Profundidad)
* **Descripción**: Explora agresivamente a lo largo de cada rama antes de retroceder. Utiliza una pila (*stack* LIFO). **No garantiza encontrar el camino más corto**, pero es rápido y efectivo en laberintos de solución única.
* **Complejidad Temporal**: $\mathcal{O}(V + E) = \mathcal{O}(N)$ en el peor caso.
* **Complejidad Espacial**: $\mathcal{O}(V) = \mathcal{O}(N)$ para mantener la pila de exploración.

#### C. A* (Búsqueda Heurística Informed)
* **Descripción**: Algoritmo de búsqueda guiada que evalúa los nodos basándose en $f(n) = g(n) + h(n)$, donde $g(n)$ es el costo real acumulado y $h(n)$ es la estimación heurística al final. Utiliza una cola de prioridad (*min-heap*) y la **distancia Manhattan** como heurística admisible ($|x_n - x_{end}| + |y_n - y_{end}|$), garantizando el camino óptimo con una exploración muy focalizada.
* **Complejidad Temporal**: $\mathcal{O}(E \log V) = \mathcal{O}(N \log N)$ debido a las operaciones de inserción y extracción del min-heap.
* **Complejidad Espacial**: $\mathcal{O}(V) = \mathcal{O}(N)$ para almacenar el mapa de costos y la cola de prioridad.
