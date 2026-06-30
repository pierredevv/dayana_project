# -*- coding: utf-8 -*-

import os
from flask import Flask
from app.controller.routes import maze_bp

def create_app() -> Flask:
    """
    Crea y configura la aplicación Flask, estableciendo los directorios para
    plantillas y archivos estáticos siguiendo la estructura de carpetas requerida.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'app', 'templates')
    static_dir = os.path.join(base_dir, 'app', 'static')

    app = Flask(
        __name__, 
        template_folder=template_dir, 
        static_folder=static_dir
    )

    # Registrar el Blueprint de enrutamiento
    app.register_blueprint(maze_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    print("======================================================================")
    print("  SERVIDOR DEL GENERADOR Y SOLUCIONADOR DE LABERINTOS INICIADO")
    print("  Accede a la aplicación en: http://127.0.0.1:5000")
    print("======================================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)
