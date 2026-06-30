/**
 * ==========================================================================
 * Lógica del Renderizado y Conexión API - MazeCraft AI
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    // ---- CONFIGURACIONES Y VARIABLES DE ESTADO ----
    let currentMaze = null;
    let isAnimating = false;
    let animationTimeoutId = null;

    // Listas para control de animación
    let exploredList = [];
    let solutionPath = [];
    let animatedExploredCount = 0;
    let animatedPathCount = 0;
    let solvePhase = 'idle'; // 'idle' | 'exploring' | 'drawing_path' | 'solved'

    // Elementos del DOM
    const canvas = document.getElementById('maze-canvas');
    const ctx = canvas.getContext('2d');
    const canvasContainer = canvas.parentElement;
    const canvasOverlay = document.getElementById('canvas-overlay');
    const overlayText = document.getElementById('overlay-text');

    // Controles
    const inputCols = document.getElementById('input-cols');
    const inputRows = document.getElementById('input-rows');
    const valCols = document.getElementById('val-cols');
    const valRows = document.getElementById('val-rows');
    const selectGenerator = document.getElementById('select-generator');
    const selectSolver = document.getElementById('select-solver');
    const inputSpeed = document.getElementById('input-speed');
    const valSpeed = document.getElementById('val-speed');

    // Botones
    const btnGenerate = document.getElementById('btn-generate');
    const btnSolve = document.getElementById('btn-solve');
    const btnClear = document.getElementById('btn-clear');

    // Estadísticas y Badges
    const statGenTime = document.getElementById('stat-gen-time');
    const statSolveTime = document.getElementById('stat-solve-time');
    const statVisited = document.getElementById('stat-visited');
    const statPathLen = document.getElementById('stat-path-len');
    const statusText = document.getElementById('status-text');
    const badgeGen = document.getElementById('badge-gen');
    const badgeSolved = document.getElementById('badge-solved');

    // ---- SINCRONIZACIÓN DE CONTROLES DE LA UI ----
    inputCols.addEventListener('input', () => { valCols.textContent = inputCols.value; });
    inputRows.addEventListener('input', () => { valRows.textContent = inputRows.value; });
    
    function getSpeedLabel(val) {
        if (val < 20) return 'Muy Lenta';
        if (val < 45) return 'Lenta';
        if (val < 70) return 'Media';
        if (val < 90) return 'Rápida';
        return 'Ultra Rápida';
    }
    
    inputSpeed.addEventListener('input', () => {
        valSpeed.textContent = getSpeedLabel(parseInt(inputSpeed.value));
    });
    valSpeed.textContent = getSpeedLabel(parseInt(inputSpeed.value));

    // ---- AJUSTE DE TAMAÑO DEL CANVAS (DPI APROPIADO) ----
    function resizeCanvas() {
        const rect = canvasContainer.getBoundingClientRect();
        // Reducir un poco el tamaño para dejar un margen interno estético
        const padding = 32;
        const targetWidth = Math.floor(rect.width - padding);
        const targetHeight = Math.floor(rect.height - padding);
        
        // Ajustar el canvas al contenedor
        canvas.width = targetWidth;
        canvas.height = targetHeight;
        
        // Redibujar si ya hay un laberinto en memoria
        if (currentMaze) {
            drawMaze();
        } else {
            drawWelcomeScreen();
        }
    }
    
    // Escuchar el evento de redimensión del navegador
    window.addEventListener('resize', resizeCanvas);

    // Pantalla de bienvenida / estado inicial
    function drawWelcomeScreen() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#94a3b8';
        ctx.font = '500 16px "Plus Jakarta Sans", sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('MazeCraft AI: Presiona "Generar Laberinto" para comenzar', canvas.width / 2, canvas.height / 2);
    }

    // ---- DETALLES DE CÁLCULO DE COORDENADAS Y DIBUJO ----
    function getMazeMetrics() {
        if (!currentMaze) return null;
        
        const cols = currentMaze.cols;
        const rows = currentMaze.rows;
        
        // Dejar un margen de seguridad
        const padding = 10;
        const availableWidth = canvas.width - padding * 2;
        const availableHeight = canvas.height - padding * 2;
        
        // Tamaño de celda cuadrado óptimo
        const cellSize = Math.min(availableWidth / cols, availableHeight / rows);
        
        // Centrar el laberinto dentro del canvas
        const offsetX = padding + (availableWidth - cols * cellSize) / 2;
        const offsetY = padding + (availableHeight - rows * cellSize) / 2;
        
        return { cols, rows, cellSize, offsetX, offsetY };
    }

    // Renderiza el estado actual del laberinto en el Canvas
    function drawMaze() {
        if (!currentMaze) return;
        
        const metrics = getMazeMetrics();
        if (!metrics) return;
        
        const { cols, rows, cellSize, offsetX, offsetY } = metrics;
        
        // 1. Limpiar Canvas y rellenar fondo
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#0b0e14'; // Fondo del laberinto
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // 2. Dibujar celdas (Caminos y Estados de exploración)
        for (let y = 0; y < rows; y++) {
            for (let x = 0; x < cols; x++) {
                const cell = currentMaze.grid[y][x];
                const cx = offsetX + x * cellSize;
                const cy = offsetY + y * cellSize;
                
                // Color base del camino libre
                ctx.fillStyle = '#161d2a';
                ctx.fillRect(cx, cy, cellSize, cellSize);
            }
        }

        // 3. Dibujar celdas exploradas (animación de búsqueda)
        if (exploredList.length > 0 && animatedExploredCount > 0) {
            const limit = Math.min(animatedExploredCount, exploredList.length);
            for (let i = 0; i < limit; i++) {
                const pos = exploredList[i];
                const cx = offsetX + pos.x * cellSize;
                const cy = offsetY + pos.y * cellSize;
                
                // Si está en el frente de exploración (los últimos 3 celdas procesadas), brillará más
                if (solvePhase === 'exploring' && i >= limit - 3) {
                    ctx.fillStyle = 'rgba(34, 211, 238, 0.7)'; // Cyan brillante
                } else {
                    // Celdas exploradas normales: transitorias en tonos índigos
                    ctx.fillStyle = 'rgba(99, 102, 241, 0.25)';
                }
                ctx.fillRect(cx, cy, cellSize, cellSize);
            }
        }

        // 4. Dibujar Ruta Solución (línea fluida continua)
        if (solutionPath.length > 0 && animatedPathCount > 0) {
            const limit = Math.min(animatedPathCount, solutionPath.length);
            
            ctx.beginPath();
            ctx.lineWidth = Math.max(3, cellSize * 0.35); // Grosor proporcional a la celda
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.strokeStyle = '#f59e0b'; // Ámbar/Oro brillante
            
            // Iniciar ruta en el centro de la celda de partida
            const startX = offsetX + solutionPath[0].x * cellSize + cellSize / 2;
            const startY = offsetY + solutionPath[0].y * cellSize + cellSize / 2;
            ctx.moveTo(startX, startY);
            
            for (let i = 1; i < limit; i++) {
                const node = solutionPath[i];
                const nx = offsetX + node.x * cellSize + cellSize / 2;
                const ny = offsetY + node.y * cellSize + cellSize / 2;
                ctx.lineTo(nx, ny);
            }
            ctx.stroke();
        }

        // 5. Dibujar celdas de Inicio y Fin
        const startCX = offsetX + currentMaze.start.x * cellSize;
        const startCY = offsetY + currentMaze.start.y * cellSize;
        const endCX = offsetX + currentMaze.end.x * cellSize;
        const endCY = offsetY + currentMaze.end.y * cellSize;
        
        // Inicio (Verde Esmeralda)
        ctx.fillStyle = '#10b981';
        ctx.fillRect(startCX + 2, startCY + 2, cellSize - 4, cellSize - 4);
        ctx.fillStyle = '#ffffff';
        ctx.font = `600 ${Math.max(10, cellSize * 0.4)}px "Plus Jakarta Sans"`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('I', startCX + cellSize / 2, startCY + cellSize / 2);

        // Fin (Rojo Carmesí)
        ctx.fillStyle = '#f43f5e';
        ctx.fillRect(endCX + 2, endCY + 2, cellSize - 4, cellSize - 4);
        ctx.fillStyle = '#ffffff';
        ctx.fillText('F', endCX + 2 + (cellSize - 4) / 2, endCY + 2 + (cellSize - 4) / 2);

        // 6. Dibujar Paredes del Laberinto
        ctx.beginPath();
        ctx.strokeStyle = '#334155'; // Gris pizarra
        ctx.lineWidth = Math.max(1.5, cellSize * 0.08); // Ancho adaptativo de pared
        ctx.lineCap = 'square';
        
        for (let y = 0; y < rows; y++) {
            for (let x = 0; x < cols; x++) {
                const cell = currentMaze.grid[y][x];
                const cx = offsetX + x * cellSize;
                const cy = offsetY + y * cellSize;
                
                // Si la pared correspondiente está levantada, trazar la línea
                if (cell.walls.N) { // Norte
                    ctx.moveTo(cx, cy);
                    ctx.lineTo(cx + cellSize, cy);
                }
                if (cell.walls.S) { // Sur
                    ctx.moveTo(cx, cy + cellSize);
                    ctx.lineTo(cx + cellSize, cy + cellSize);
                }
                if (cell.walls.E) { // Este
                    ctx.moveTo(cx + cellSize, cy);
                    ctx.lineTo(cx + cellSize, cy + cellSize);
                }
                if (cell.walls.W) { // Oeste
                    ctx.moveTo(cx, cy);
                    ctx.lineTo(cx, cy + cellSize);
                }
            }
        }
        ctx.stroke();
    }

    // ---- LOADER / OVERLAYS ----
    function showOverlay(message) {
        overlayText.textContent = message;
        canvasOverlay.classList.remove('hidden');
    }

    function hideOverlay() {
        canvasOverlay.classList.add('hidden');
    }

    // ---- LLAMADAS A LA API REST (FETCH) ----

    // Generar laberinto llamando al Backend
    async function generateMaze() {
        if (isAnimating) cancelAnimation();
        
        const cols = parseInt(inputCols.value);
        const rows = parseInt(inputRows.value);
        const algorithm = selectGenerator.value;
        
        showOverlay('Generando Laberinto...');
        setUIState('busy');
        
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cols, rows, algorithm })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                alert(`Error: ${data.error}`);
                setUIState('idle');
                return;
            }
            
            // Almacenar laberinto en estado
            currentMaze = data.maze;
            
            // Limpiar datos previos de resolución
            exploredList = [];
            solutionPath = [];
            animatedExploredCount = 0;
            animatedPathCount = 0;
            solvePhase = 'idle';
            
            // Actualizar estadísticas del backend
            statGenTime.textContent = `${data.stats.generation_time_ms} ms`;
            statSolveTime.textContent = '-';
            statVisited.textContent = '-';
            statPathLen.textContent = '-';
            
            statusText.textContent = 'Laberinto generado con éxito';
            badgeGen.textContent = `${cols}x${rows} (${selectGenerator.options[selectGenerator.selectedIndex].text})`;
            badgeSolved.textContent = 'Sin Resolver';
            badgeSolved.className = 'badge badge-indigo';
            
            // Dibujar el laberinto
            drawMaze();
            setUIState('ready');
            
        } catch (error) {
            console.error('Error al generar:', error);
            alert('Ocurrió un error al conectar con el servidor.');
            setUIState('idle');
        } finally {
            hideOverlay();
        }
    }

    // Resolver laberinto llamando al Backend
    async function solveMaze() {
        if (!currentMaze) return;
        if (isAnimating) cancelAnimation();
        
        const algorithm = selectSolver.value;
        showOverlay('Calculando solución...');
        setUIState('busy');
        
        try {
            const response = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ maze: currentMaze, algorithm })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                alert(`Error: ${data.error}`);
                setUIState('ready');
                return;
            }
            
            // Almacenar resultados de la búsqueda
            exploredList = data.explored;
            solutionPath = data.path;
            
            // Actualizar estadísticas en UI
            statSolveTime.textContent = `${data.stats.solve_time_ms} ms`;
            statVisited.textContent = data.stats.visited_nodes;
            statPathLen.textContent = data.path.length > 0 ? `${data.stats.path_length} celdas` : 'Inalcanzable';
            
            if (data.path.length === 0) {
                statusText.textContent = 'Búsqueda finalizada. ¡El laberinto no tiene solución!';
                badgeSolved.textContent = 'Sin Solución';
                badgeSolved.className = 'badge badge-rose';
            }
            
            // Lanzar animación paso a paso
            animateSearch();
            
        } catch (error) {
            console.error('Error al resolver:', error);
            alert('Ocurrió un error de red al resolver el laberinto.');
            setUIState('ready');
        } finally {
            hideOverlay();
        }
    }

    // ---- SISTEMA DE ANIMACIÓN DINÁMICA ----
    
    function cancelAnimation() {
        if (animationTimeoutId) {
            clearTimeout(animationTimeoutId);
            animationTimeoutId = null;
        }
        isAnimating = false;
    }

    // Animación de la exploración de celdas (Frente de onda)
    function animateSearch() {
        isAnimating = true;
        animatedExploredCount = 0;
        animatedPathCount = 0;
        solvePhase = 'exploring';
        setUIState('animating');
        
        statusText.textContent = `Explorando camino con ${selectSolver.options[selectSolver.selectedIndex].text}...`;

        function step() {
            if (!isAnimating) return;
            
            // Determinar velocidad y tamaño de lote (batch size) adaptativo.
            // Para laberintos grandes y velocidades altas, dibujamos múltiples celdas por fotograma.
            const speedVal = parseInt(inputSpeed.value); // 1 a 100
            
            // El delay es inverso a la velocidad. Rango: de 1ms a 150ms.
            const delay = Math.max(1, Math.floor(150 - (speedVal * 1.48)));
            
            // Tamaño de lote: a velocidades > 70 dibuja varios de golpe
            let batchSize = 1;
            if (speedVal > 70) batchSize = 2;
            if (speedVal > 85) batchSize = Math.max(3, Math.ceil(exploredList.length / 100));
            if (speedVal > 95) batchSize = Math.max(5, Math.ceil(exploredList.length / 40));

            animatedExploredCount += batchSize;
            
            if (animatedExploredCount >= exploredList.length) {
                animatedExploredCount = exploredList.length;
                drawMaze();
                
                // Fin de la exploración. Proceder a pintar la ruta si existe.
                if (solutionPath && solutionPath.length > 0) {
                    animatePath();
                } else {
                    finishAnimation(false);
                }
            } else {
                drawMaze();
                animationTimeoutId = setTimeout(step, delay);
            }
        }
        
        step();
    }

    // Animación del trazo del camino solución
    function animatePath() {
        solvePhase = 'drawing_path';
        animatedPathCount = 0;
        
        statusText.textContent = 'Trazando ruta de solución óptima...';

        function step() {
            if (!isAnimating) return;
            
            const speedVal = parseInt(inputSpeed.value);
            const delay = Math.max(2, Math.floor(100 - (speedVal * 0.95)));
            
            let batchSize = 1;
            if (speedVal > 80) batchSize = 2;
            if (speedVal > 95) batchSize = Math.max(3, Math.ceil(solutionPath.length / 30));

            animatedPathCount += batchSize;
            
            if (animatedPathCount >= solutionPath.length) {
                animatedPathCount = solutionPath.length;
                drawMaze();
                finishAnimation(true);
            } else {
                drawMaze();
                animationTimeoutId = setTimeout(step, delay);
            }
        }
        
        step();
    }

    // Finalizar proceso de animación y restaurar estado de los botones
    function finishAnimation(hasSolution) {
        isAnimating = false;
        solvePhase = 'solved';
        setUIState('solved');
        
        if (hasSolution) {
            statusText.textContent = 'Laberinto resuelto con éxito';
            badgeSolved.textContent = 'Resuelto';
            badgeSolved.className = 'badge badge-emerald';
        }
    }

    // Limpia la solución pintada sin borrar el laberinto base para poder resolverlo con otro algoritmo
    function clearSolution() {
        cancelAnimation();
        
        exploredList = [];
        solutionPath = [];
        animatedExploredCount = 0;
        animatedPathCount = 0;
        solvePhase = 'idle';
        
        // Reiniciar estadísticas de resolución
        statSolveTime.textContent = '-';
        statVisited.textContent = '-';
        statPathLen.textContent = '-';
        
        statusText.textContent = 'Visualización limpia. Listo para resolver.';
        badgeSolved.textContent = 'Sin Resolver';
        badgeSolved.className = 'badge badge-indigo';
        
        drawMaze();
        setUIState('ready');
    }

    // ---- MÁQUINA DE ESTADO DE LA INTERFAZ DE USUARIO (UI STATE) ----
    function setUIState(state) {
        switch (state) {
            case 'idle':
                btnGenerate.disabled = false;
                btnSolve.disabled = true;
                btnClear.disabled = true;
                inputCols.disabled = false;
                inputRows.disabled = false;
                selectGenerator.disabled = false;
                selectSolver.disabled = false;
                break;
                
            case 'ready':
                btnGenerate.disabled = false;
                btnSolve.disabled = false;
                btnClear.disabled = true;
                inputCols.disabled = false;
                inputRows.disabled = false;
                selectGenerator.disabled = false;
                selectSolver.disabled = false;
                break;
                
            case 'animating':
                btnGenerate.disabled = true;
                btnSolve.disabled = true;
                btnClear.disabled = false; // Permite detener / limpiar
                inputCols.disabled = true;
                inputRows.disabled = true;
                selectGenerator.disabled = true;
                selectSolver.disabled = true;
                break;
                
            case 'solved':
                btnGenerate.disabled = false;
                btnSolve.disabled = false;
                btnClear.disabled = false;
                inputCols.disabled = false;
                inputRows.disabled = false;
                selectGenerator.disabled = false;
                selectSolver.disabled = false;
                break;
                
            case 'busy':
                btnGenerate.disabled = true;
                btnSolve.disabled = true;
                btnClear.disabled = true;
                break;
        }
    }

    // ---- CAPTURA DE EVENTOS DE BOTONES ----
    btnGenerate.addEventListener('click', generateMaze);
    btnSolve.addEventListener('click', solveMaze);
    btnClear.addEventListener('click', clearSolution);

    // Inicialización del Canvas y vista inicial al cargar
    resizeCanvas();
});
