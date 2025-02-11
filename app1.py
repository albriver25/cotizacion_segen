from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from weasyprint import HTML

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
    template_folder=os.path.join(basedir, 'templates'),
    static_folder=os.path.join(basedir, 'static')
)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cotizaciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def format_currency(value):
    return "${:,.2f} COP".format(value)

app.jinja_env.filters['currency'] = format_currency

class Cotizacion(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    asunto = db.Column(db.String(200), nullable=False)
    descripcion1 = db.Column(db.Text, nullable=False)
    cantidad1 = db.Column(db.Integer, nullable=False)
    valor_unitario1 = db.Column(db.Float, nullable=False)
    valor_total1 = db.Column(db.Float, nullable=False)
    descripcion2 = db.Column(db.Text, default="")
    cantidad2 = db.Column(db.Integer, default=0)
    valor_unitario2 = db.Column(db.Float, default=0.0)
    valor_total2 = db.Column(db.Float, default=0.0)
    descripcion3 = db.Column(db.Text, default="")
    cantidad3 = db.Column(db.Integer, default=0)
    valor_unitario3 = db.Column(db.Float, default=0.0)
    valor_total3 = db.Column(db.Float, default=0.0)
    descripcion4 = db.Column(db.Text, default="")
    cantidad4 = db.Column(db.Integer, default=0)
    valor_unitario4 = db.Column(db.Float, default=0.0)
    valor_total4 = db.Column(db.Float, default=0.0)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    numero_cotizacion = db.Column(db.String(20))

    def generate_quote_number(self):
        return f"SEG{str(self.id).zfill(4)}"

@app.route("/", methods=["GET"])
def home():
    return render_template("editor_wendy.html")

@app.route("/crear-cotizacion", methods=["POST"])
def crear_cotizacion():
    cliente_nombre = request.form.get("cliente_nombre")
    asunto = request.form.get("asunto")
    
    nueva_cotizacion = Cotizacion(
        cliente_nombre=cliente_nombre,
        asunto=asunto,
        descripcion1=request.form.get("descripcion1", ""),
        cantidad1=int(request.form.get("cantidad1", "0") or 0),
        valor_unitario1=float(request.form.get("valor_unitario1", "0") or 0),
        valor_total1=int(request.form.get("cantidad1", "0") or 0) * float(request.form.get("valor_unitario1", "0") or 0),
        descripcion2=request.form.get("descripcion2", ""),
        cantidad2=int(request.form.get("cantidad2", "0") or 0),
        valor_unitario2=float(request.form.get("valor_unitario2", "0") or 0),
        valor_total2=int(request.form.get("cantidad2", "0") or 0) * float(request.form.get("valor_unitario2", "0") or 0),
        descripcion3=request.form.get("descripcion3", ""),
        cantidad3=int(request.form.get("cantidad3", "0") or 0),
        valor_unitario3=float(request.form.get("valor_unitario3", "0") or 0),
        valor_total3=int(request.form.get("cantidad3", "0") or 0) * float(request.form.get("valor_unitario3", "0") or 0),
        descripcion4=request.form.get("descripcion4", ""),
        cantidad4=int(request.form.get("cantidad4", "0") or 0),
        valor_unitario4=float(request.form.get("valor_unitario4", "0") or 0),
        valor_total4=int(request.form.get("cantidad4", "0") or 0) * float(request.form.get("valor_unitario4", "0") or 0)
    )
    
    db.session.add(nueva_cotizacion)
    db.session.commit()
    nueva_cotizacion.numero_cotizacion = nueva_cotizacion.generate_quote_number()
    db.session.commit()

    return redirect(url_for("ver_cotizacion", cotizacion_id=nueva_cotizacion.id))

@app.route("/ver-cotizacion/<int:cotizacion_id>", methods=["GET"])
def ver_cotizacion(cotizacion_id):
    cotizacion = Cotizacion.query.get_or_404(cotizacion_id)
    return render_template("cotizacion_wendy.html", cotizacion=cotizacion)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
