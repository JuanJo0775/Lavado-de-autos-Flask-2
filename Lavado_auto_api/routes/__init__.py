from .dashboard import dashboard_bp
from .vehiculos import vehiculo_bp
from .servicios import servicio_bp
from .insumos import insumo_bp
from .inventario import inventario_bp
from .reportes import reporte_bp

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación"""
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vehiculo_bp)
    app.register_blueprint(servicio_bp)
    app.register_blueprint(insumo_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(reporte_bp)