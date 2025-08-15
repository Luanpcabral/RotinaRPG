import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.tasks import tasks_bp
from src.routes.achievements import achievements_bp, init_default_achievements
from src.routes.store import store_bp
from src.routes.timer import timer_bp
from src.routes.pets import pets_bp
from src.routes.file_manager import file_manager_bp
from src.utils.daily_reset import schedule_daily_reset
from src.models.pet import Pet, UserPet, PetBoxOpening  # Importar modelos de pets

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar CORS para permitir requisições do frontend
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(tasks_bp, url_prefix='/api')
app.register_blueprint(achievements_bp, url_prefix='/api')
app.register_blueprint(store_bp, url_prefix='/api')
app.register_blueprint(timer_bp, url_prefix='/api')
app.register_blueprint(pets_bp, url_prefix='/api')
app.register_blueprint(file_manager_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    # Inicializar conquistas padrão
    init_default_achievements()
    # Inicializar pets
    from src.init_pets import init_pets
    init_pets()
    # Inicializar sistema de reset diário
    schedule_daily_reset()
    
    # Criar usuário padrão se não existir
    from src.models.user import User
    if not User.query.filter_by(email="luan@example.com").first():
        default_user = User(
            username="Luan",
            email="luan@example.com",
            level=1,
            xp=0,
            coins=0,
            avatar_stage=1
        )
        db.session.add(default_user)
        db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

