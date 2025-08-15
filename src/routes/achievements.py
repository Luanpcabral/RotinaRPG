from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.user import User, Achievement, UserAchievement, db

achievements_bp = Blueprint('achievements', __name__)

@achievements_bp.route('/achievements', methods=['GET'])
@cross_origin()
def get_achievements():
    achievements = Achievement.query.all()
    return jsonify([achievement.to_dict() for achievement in achievements])

@achievements_bp.route('/achievements', methods=['POST'])
@cross_origin()
def create_achievement():
    data = request.json
    
    achievement = Achievement(
        name=data['name'],
        description=data.get('description', ''),
        icon=data.get('icon', '🏆'),
        xp_reward=data.get('xp_reward', 50),
        coin_reward=data.get('coin_reward', 25),
        condition_type=data['condition_type'],
        condition_value=data['condition_value']
    )
    
    db.session.add(achievement)
    db.session.commit()
    return jsonify(achievement.to_dict()), 201

@achievements_bp.route('/achievements/<int:achievement_id>', methods=['GET'])
@cross_origin()
def get_achievement(achievement_id):
    achievement = Achievement.query.get_or_404(achievement_id)
    return jsonify(achievement.to_dict())

@achievements_bp.route('/achievements/<int:achievement_id>', methods=['PUT'])
@cross_origin()
def update_achievement(achievement_id):
    achievement = Achievement.query.get_or_404(achievement_id)
    data = request.json
    
    achievement.name = data.get('name', achievement.name)
    achievement.description = data.get('description', achievement.description)
    achievement.icon = data.get('icon', achievement.icon)
    achievement.xp_reward = data.get('xp_reward', achievement.xp_reward)
    achievement.coin_reward = data.get('coin_reward', achievement.coin_reward)
    achievement.condition_type = data.get('condition_type', achievement.condition_type)
    achievement.condition_value = data.get('condition_value', achievement.condition_value)
    
    db.session.commit()
    return jsonify(achievement.to_dict())

@achievements_bp.route('/achievements/<int:achievement_id>', methods=['DELETE'])
@cross_origin()
def delete_achievement(achievement_id):
    achievement = Achievement.query.get_or_404(achievement_id)
    db.session.delete(achievement)
    db.session.commit()
    return '', 204

@achievements_bp.route('/users/<int:user_id>/achievements', methods=['GET'])
@cross_origin()
def get_user_achievements(user_id):
    user = User.query.get_or_404(user_id)
    user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
    
    return jsonify([ua.to_dict() for ua in user_achievements])

@achievements_bp.route('/users/<int:user_id>/achievements/available', methods=['GET'])
@cross_origin()
def get_available_achievements(user_id):
    """Retorna conquistas que o usuário ainda não desbloqueou"""
    user = User.query.get_or_404(user_id)
    
    # IDs das conquistas já desbloqueadas
    earned_achievement_ids = [ua.achievement_id for ua in user.achievements]
    
    # Conquistas disponíveis (não desbloqueadas)
    available_achievements = Achievement.query.filter(
        ~Achievement.id.in_(earned_achievement_ids)
    ).all()
    
    return jsonify([achievement.to_dict() for achievement in available_achievements])

def init_default_achievements():
    """Inicializa conquistas padrão se não existirem"""
    if Achievement.query.count() == 0:
        default_achievements = [
            # Conquistas de Primeiros Passos (5)
            {
                'name': 'Primeiro Passo',
                'description': 'Complete sua primeira tarefa',
                'icon': '🎯',
                'condition_type': 'tasks_completed',
                'condition_value': 1,
                'xp_reward': 25,
                'coin_reward': 10
            },
            {
                'name': 'Começando Bem',
                'description': 'Complete 3 tarefas',
                'icon': '🌟',
                'condition_type': 'tasks_completed',
                'condition_value': 3,
                'xp_reward': 35,
                'coin_reward': 15
            },
            {
                'name': 'Pegando o Ritmo',
                'description': 'Complete 5 tarefas',
                'icon': '⚡',
                'condition_type': 'tasks_completed',
                'condition_value': 5,
                'xp_reward': 45,
                'coin_reward': 20
            },
            {
                'name': 'Primeira Semana',
                'description': 'Complete 7 tarefas',
                'icon': '📅',
                'condition_type': 'tasks_completed',
                'condition_value': 7,
                'xp_reward': 55,
                'coin_reward': 25
            },
            {
                'name': 'Dez é Pouco',
                'description': 'Complete 10 tarefas',
                'icon': '🔟',
                'condition_type': 'tasks_completed',
                'condition_value': 10,
                'xp_reward': 65,
                'coin_reward': 30
            },

            # Conquistas de Produtividade (8)
            {
                'name': 'Produtivo',
                'description': 'Complete 25 tarefas',
                'icon': '💪',
                'condition_type': 'tasks_completed',
                'condition_value': 25,
                'xp_reward': 75,
                'coin_reward': 35
            },
            {
                'name': 'Máquina de Produtividade',
                'description': 'Complete 50 tarefas',
                'icon': '🚀',
                'condition_type': 'tasks_completed',
                'condition_value': 50,
                'xp_reward': 100,
                'coin_reward': 50
            },
            {
                'name': 'Cem Tarefas!',
                'description': 'Complete 100 tarefas',
                'icon': '💯',
                'condition_type': 'tasks_completed',
                'condition_value': 100,
                'xp_reward': 150,
                'coin_reward': 75
            },
            {
                'name': 'Duzentas e Contando',
                'description': 'Complete 200 tarefas',
                'icon': '🎊',
                'condition_type': 'tasks_completed',
                'condition_value': 200,
                'xp_reward': 200,
                'coin_reward': 100
            },
            {
                'name': 'Trezentas Conquistas',
                'description': 'Complete 300 tarefas',
                'icon': '🏆',
                'condition_type': 'tasks_completed',
                'condition_value': 300,
                'xp_reward': 250,
                'coin_reward': 125
            },
            {
                'name': 'Quinhentas!',
                'description': 'Complete 500 tarefas',
                'icon': '👑',
                'condition_type': 'tasks_completed',
                'condition_value': 500,
                'xp_reward': 300,
                'coin_reward': 150
            },
            {
                'name': 'Mil Tarefas',
                'description': 'Complete 1000 tarefas',
                'icon': '🌟',
                'condition_type': 'tasks_completed',
                'condition_value': 1000,
                'xp_reward': 500,
                'coin_reward': 250
            },
            {
                'name': 'Lenda da Produtividade',
                'description': 'Complete 2000 tarefas',
                'icon': '🦄',
                'condition_type': 'tasks_completed',
                'condition_value': 2000,
                'xp_reward': 1000,
                'coin_reward': 500
            },

            # Conquistas de Níveis (8)
            {
                'name': 'Novato',
                'description': 'Alcance o nível 5',
                'icon': '🌱',
                'condition_type': 'level_reached',
                'condition_value': 5,
                'xp_reward': 50,
                'coin_reward': 25
            },
            {
                'name': 'Aprendiz',
                'description': 'Alcance o nível 10',
                'icon': '🌿',
                'condition_type': 'level_reached',
                'condition_value': 10,
                'xp_reward': 75,
                'coin_reward': 35
            },
            {
                'name': 'Experiente',
                'description': 'Alcance o nível 15',
                'icon': '🌳',
                'condition_type': 'level_reached',
                'condition_value': 15,
                'xp_reward': 100,
                'coin_reward': 50
            },
            {
                'name': 'Veterano',
                'description': 'Alcance o nível 25',
                'icon': '🏔️',
                'condition_type': 'level_reached',
                'condition_value': 25,
                'xp_reward': 150,
                'coin_reward': 75
            },
            {
                'name': 'Especialista',
                'description': 'Alcance o nível 35',
                'icon': '⭐',
                'condition_type': 'level_reached',
                'condition_value': 35,
                'xp_reward': 200,
                'coin_reward': 100
            },
            {
                'name': 'Mestre',
                'description': 'Alcance o nível 50',
                'icon': '🎖️',
                'condition_type': 'level_reached',
                'condition_value': 50,
                'xp_reward': 300,
                'coin_reward': 150
            },
            {
                'name': 'Grão-Mestre',
                'description': 'Alcance o nível 75',
                'icon': '🏅',
                'condition_type': 'level_reached',
                'condition_value': 75,
                'xp_reward': 400,
                'coin_reward': 200
            },
            {
                'name': 'Lendário',
                'description': 'Alcance o nível 100',
                'icon': '👑',
                'condition_type': 'level_reached',
                'condition_value': 100,
                'xp_reward': 500,
                'coin_reward': 250
            },

            # Conquistas de Produtividade Geral (8)
            {
                'name': 'Primeira Conquista!',
                'description': 'Desbloqueie sua primeira conquista',
                'icon': '⭐',
                'condition_type': 'achievements_unlocked',
                'condition_value': 1,
                'xp_reward': 20,
                'coin_reward': 10
            },
            {
                'name': 'Colecionador de Conquistas',
                'description': 'Desbloqueie 5 conquistas',
                'icon': '🏅',
                'condition_type': 'achievements_unlocked',
                'condition_value': 5,
                'xp_reward': 50,
                'coin_reward': 25
            },
            {
                'name': 'Mestre das Conquistas',
                'description': 'Desbloqueie 10 conquistas',
                'icon': '🏆',
                'condition_type': 'achievements_unlocked',
                'condition_value': 10,
                'xp_reward': 100,
                'coin_reward': 50
            },
            {
                'name': 'Comprador Compulsivo',
                'description': 'Compre 3 itens na loja',
                'icon': '🛍️',
                'condition_type': 'items_bought',
                'condition_value': 3,
                'xp_reward': 60,
                'coin_reward': 30
            },
            {
                'name': 'Cliente VIP',
                'description': 'Compre 10 itens na loja',
                'icon': '💎',
                'condition_type': 'items_bought',
                'condition_value': 10,
                'xp_reward': 120,
                'coin_reward': 60
            },
            {
                'name': 'Gastador Nato',
                'description': 'Gaste 500 moedas na loja',
                'icon': '💸',
                'condition_type': 'coins_spent',
                'condition_value': 500,
                'xp_reward': 150,
                'coin_reward': 75
            },
            {
                'name': 'Economista Produtivo',
                'description': 'Gaste 1000 moedas na loja',
                'icon': '💰',
                'condition_type': 'coins_spent',
                'condition_value': 1000,
                'xp_reward': 250,
                'coin_reward': 125
            },
            {
                'name': 'Ouro na Mão',
                'description': 'Gaste 5000 moedas na loja',
                'icon': '👑',
                'condition_type': 'coins_spent',
                'condition_value': 5000,
                'xp_reward': 500,
                'coin_reward': 250
            },

            # Conquistas de Moedas (6)
            {
                'name': 'Primeiro Tesouro',
                'description': 'Acumule 100 moedas',
                'icon': '🪙',
                'condition_type': 'coins_earned',
                'condition_value': 100,
                'xp_reward': 50,
                'coin_reward': 25
            },
            {
                'name': 'Rico',
                'description': 'Acumule 500 moedas',
                'icon': '💰',
                'condition_type': 'coins_earned',
                'condition_value': 500,
                'xp_reward': 100,
                'coin_reward': 50
            },
            {
                'name': 'Milionário',
                'description': 'Acumule 1000 moedas',
                'icon': '💎',
                'condition_type': 'coins_earned',
                'condition_value': 1000,
                'xp_reward': 150,
                'coin_reward': 75
            },
            {
                'name': 'Colecionador de Ouro',
                'description': 'Acumule 2500 moedas',
                'icon': '🏆',
                'condition_type': 'coins_earned',
                'condition_value': 2500,
                'xp_reward': 250,
                'coin_reward': 125
            },
            {
                'name': 'Tesouro do Dragão',
                'description': 'Acumule 5000 moedas',
                'icon': '🐉',
                'condition_type': 'coins_earned',
                'condition_value': 5000,
                'xp_reward': 400,
                'coin_reward': 200
            },
            {
                'name': 'Rei Midas',
                'description': 'Acumule 10000 moedas',
                'icon': '👑',
                'condition_type': 'coins_earned',
                'condition_value': 10000,
                'xp_reward': 750,
                'coin_reward': 375
            },

            # Conquistas Especiais/Criativas (5)
            {
                'name': 'Madrugador',
                'description': 'Complete uma tarefa antes das 6h da manhã',
                'icon': '🌅',
                'condition_type': 'early_bird',
                'condition_value': 1,
                'xp_reward': 75,
                'coin_reward': 40
            },
            {
                'name': 'Coruja Noturna',
                'description': 'Complete uma tarefa depois das 23h',
                'icon': '🦉',
                'condition_type': 'night_owl',
                'condition_value': 1,
                'xp_reward': 75,
                'coin_reward': 40
            },
            {
                'name': 'Fim de Semana Produtivo',
                'description': 'Complete 5 tarefas no fim de semana',
                'icon': '🎉',
                'condition_type': 'weekend_warrior',
                'condition_value': 5,
                'xp_reward': 100,
                'coin_reward': 50
            },
            {
                'name': 'Velocista',
                'description': 'Complete 10 tarefas em um único dia',
                'icon': '⚡',
                'condition_type': 'daily_sprint',
                'condition_value': 10,
                'xp_reward': 150,
                'coin_reward': 75
            },
            {
                'name': 'Perfeccionista',
                'description': 'Complete todas as tarefas diárias por 7 dias seguidos',
                'icon': '✨',
                'condition_type': 'perfect_week',
                'condition_value': 7,
                'xp_reward': 200,
                'coin_reward': 100
            }
        ]
        
        for achievement_data in default_achievements:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
        
        db.session.commit()
        print("Conquistas padrão inicializadas!")

