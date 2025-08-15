from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.user import User, Task, Achievement, UserAchievement, db
from datetime import datetime, date

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@cross_origin()
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
@cross_origin()
def create_user():
    data = request.json
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@cross_origin()
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@cross_origin()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

@user_bp.route('/users/<int:user_id>/stats', methods=['GET'])
@cross_origin()
def get_user_stats(user_id):
    user = User.query.get_or_404(user_id)
    
    # Estatísticas das tarefas
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, completed=True).count()
    
    # Tarefas por tipo
    habits = Task.query.filter_by(user_id=user_id, task_type='habit').count()
    dailies = Task.query.filter_by(user_id=user_id, task_type='daily').count()
    uniques = Task.query.filter_by(user_id=user_id, task_type='unique').count()
    
    # Conquistas
    achievements_earned = UserAchievement.query.filter_by(user_id=user_id).count()
    total_achievements = Achievement.query.count()
    
    return jsonify({
        'user': user.to_dict(),
        'stats': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'habits': habits,
            'dailies': dailies,
            'uniques': uniques,
            'achievements_earned': achievements_earned,
            'total_achievements': total_achievements
        }
    })

@user_bp.route('/users/<int:user_id>/login', methods=['POST'])
@cross_origin()
def user_login(user_id):
    user = User.query.get_or_404(user_id)
    user.last_login = datetime.utcnow()
    db.session.commit()
    return jsonify(user.to_dict())


@user_bp.route('/users/<int:user_id>/reset-progress', methods=['POST'])
@cross_origin()
def reset_user_progress(user_id):
    """Reset completo do progresso do usuário"""
    from src.models.user import Purchase
    
    user = User.query.get_or_404(user_id)
    
    # Resetar dados do usuário
    user.level = 1
    user.xp = 0
    user.coins = 0
    user.avatar_stage = 1
    user.tasks_completed = 0
    user.total_coins_earned = 0
    
    # Deletar todas as tarefas do usuário
    Task.query.filter_by(user_id=user_id).delete()
    
    # Deletar todas as conquistas do usuário
    UserAchievement.query.filter_by(user_id=user_id).delete()
    
    # Deletar todas as compras do usuário
    Purchase.query.filter_by(user_id=user_id).delete()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Progresso resetado com sucesso',
        'user': user.to_dict()
    })

def get_level_title(level):
    """Retorna o título baseado no nível do usuário"""
    if level >= 50:
        return "Lenda Suprema"
    elif level >= 45:
        return "Mestre Absoluto"
    elif level >= 40:
        return "Grande Mestre"
    elif level >= 35:
        return "Mestre Sênior"
    elif level >= 30:
        return "Mestre"
    elif level >= 25:
        return "Especialista Avançado"
    elif level >= 20:
        return "Especialista"
    elif level >= 15:
        return "Veterano"
    elif level >= 10:
        return "Experiente"
    elif level >= 5:
        return "Aprendiz"
    else:
        return "Novato"

@user_bp.route('/users/<int:user_id>/title', methods=['GET'])
@cross_origin()
def get_user_title(user_id):
    """Retorna o título atual do usuário"""
    user = User.query.get_or_404(user_id)
    title = get_level_title(user.level)
    return jsonify({'title': title, 'level': user.level})



@user_bp.route('/users/<int:user_id>/streak', methods=['GET'])
@cross_origin()
def get_user_streak(user_id):
    """Retorna o streak de tarefas do usuário"""
    user = User.query.get_or_404(user_id)
    
    # Calcular streak baseado nas tarefas completadas
    from datetime import datetime, timedelta
    
    # Buscar tarefas completadas ordenadas por data
    completed_tasks = Task.query.filter_by(
        user_id=user_id, 
        completed=True
    ).order_by(Task.completed_at.desc()).all()
    
    if not completed_tasks:
        return jsonify({'streak': 0, 'last_activity': None})
    
    # Calcular streak consecutivo
    streak = 0
    current_date = datetime.now().date()
    
    # Verificar se completou tarefa hoje
    today_tasks = [task for task in completed_tasks 
                   if task.completed_at and task.completed_at.date() == current_date]
    
    if today_tasks:
        streak = 1
        check_date = current_date - timedelta(days=1)
    else:
        # Se não completou hoje, verificar se completou ontem
        yesterday = current_date - timedelta(days=1)
        yesterday_tasks = [task for task in completed_tasks 
                          if task.completed_at and task.completed_at.date() == yesterday]
        if yesterday_tasks:
            streak = 1
            check_date = yesterday - timedelta(days=1)
        else:
            return jsonify({'streak': 0, 'last_activity': completed_tasks[0].completed_at.isoformat()})
    
    # Contar dias consecutivos
    while True:
        day_tasks = [task for task in completed_tasks 
                    if task.completed_at and task.completed_at.date() == check_date]
        if day_tasks:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    return jsonify({
        'streak': streak,
        'last_activity': completed_tasks[0].completed_at.isoformat()
    })

@user_bp.route('/users/<int:user_id>/xp-progress', methods=['GET'])
@cross_origin()
def get_user_xp_progress(user_id):
    """Retorna o progresso de XP dos últimos 5 dias"""
    user = User.query.get_or_404(user_id)
    
    from datetime import datetime, timedelta
    
    # Calcular os últimos 5 dias
    today = datetime.now().date()
    days = []
    xp_data = []
    
    for i in range(4, -1, -1):  # 4, 3, 2, 1, 0 (últimos 5 dias)
        day = today - timedelta(days=i)
        days.append(day.strftime('%d/%m'))
        
        # Buscar tarefas completadas neste dia
        day_tasks = Task.query.filter_by(
            user_id=user_id,
            completed=True
        ).filter(
            db.func.date(Task.completed_at) == day
        ).all()
        
        # Somar XP do dia
        day_xp = sum(task.xp_reward for task in day_tasks)
        xp_data.append(day_xp)
    
    return jsonify({
        'days': days,
        'xp_data': xp_data,
        'total_xp': sum(xp_data)
    })

