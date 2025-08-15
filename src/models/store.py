from datetime import datetime
from src.models.user import db

class StoreItem(db.Model):
    __tablename__ = 'store_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)  # Preço em moedas
    icon = db.Column(db.String(10), default='🎁')  # Emoji para o ícone
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'icon': self.icon,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Purchase(db.Model):
    __tablename__ = 'purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    store_item_id = db.Column(db.Integer, db.ForeignKey('store_items.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_cost = db.Column(db.Integer, nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_redeemed = db.Column(db.Boolean, default=False)
    redeemed_at = db.Column(db.DateTime)
    
    # Relacionamentos
    user = db.relationship('User', backref='purchases')
    store_item = db.relationship('StoreItem', backref='purchases')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'store_item': self.store_item.to_dict() if self.store_item else None,
            'quantity': self.quantity,
            'total_cost': self.total_cost,
            'purchased_at': self.purchased_at.isoformat() if self.purchased_at else None,
            'is_redeemed': self.is_redeemed,
            'redeemed_at': self.redeemed_at.isoformat() if self.redeemed_at else None
        }

