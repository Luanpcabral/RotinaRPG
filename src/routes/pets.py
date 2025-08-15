import random
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.user import db, User
from src.models.pet import Pet, UserPet, PetBoxOpening

pets_bp = Blueprint('pets', __name__)

# Probabilidades de raridade
RARITY_PROBABILITIES = {
    'common': 0.60,      # 60%
    'rare': 0.25,        # 25%
    'epic': 0.125,       # 12.5%
    'legendary': 0.025   # 2.5%
}

# Listar todos os pets disponíveis
@pets_bp.route('/pets', methods=['GET'])
@cross_origin()
def get_all_pets():
    pets = Pet.query.all()
    return jsonify([pet.to_dict() for pet in pets])

# Listar pets do usuário
@pets_bp.route('/users/<int:user_id>/pets', methods=['GET'])
@cross_origin()
def get_user_pets(user_id):
    user_pets = UserPet.query.filter_by(user_id=user_id).all()
    return jsonify([user_pet.to_dict() for user_pet in user_pets])

# Obter pet equipado do usuário
@pets_bp.route('/users/<int:user_id>/pets/equipped', methods=['GET'])
@cross_origin()
def get_equipped_pet(user_id):
    equipped_pet = UserPet.query.filter_by(user_id=user_id, is_equipped=True).first()
    if equipped_pet:
        return jsonify(equipped_pet.to_dict())
    return jsonify(None)

# Equipar pet
@pets_bp.route('/users/<int:user_id>/pets/<int:user_pet_id>/equip', methods=['POST'])
@cross_origin()
def equip_pet(user_id, user_pet_id):
    # Desequipar pet atual
    current_equipped = UserPet.query.filter_by(user_id=user_id, is_equipped=True).first()
    if current_equipped:
        current_equipped.is_equipped = False
    
    # Equipar novo pet
    user_pet = UserPet.query.filter_by(id=user_pet_id, user_id=user_id).first()
    if not user_pet:
        return jsonify({'error': 'Pet não encontrado'}), 404
    
    user_pet.is_equipped = True
    db.session.commit()
    
    return jsonify({
        'message': 'Pet equipado com sucesso!',
        'equipped_pet': user_pet.to_dict()
    })

# Desequipar pet
@pets_bp.route('/users/<int:user_id>/pets/unequip', methods=['POST'])
@cross_origin()
def unequip_pet(user_id):
    equipped_pet = UserPet.query.filter_by(user_id=user_id, is_equipped=True).first()
    if equipped_pet:
        equipped_pet.is_equipped = False
        db.session.commit()
        return jsonify({'message': 'Pet desequipado com sucesso!'})
    
    return jsonify({'message': 'Nenhum pet equipado'}), 400

# Abrir caixa misteriosa de pet
@pets_bp.route('/users/<int:user_id>/pets/open-box', methods=['POST'])
@cross_origin()
def open_pet_box(user_id):
    try:
        data = request.get_json() or {}
        box_type = data.get('box_type', 'basic')  # 'basic' ou 'luxury'
        
        user = User.query.get_or_404(user_id)
        
        # Definir preço e probabilidades baseado no tipo de caixa
        if box_type == 'luxury':
            box_price = 500
            probabilities = {
                'common': 0.0,    # 0% de chance
                'rare': 0.5,      # 50% de chance
                'epic': 0.4,      # 40% de chance
                'legendary': 0.1  # 10% de chance
            }
        else:  # basic
            box_price = 200
            probabilities = {
                'common': 0.60,   # 60% de chance
                'rare': 0.25,     # 25% de chance
                'epic': 0.125,    # 12.5% de chance
                'legendary': 0.025 # 2.5% de chance
            }
        
        # Verificar se o usuário tem moedas suficientes
        if user.coins < box_price:
            return jsonify({'error': f'Moedas insuficientes. Necessário: {box_price}'}), 400
        
        # Deduzir moedas
        user.coins -= box_price
        
        # Selecionar pet baseado na probabilidade
        selected_pet = select_random_pet_with_probabilities(user_id, probabilities)
        if not selected_pet:
            return jsonify({'error': 'Nenhum pet disponível'}), 400
        
        # Verificar se o usuário já tem este pet
        existing_user_pet = UserPet.query.filter_by(user_id=user_id, pet_id=selected_pet.id).first()
        
        was_duplicate = False
        level_gained = 1
        
        if existing_user_pet:
            # Pet duplicado - aumentar nível
            if existing_user_pet.level < 25:  # Nível máximo
                existing_user_pet.level += 1
                level_gained = existing_user_pet.level
                was_duplicate = True
                user_pet = existing_user_pet
            else:
                # Pet já está no nível máximo, selecionar outro
                return open_pet_box(user_id)  # Recursão para tentar novamente
        else:
            # Novo pet
            user_pet = UserPet(
                user_id=user_id,
                pet_id=selected_pet.id,
                level=1
            )
            db.session.add(user_pet)
        
        # Registrar abertura da caixa
        box_opening = PetBoxOpening(
            user_id=user_id,
            pet_id=selected_pet.id,
            box_type=box_type,
            was_duplicate=was_duplicate,
            level_gained=level_gained
        )
        db.session.add(box_opening)
        
        db.session.commit()
        
        # Calcular efeitos atuais do pet
        current_effects = {}
        for effect_name, base_value in selected_pet.base_effects.items():
            current_effects[effect_name] = base_value * level_gained
        
        return jsonify({
            'success': True,
            'pet': {
                'id': selected_pet.id,
                'name': selected_pet.name,
                'rarity': selected_pet.rarity,
                'sprite_path': selected_pet.sprite_path,
                'base_effects': selected_pet.base_effects
            },
            'was_duplicate': was_duplicate,
            'level_gained': level_gained,
            'current_effects': current_effects,
            'box_type': box_type,
            'user_coins': user.coins
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def select_random_pet_with_probabilities(user_id, probabilities):
    """Seleciona um pet aleatório baseado nas probabilidades customizadas, excluindo pets no nível máximo"""
    
    # Obter pets que o usuário já tem no nível máximo
    max_level_pets = db.session.query(UserPet.pet_id).filter_by(user_id=user_id, level=25).all()
    max_level_pet_ids = [pet.pet_id for pet in max_level_pets]
    
    # Obter pets disponíveis (excluindo os de nível máximo)
    available_pets = Pet.query.filter(~Pet.id.in_(max_level_pet_ids)).all()
    
    if not available_pets:
        return None
    
    # Agrupar pets por raridade
    pets_by_rarity = {
        'common': [p for p in available_pets if p.rarity == 'common'],
        'rare': [p for p in available_pets if p.rarity == 'rare'],
        'epic': [p for p in available_pets if p.rarity == 'epic'],
        'legendary': [p for p in available_pets if p.rarity == 'legendary']
    }
    
    # Selecionar raridade baseada na probabilidade customizada
    rand = random.random()
    cumulative_prob = 0
    
    for rarity, prob in probabilities.items():
        cumulative_prob += prob
        if rand <= cumulative_prob and pets_by_rarity[rarity]:
            return random.choice(pets_by_rarity[rarity])
    
    # Fallback - selecionar qualquer pet disponível
    return random.choice(available_pets)

def select_random_pet(user_id):
    """Seleciona um pet aleatório baseado nas probabilidades, excluindo pets no nível máximo"""
    
    # Obter pets que o usuário já tem no nível máximo
    max_level_pets = db.session.query(UserPet.pet_id).filter_by(user_id=user_id, level=25).all()
    max_level_pet_ids = [pet.pet_id for pet in max_level_pets]
    
    # Obter pets disponíveis (excluindo os de nível máximo)
    available_pets = Pet.query.filter(~Pet.id.in_(max_level_pet_ids)).all()
    
    if not available_pets:
        return None
    
    # Agrupar pets por raridade
    pets_by_rarity = {
        'common': [p for p in available_pets if p.rarity == 'common'],
        'rare': [p for p in available_pets if p.rarity == 'rare'],
        'epic': [p for p in available_pets if p.rarity == 'epic'],
        'legendary': [p for p in available_pets if p.rarity == 'legendary']
    }
    
    # Selecionar raridade baseada na probabilidade
    rand = random.random()
    cumulative_prob = 0
    
    for rarity, prob in RARITY_PROBABILITIES.items():
        cumulative_prob += prob
        if rand <= cumulative_prob and pets_by_rarity[rarity]:
            return random.choice(pets_by_rarity[rarity])
    
    # Fallback - selecionar qualquer pet disponível
    return random.choice(available_pets)

# Histórico de aberturas de caixa
@pets_bp.route('/users/<int:user_id>/pets/box-history', methods=['GET'])
@cross_origin()
def get_box_history(user_id):
    history = PetBoxOpening.query.filter_by(user_id=user_id).order_by(PetBoxOpening.opened_at.desc()).limit(20).all()
    return jsonify([opening.to_dict() for opening in history])

# Estatísticas de pets do usuário
@pets_bp.route('/users/<int:user_id>/pets/stats', methods=['GET'])
@cross_origin()
def get_pet_stats(user_id):
    user_pets = UserPet.query.filter_by(user_id=user_id).all()
    
    stats = {
        'total_pets': len(user_pets),
        'pets_by_rarity': {
            'common': len([p for p in user_pets if p.pet.rarity == 'common']),
            'rare': len([p for p in user_pets if p.pet.rarity == 'rare']),
            'epic': len([p for p in user_pets if p.pet.rarity == 'epic']),
            'legendary': len([p for p in user_pets if p.pet.rarity == 'legendary'])
        },
        'max_level_pets': len([p for p in user_pets if p.level == 25]),
        'equipped_pet': None
    }
    
    equipped_pet = UserPet.query.filter_by(user_id=user_id, is_equipped=True).first()
    if equipped_pet:
        stats['equipped_pet'] = equipped_pet.to_dict()
    
    return jsonify(stats)


# Comprar slot de pet
@pets_bp.route('/users/<int:user_id>/pets/buy-slot', methods=['POST'])
@cross_origin()
def buy_pet_slot(user_id):
    user = User.query.get_or_404(user_id)
    
    # Definir preços dos slots
    slot_prices = {
        2: 3000,   # Segundo slot custa 3000 moedas
        3: 10000   # Terceiro slot custa 10000 moedas
    }
    
    # Verificar qual slot o usuário está tentando comprar
    next_slot = user.pet_slots + 1
    
    if next_slot > 3:
        return jsonify({'error': 'Número máximo de slots já atingido'}), 400
    
    slot_price = slot_prices.get(next_slot)
    if not slot_price:
        return jsonify({'error': 'Slot inválido'}), 400
    
    # Verificar se o usuário tem moedas suficientes
    if user.coins < slot_price:
        return jsonify({'error': f'Moedas insuficientes. Necessário: {slot_price}'}), 400
    
    # Deduzir moedas e adicionar slot
    user.coins -= slot_price
    user.pet_slots += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Slot {next_slot} comprado com sucesso!',
        'new_slot_count': user.pet_slots,
        'remaining_coins': user.coins
    })

# Obter pets equipados (todos os slots)
@pets_bp.route('/users/<int:user_id>/pets/equipped-all', methods=['GET'])
@cross_origin()
def get_all_equipped_pets(user_id):
    equipped_pets = UserPet.query.filter_by(user_id=user_id, is_equipped=True).order_by(UserPet.slot_position).all()
    return jsonify([pet.to_dict() for pet in equipped_pets])

# Equipar pet em slot específico
@pets_bp.route('/users/<int:user_id>/pets/<int:user_pet_id>/equip-slot/<int:slot>', methods=['POST'])
@cross_origin()
def equip_pet_in_slot(user_id, user_pet_id, slot):
    user = User.query.get_or_404(user_id)
    
    # Verificar se o slot é válido
    if slot < 1 or slot > user.pet_slots:
        return jsonify({'error': f'Slot inválido. Você tem {user.pet_slots} slots disponíveis'}), 400
    
    # Verificar se o pet existe e pertence ao usuário
    user_pet = UserPet.query.filter_by(id=user_pet_id, user_id=user_id).first()
    if not user_pet:
        return jsonify({'error': 'Pet não encontrado'}), 404
    
    # Desequipar pet que está no slot desejado
    current_pet_in_slot = UserPet.query.filter_by(user_id=user_id, slot_position=slot, is_equipped=True).first()
    if current_pet_in_slot:
        current_pet_in_slot.is_equipped = False
        current_pet_in_slot.slot_position = None
    
    # Desequipar o pet se ele já estiver equipado em outro slot
    if user_pet.is_equipped:
        user_pet.is_equipped = False
        user_pet.slot_position = None
    
    # Equipar pet no slot desejado
    user_pet.is_equipped = True
    user_pet.slot_position = slot
    
    db.session.commit()
    
    return jsonify({
        'message': f'Pet equipado no slot {slot} com sucesso!',
        'equipped_pet': user_pet.to_dict()
    })

# Desequipar pet de slot específico
@pets_bp.route('/users/<int:user_id>/pets/unequip-slot/<int:slot>', methods=['POST'])
@cross_origin()
def unequip_pet_from_slot(user_id, slot):
    user = User.query.get_or_404(user_id)
    
    # Verificar se o slot é válido
    if slot < 1 or slot > user.pet_slots:
        return jsonify({'error': f'Slot inválido. Você tem {user.pet_slots} slots disponíveis'}), 400
    
    # Encontrar pet no slot
    pet_in_slot = UserPet.query.filter_by(user_id=user_id, slot_position=slot, is_equipped=True).first()
    if not pet_in_slot:
        return jsonify({'error': f'Nenhum pet equipado no slot {slot}'}), 400
    
    # Desequipar pet
    pet_in_slot.is_equipped = False
    pet_in_slot.slot_position = None
    
    db.session.commit()
    
    return jsonify({
        'message': f'Pet desequipado do slot {slot} com sucesso!'
    })

# Obter informações dos slots disponíveis
@pets_bp.route('/users/<int:user_id>/pets/slots-info', methods=['GET'])
@cross_origin()
def get_slots_info(user_id):
    user = User.query.get_or_404(user_id)
    
    slot_prices = {
        2: 3000,   # Segundo slot custa 3000 moedas
        3: 10000   # Terceiro slot custa 10000 moedas
    }
    
    slots_info = {
        'current_slots': user.pet_slots,
        'max_slots': 3,
        'next_slot_price': slot_prices.get(user.pet_slots + 1),
        'can_buy_next_slot': user.pet_slots < 3 and user.coins >= slot_prices.get(user.pet_slots + 1, 0)
    }
    
    return jsonify(slots_info)

