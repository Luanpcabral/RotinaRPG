import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

file_manager_bp = Blueprint('file_manager', __name__)

# Diretório base do projeto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Arquivos permitidos para edição
ALLOWED_FILES = {
    'src/main.py': 'python',
    'src/__init__.py': 'python',
    'src/init_pets.py': 'python',
    'src/models/user.py': 'python',
    'src/models/pet.py': 'python',
    'src/models/store.py': 'python',
    'src/routes/user.py': 'python',
    'src/routes/tasks.py': 'python',
    'src/routes/achievements.py': 'python',
    'src/routes/store.py': 'python',
    'src/routes/timer.py': 'python',
    'src/routes/pets.py': 'python',
    'src/utils/daily_reset.py': 'python',
    'requirements.txt': 'text',
    'README.md': 'markdown'
}

@file_manager_bp.route('/files', methods=['GET'])
def list_files():
    """Lista todos os arquivos disponíveis para edição"""
    try:
        files_info = {}
        for file_path, file_type in ALLOWED_FILES.items():
            full_path = os.path.join(PROJECT_ROOT, file_path)
            if os.path.exists(full_path):
                files_info[file_path] = {
                    'type': file_type,
                    'exists': True,
                    'size': os.path.getsize(full_path)
                }
            else:
                files_info[file_path] = {
                    'type': file_type,
                    'exists': False,
                    'size': 0
                }
        
        return jsonify({
            'success': True,
            'files': files_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_manager_bp.route('/files/<path:file_path>', methods=['GET'])
def read_file(file_path):
    """Lê o conteúdo de um arquivo específico"""
    try:
        # Verificar se o arquivo está na lista permitida
        if file_path not in ALLOWED_FILES:
            return jsonify({
                'success': False,
                'error': 'Arquivo não permitido para edição'
            }), 403
        
        full_path = os.path.join(PROJECT_ROOT, file_path)
        
        if not os.path.exists(full_path):
            return jsonify({
                'success': False,
                'error': 'Arquivo não encontrado'
            }), 404
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'file_type': ALLOWED_FILES[file_path]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_manager_bp.route('/files/<path:file_path>', methods=['POST'])
def save_file(file_path):
    """Salva o conteúdo de um arquivo específico"""
    try:
        # Verificar se o arquivo está na lista permitida
        if file_path not in ALLOWED_FILES:
            return jsonify({
                'success': False,
                'error': 'Arquivo não permitido para edição'
            }), 403
        
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Conteúdo não fornecido'
            }), 400
        
        full_path = os.path.join(PROJECT_ROOT, file_path)
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Fazer backup do arquivo original
        if os.path.exists(full_path):
            backup_path = full_path + '.backup'
            with open(full_path, 'r', encoding='utf-8') as original:
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(original.read())
        
        # Salvar novo conteúdo
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        
        return jsonify({
            'success': True,
            'message': 'Arquivo salvo com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_manager_bp.route('/project/info', methods=['GET'])
def project_info():
    """Retorna informações sobre o projeto"""
    try:
        return jsonify({
            'success': True,
            'project_name': 'Productivity App',
            'project_root': PROJECT_ROOT,
            'total_files': len(ALLOWED_FILES),
            'deploy_url': 'https://g8h3ilc1yk6d.manus.space'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@file_manager_bp.route('/project/backup', methods=['GET'])
def create_backup():
    """Cria um backup de todos os arquivos do projeto"""
    try:
        backup_data = {}
        
        for file_path in ALLOWED_FILES.keys():
            full_path = os.path.join(PROJECT_ROOT, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    backup_data[file_path] = f.read()
        
        return jsonify({
            'success': True,
            'backup': backup_data,
            'timestamp': str(os.time.time())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

