from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.user import User, Task, Achievement, UserAchievement, db
from datetime import datetime, date, timedelta

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
@cross_origin()
def get_user_tasks(user_id):
    task_type = request.args.get('type')
    
    query = Task.query.filter_by(user_id=user_id)
    if task_type:
        query = query.filter_by(task_type=task_type)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@tasks_bp.route('/users/<int:user_id>/tasks', methods=['POST'])
@cross_origin()
def create_task(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Definir recompensas baseadas na dificuldade
    difficulty_rewards = {
        'easy': {'xp': 10, 'coins': 5},
        'medium': {'xp': 20, 'coins': 10},
        'hard': {'xp': 30, 'coins': 15}
    }
    
    difficulty = data.get('difficulty', 'medium')
    
    # Se for personalizado, usar XP customizado
    if difficulty == 'custom':
        custom_xp = data.get('custom_xp', 20)
        xp_reward = int(custom_xp)
        coin_reward = max(5, int(xp_reward / 2))  # Moedas baseadas no XP
    else:
        rewards = difficulty_rewards.get(difficulty, difficulty_rewards['medium'])
        xp_reward = rewards['xp']
        coin_reward = rewards['coins']
    
    task = Task(
        user_id=user_id,
        title=data['title'],
        description=data.get('description', ''),
        task_type=data['task_type'],
        difficulty=difficulty,
        xp_reward=xp_reward,
        coin_reward=coin_reward,
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None
    )
    
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
@cross_origin()
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@cross_origin()
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.difficulty = data.get('difficulty', task.difficulty)
    
    if data.get('due_date'):
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    
    # Atualizar recompensas se a dificuldade mudou
    if 'difficulty' in data:
        difficulty = task.difficulty
        
        if difficulty == 'custom':
            custom_xp = data.get('custom_xp', task.xp_reward)
            task.xp_reward = int(custom_xp)
            task.coin_reward = max(5, int(task.xp_reward / 2))
        else:
            difficulty_rewards = {
                'easy': {'xp': 10, 'coins': 5},
                'medium': {'xp': 20, 'coins': 10},
                'hard': {'xp': 30, 'coins': 15}
            }
            rewards = difficulty_rewards.get(difficulty, difficulty_rewards['medium'])
            task.xp_reward = rewards['xp']
            task.coin_reward = rewards['coins']
    
    db.session.commit()
    return jsonify(task.to_dict())

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@cross_origin()
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204

@tasks_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@cross_origin()
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    user = User.query.get_or_404(task.user_id)
    
    if task.complete_task():
        # Aplicar buffs dos pets equipados (sistema aditivo)
        from src.models.pet import UserPet
        equipped_pets = UserPet.query.filter_by(user_id=user.id, is_equipped=True).all()
        
        base_xp = task.xp_reward
        base_coins = task.coin_reward
        
        if equipped_pets:
            # Coletar todos os efeitos de todos os pets equipados
            total_xp_bonus = 0
            total_coin_bonus = 0
            total_easy_task_xp_bonus = 0
            total_hard_task_coin_bonus = 0
            total_weekend_xp_bonus = 0
            total_weekend_coin_bonus = 0
            total_weekday_xp_bonus = 0
            total_weekday_coin_bonus = 0
            total_last_task_xp_bonus = 0
            total_first_task_coin_bonus = 0
            total_duplicate_coin_chance = 0
            
            # Somar todos os buffs de forma aditiva
            for pet in equipped_pets:
                effects = pet.get_current_effects()
                
                # Buffs gerais
                total_xp_bonus += effects.get('xp_bonus', 0)
                total_coin_bonus += effects.get('coin_bonus', 0)
                
                # Buffs específicos por dificuldade
                total_easy_task_xp_bonus += effects.get('easy_task_xp_bonus', 0)
                total_hard_task_coin_bonus += effects.get('hard_task_coin_bonus', 0)
                
                # Buffs de final de semana/dia da semana
                total_weekend_xp_bonus += effects.get('weekend_xp_bonus', 0)
                total_weekend_coin_bonus += effects.get('weekend_coin_bonus', 0)
                total_weekday_xp_bonus += effects.get('weekday_xp_bonus', 0)
                total_weekday_coin_bonus += effects.get('weekday_coin_bonus', 0)
                
                # Buffs especiais
                total_last_task_xp_bonus += effects.get('last_task_xp_bonus', 0)
                total_first_task_coin_bonus += effects.get('first_task_coin_bonus', 0)
                total_duplicate_coin_chance += effects.get('duplicate_coin_chance', 0)
            
            # Aplicar buffs de XP (aditivos)
            if total_xp_bonus > 0:
                base_xp = int(base_xp * (1 + total_xp_bonus))
            
            # Aplicar buffs de moedas (aditivos)
            if total_coin_bonus > 0:
                base_coins = int(base_coins * (1 + total_coin_bonus))
            
            # Buffs específicos por dificuldade
            if task.difficulty == 'easy' and total_easy_task_xp_bonus > 0:
                base_xp = int(base_xp * (1 + total_easy_task_xp_bonus))
            
            if task.difficulty == 'hard' and total_hard_task_coin_bonus > 0:
                base_coins = int(base_coins * (1 + total_hard_task_coin_bonus))
            
            # Buffs de final de semana
            from datetime import datetime
            today = datetime.now().weekday()  # 0=Monday, 6=Sunday
            is_weekend = today >= 5  # Saturday or Sunday
            
            if is_weekend:
                if total_weekend_xp_bonus > 0:
                    base_xp = int(base_xp * (1 + total_weekend_xp_bonus))
                if total_weekend_coin_bonus > 0:
                    base_coins = int(base_coins * (1 + total_weekend_coin_bonus))
            else:
                if total_weekday_xp_bonus > 0:
                    base_xp = int(base_xp * (1 + total_weekday_xp_bonus))
                if total_weekday_coin_bonus > 0:
                    base_coins = int(base_coins * (1 + total_weekday_coin_bonus))
            
            # Buffs especiais
            if total_first_task_coin_bonus > 0:
                # Verificar se é a primeira tarefa do dia
                from datetime import date
                today_tasks = Task.query.filter(
                    Task.user_id == user.id,
                    Task.completed == True,
                    db.func.date(Task.completed_at) == date.today()
                ).count()
                
                if today_tasks == 1:  # Esta é a primeira tarefa do dia
                    base_coins += int(total_first_task_coin_bonus)
            
            if total_last_task_xp_bonus > 0:
                # Aplicar bônus na última tarefa (simplificado - aplicar sempre)
                base_xp = int(base_xp * (1 + total_last_task_xp_bonus))
            
            # Chance de duplicar moedas (limitada a 100%)
            if total_duplicate_coin_chance > 0:
                import random
                chance = min(total_duplicate_coin_chance, 1.0)  # Máximo 100%
                if random.random() < chance:
                    base_coins *= 2
        
        # Adicionar XP e moedas ao usuário com buffs aplicados
        level_up = user.add_xp(base_xp)
        user.add_coins(base_coins)
        
        # Verificar conquistas
        check_achievements(user)
        
        # Se for missão única, agendar para deletar em 2 minutos
        if task.task_type == 'unique':
            task.auto_delete_at = datetime.utcnow() + timedelta(minutes=2)
        
        db.session.commit()
        
        return jsonify({
            'task': task.to_dict(),
            'user': user.to_dict(),
            'level_up': level_up,
            'rewards': {
                'xp': base_xp,
                'coins': base_coins
            }
        })
    else:
        return jsonify({'message': 'Tarefa já estava completa'}), 400

@tasks_bp.route('/tasks/<int:task_id>/uncomplete', methods=['POST'])
@cross_origin()
def uncomplete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.completed:
        task.completed = False
        task.completed_at = None
        
        # Para hábitos, ajustar streak se necessário
        if task.task_type == 'habit' and task.streak > 0:
            task.streak -= 1
        
        db.session.commit()
        return jsonify(task.to_dict())
    else:
        return jsonify({'message': 'Tarefa já estava incompleta'}), 400

@tasks_bp.route('/users/<int:user_id>/tasks/reset-dailies', methods=['POST'])
@cross_origin()
def reset_daily_tasks(user_id):
    """Reseta todas as tarefas diárias do usuário"""
    daily_tasks = Task.query.filter_by(user_id=user_id, task_type='daily').all()
    
    for task in daily_tasks:
        task.reset_daily_task()
    
    db.session.commit()
    return jsonify({'message': f'Resetadas {len(daily_tasks)} tarefas diárias'})

def check_achievements(user):
    """Verifica se o usuário desbloqueou novas conquistas"""
    # Buscar todas as conquistas que o usuário ainda não tem
    earned_achievement_ids = [ua.achievement_id for ua in user.achievements]
    available_achievements = Achievement.query.filter(~Achievement.id.in_(earned_achievement_ids)).all()
    
    for achievement in available_achievements:
        earned = False
        
        if achievement.condition_type == 'level_reached':
            earned = user.level >= achievement.condition_value
        elif achievement.condition_type == 'tasks_completed':
            completed_count = Task.query.filter_by(user_id=user.id, completed=True).count()
            earned = completed_count >= achievement.condition_value
        elif achievement.condition_type == 'streak':
            max_streak = db.session.query(db.func.max(Task.streak)).filter_by(
                user_id=user.id, task_type='habit'
            ).scalar() or 0
            earned = max_streak >= achievement.condition_value
        
        if earned:
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id
            )
            db.session.add(user_achievement)
            
            # Adicionar recompensas da conquista
            user.add_xp(achievement.xp_reward)
            user.add_coins(achievement.coin_reward)



@tasks_bp.route('/tasks/cleanup-expired', methods=['POST'])
@cross_origin()
def cleanup_expired_tasks():
    """Remove tarefas únicas que foram marcadas para auto-exclusão"""
    now = datetime.utcnow()
    expired_tasks = Task.query.filter(
        Task.task_type == 'unique',
        Task.auto_delete_at.isnot(None),
        Task.auto_delete_at <= now
    ).all()
    
    deleted_count = len(expired_tasks)
    
    for task in expired_tasks:
        db.session.delete(task)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Removidas {deleted_count} tarefas expiradas',
        'deleted_count': deleted_count
    })

@tasks_bp.route('/users/<int:user_id>/tasks/active', methods=['GET'])
@cross_origin()
def get_active_user_tasks(user_id):
    """Retorna apenas tarefas ativas (não expiradas)"""
    now = datetime.utcnow()
    
    # Buscar tarefas que não estão marcadas para auto-exclusão ou ainda não expiraram
    tasks = Task.query.filter_by(user_id=user_id).filter(
        db.or_(
            Task.auto_delete_at.is_(None),
            Task.auto_delete_at > now
        )
    ).order_by(Task.created_at.desc()).all()
    
    return jsonify([task.to_dict() for task in tasks])

