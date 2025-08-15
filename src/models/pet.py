from datetime import datetime
from src.models.user import db, User

class Pet(db.Model):
    __tablename__ = 'pets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rarity = db.Column(db.String(20), nullable=False)  # common, rare, epic, legendary
    sprite_path = db.Column(db.String(200), nullable=False)
    base_effects = db.Column(db.JSON, nullable=False)  # JSON com os efeitos base
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com pets do usuário
    user_pets = db.relationship('UserPet', backref='pet', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'rarity': self.rarity,
            'sprite_path': self.sprite_path,
            'base_effects': self.base_effects,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserPet(db.Model):
    __tablename__ = 'user_pets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    level = db.Column(db.Integer, default=1)
    is_equipped = db.Column(db.Boolean, default=False)
    slot_position = db.Column(db.Integer, default=None)  # 1, 2, ou 3 para indicar qual slot
    obtained_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='user_pets')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'pet_id': self.pet_id,
            'pet': self.pet.to_dict() if self.pet else None,
            'level': self.level,
            'is_equipped': self.is_equipped,
            'slot_position': self.slot_position,
            'obtained_at': self.obtained_at.isoformat() if self.obtained_at else None,
            'current_effects': self.get_current_effects()
        }
    
    def get_current_effects(self):
        """Calcula os efeitos atuais baseados no nível do pet"""
        if not self.pet:
            return {}
        
        try:
            base_effects = self.pet.base_effects or {}
            current_effects = {}
            
            # Multiplica os efeitos base pelo nível
            for effect, value in base_effects.items():
                if isinstance(value, (int, float)):
                    current_effects[effect] = value * self.level
                else:
                    current_effects[effect] = value
            
            return current_effects
        except Exception as e:
            print(f"Erro ao calcular efeitos do pet: {e}")
            return {}

class PetBoxOpening(db.Model):
    __tablename__ = 'pet_box_openings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    box_type = db.Column(db.String(20), default='basic')  # 'basic' ou 'luxury'
    was_duplicate = db.Column(db.Boolean, default=False)
    level_gained = db.Column(db.Integer, default=1)  # Nível que o pet ficou após a abertura
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='pet_box_openings')
    pet = db.relationship('Pet', backref='box_openings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'pet_id': self.pet_id,
            'pet': self.pet.to_dict() if self.pet else None,
            'box_type': self.box_type,
            'was_duplicate': self.was_duplicate,
            'level_gained': self.level_gained,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None
        }

