from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
    template_folder=os.path.join(basedir, 'templates'),
    static_folder=os.path.join(basedir, 'static')
)

# Configuración de la base de datos y API key de Bing
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cotizaciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BING_API_KEY'] = '045392bff46d41cebae3a059bba53a42'

db = SQLAlchemy(app)

class Cotizacion(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    asunto = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    numero_cotizacion = db.Column(db.String(20))

    def generate_quote_number(self):
        return f"SEG{str(self.id).zfill(4)}"

@app.route("/", methods=["GET"])
def home():
    return render_template("editor_wendy.html", 
                         api_key=app.config['BING_API_KEY'],
                         logo_url="https://segen.tech/wp-content/uploads/2024/11/cropped-logo_pagina_oficial_letra_s-removebg-preview.png")

@app.route("/crear-cotizacion", methods=["POST"])
def crear_cotizacion():
    try:
        cliente_nombre = request.form.get("cliente_nombre")
        asunto = request.form.get("asunto")
        descripcion = request.form.get("descripcion")
        cantidad = int(request.form.get("cantidad"))
        valor_unitario = float(request.form.get("valor_unitario"))
        valor_total = cantidad * valor_unitario

        nueva_cotizacion = Cotizacion(
            cliente_nombre=cliente_nombre,
            asunto=asunto,
            descripcion=descripcion,
            cantidad=cantidad,
            valor_unitario=valor_unitario,
            valor_total=valor_total
        )
        
        db.session.add(nueva_cotizacion)
        db.session.commit()
        
        nueva_cotizacion.numero_cotizacion = nueva_cotizacion.generate_quote_number()
        db.session.commit()

        return redirect(url_for("ver_cotizacion", cotizacion_id=nueva_cotizacion.id))
    except Exception as e:
        # Manejo de errores
        print(f"Error al crear cotización: {str(e)}")
        return "Error al crear la cotización", 500

@app.route("/ver-cotizacion/<int:cotizacion_id>", methods=["GET"])
def ver_cotizacion(cotizacion_id):
    try:
        cotizacion = Cotizacion.query.get_or_404(cotizacion_id)
        return render_template(
            "cotizacion_wendy.html", 
            cotizacion=cotizacion,
            api_key=app.config['BING_API_KEY'],
            logo_url="https://segen.tech/wp-content/uploads/2024/11/cropped-logo_pagina_oficial_letra_s-removebg-preview.png"
        )
    except Exception as e:
        print(f"Error al ver cotización: {str(e)}")
        return "Error al mostrar la cotización", 500

@app.route("/guardar-cotizacion/<int:cotizacion_id>/<formato>", methods=["GET"])
def guardar_cotizacion(cotizacion_id, formato):
    try:
        cotizacion = Cotizacion.query.get_or_404(cotizacion_id)

        if formato == "html":
            contenido = render_template(
                "cotizacion_wendy.html", 
                cotizacion=cotizacion,
                api_key=app.config['BING_API_KEY'],
                logo_url="https://segen.tech/wp-content/uploads/2024/11/cropped-logo_pagina_oficial_letra_s-removebg-preview.png"
            )
            nombre_archivo = f"cotizacion_{cotizacion.cliente_nombre}.html"
            mimetype = "text/html"
        elif formato == "txt":
            contenido = render_template(
                "cotizacion_wendy.txt", 
                cotizacion=cotizacion,
                api_key=app.config['BING_API_KEY'],
                logo_url="https://segen.tech/wp-content/uploads/2024/11/cropped-logo_pagina_oficial_letra_s-removebg-preview.png"
            )
            nombre_archivo = f"cotizacion_{cotizacion.cliente_nombre}.txt"
            mimetype = "text/plain"
        else:
            return "Formato no válido", 400

        response = make_response(contenido)
        response.headers["Content-Disposition"] = f"attachment; filename={nombre_archivo}"
        response.mimetype = mimetype
        return response
    except Exception as e:
        print(f"Error al guardar cotización: {str(e)}")
        return "Error al guardar la cotización", 500

@app.template_filter('currency')
def currency_filter(value):
    return f"${value:,.2f}"

# Manejo de errores 404
@app.errorhandler(404)
def not_found_error(error):
    return "Página no encontrada", 404

# Manejo de errores 500
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return "Error interno del servidor", 500

# Inicialización de la base de datos
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
