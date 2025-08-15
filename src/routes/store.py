from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.user import db, User
from src.models.store import StoreItem, Purchase

store_bp = Blueprint('store', __name__)

# Listar todos os itens da loja ativos
@store_bp.route('/store/items', methods=['GET'])
@cross_origin()
def get_store_items():
    items = StoreItem.query.filter_by(is_active=True).all()
    return jsonify([item.to_dict() for item in items])

# Criar novo item na loja
@store_bp.route('/store/items', methods=['POST'])
@cross_origin()
def create_store_item():
    data = request.get_json()
    
    if not data.get('name') or not data.get('price'):
        return jsonify({'error': 'Nome e preço são obrigatórios'}), 400
    
    item = StoreItem(
        name=data['name'],
        description=data.get('description', ''),
        price=int(data['price']),
        icon=data.get('icon', '🎁')
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify(item.to_dict()), 201

# Atualizar item da loja
@store_bp.route('/store/items/<int:item_id>', methods=['PUT'])
@cross_origin()
def update_store_item(item_id):
    item = StoreItem.query.get_or_404(item_id)
    data = request.get_json()
    
    if 'name' in data:
        item.name = data['name']
    if 'description' in data:
        item.description = data['description']
    if 'price' in data:
        item.price = int(data['price'])
    if 'icon' in data:
        item.icon = data['icon']
    if 'is_active' in data:
        item.is_active = data['is_active']
    
    db.session.commit()
    return jsonify(item.to_dict())

# Deletar item da loja
@store_bp.route('/store/items/<int:item_id>', methods=['DELETE'])
@cross_origin()
def delete_store_item(item_id):
    item = StoreItem.query.get_or_404(item_id)
    item.is_active = False  # Soft delete
    db.session.commit()
    return jsonify({'message': 'Item removido da loja'})

# Comprar item
@store_bp.route('/users/<int:user_id>/purchase', methods=['POST'])
@cross_origin()
def purchase_item(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    if not item_id:
        return jsonify({'error': 'ID do item é obrigatório'}), 400
    
    item = StoreItem.query.get_or_404(item_id)
    
    if not item.is_active:
        return jsonify({'error': 'Item não está disponível'}), 400
    
    # Aplicar desconto do pet equipado
    from src.models.pet import UserPet
    equipped_pet = UserPet.query.filter_by(user_id=user.id, is_equipped=True).first()
    
    base_price = item.price
    final_price = base_price
    discount_applied = 0
    
    if equipped_pet:
        effects = equipped_pet.get_current_effects()
        if 'store_discount' in effects:
            discount = effects['store_discount']
            final_price = int(base_price * (1 - discount))
            discount_applied = base_price - final_price
    
    total_cost = final_price * quantity
    
    if user.coins < total_cost:
        return jsonify({'error': 'Moedas insuficientes'}), 400
    
    # Realizar compra
    user.coins -= total_cost
    
    purchase = Purchase(
        user_id=user_id,
        store_item_id=item_id,
        quantity=quantity,
        total_cost=total_cost
    )
    
    db.session.add(purchase)
    db.session.commit()
    
    return jsonify({
        'message': 'Compra realizada com sucesso!',
        'purchase': purchase.to_dict(),
        'user': user.to_dict(),
        'original_price': base_price,
        'final_price': final_price,
        'discount_applied': discount_applied
    })

# Listar compras do usuário
@store_bp.route('/users/<int:user_id>/purchases', methods=['GET'])
@cross_origin()
def get_user_purchases(user_id):
    purchases = Purchase.query.filter_by(user_id=user_id).order_by(Purchase.purchased_at.desc()).all()
    return jsonify([purchase.to_dict() for purchase in purchases])

# Resgatar item comprado
@store_bp.route('/purchases/<int:purchase_id>/redeem', methods=['POST'])
@cross_origin()
def redeem_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    
    if purchase.is_redeemed:
        return jsonify({'error': 'Item já foi resgatado'}), 400
    
    purchase.is_redeemed = True
    purchase.redeemed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Item resgatado com sucesso!',
        'purchase': purchase.to_dict()
    })

# Listar itens não resgatados do usuário
@store_bp.route('/users/<int:user_id>/inventory', methods=['GET'])
@cross_origin()
def get_user_inventory(user_id):
    purchases = Purchase.query.filter_by(user_id=user_id, is_redeemed=False).order_by(Purchase.purchased_at.desc()).all()
    return jsonify([purchase.to_dict() for purchase in purchases])

