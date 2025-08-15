from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    coins = db.Column(db.Integer, default=0)
    avatar_stage = db.Column(db.Integer, default=1)
    pet_slots = db.Column(db.Integer, default=1)  # Número de slots de pets desbloqueados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_avatar_stage(self):
        """Determina o estágio do avatar baseado no nível"""
        if self.level >= 50:
            return 8  # Lendário
        elif self.level >= 40:
            return 7  # Mestre
        elif self.level >= 30:
            return 6  # Especialista
        elif self.level >= 20:
            return 5  # Avançado
        elif self.level >= 15:
            return 4  # Intermediário
        elif self.level >= 10:
            return 3  # Experiente
        elif self.level >= 5:
            return 2  # Novato
        else:
            return 1  # Iniciante
    
    def add_xp(self, amount):
        """Adiciona XP e verifica se subiu de nível"""
        self.xp += amount
        old_level = self.level
        
        # Nova progressão de XP para alcançar ~70.000 XP no nível 100
        new_level = 1
        total_xp_needed = 0
        
        # Progressão linear mais suave
        for level in range(1, 101):  # Até nível 100
            # XP necessário para o próximo nível
            xp_for_next_level = 100 + (level - 1) * 10  # Começa com 100, aumenta 10 por nível
            
            if self.xp >= total_xp_needed + xp_for_next_level:
                total_xp_needed += xp_for_next_level
                new_level = level + 1
            else:
                break
        
        self.level = new_level
        self.avatar_stage = self.get_avatar_stage()
        
        return new_level > old_level  # Retorna True se subiu de nível
    
    def add_coins(self, amount):
        """Adiciona moedas"""
        self.coins += amount
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'level': self.level,
            'xp': self.xp,
            'coins': self.coins,
            'avatar_stage': self.avatar_stage,
            'pet_slots': self.pet_slots,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(20), nullable=False)  # 'habit', 'daily', 'unique'
    difficulty = db.Column(db.String(10), default='medium')  # 'easy', 'medium', 'hard'
    xp_reward = db.Column(db.Integer, default=10)
    coin_reward = db.Column(db.Integer, default=5)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date)
    streak = db.Column(db.Integer, default=0)  # Para hábitos
    last_completed = db.Column(db.Date)  # Para controle de streak
    auto_delete_at = db.Column(db.DateTime)  # Para auto-exclusão de missões únicas
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def complete_task(self):
        """Marca a tarefa como completa e atualiza streak se necessário"""
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.utcnow()
            
            # Atualiza streak para hábitos
            if self.task_type == 'habit':
                today = date.today()
                if self.last_completed == today - datetime.timedelta(days=1):
                    self.streak += 1
                elif self.last_completed != today:
                    self.streak = 1
                self.last_completed = today
            
            return True
        return False
    
    def reset_daily_task(self):
        """Reseta tarefa diária para o próximo dia"""
        if self.task_type == 'daily':
            self.completed = False
            self.completed_at = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'difficulty': self.difficulty,
            'xp_reward': self.xp_reward,
            'coin_reward': self.coin_reward,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'streak': self.streak,
            'last_completed': self.last_completed.isoformat() if self.last_completed else None,
            'auto_delete_at': self.auto_delete_at.isoformat() if self.auto_delete_at else None
        }

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    xp_reward = db.Column(db.Integer, default=50)
    coin_reward = db.Column(db.Integer, default=25)
    condition_type = db.Column(db.String(50))  # 'tasks_completed', 'level_reached', 'streak', etc.
    condition_value = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'xp_reward': self.xp_reward,
            'coin_reward': self.coin_reward,
            'condition_type': self.condition_type,
            'condition_value': self.condition_value
        }

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'achievement': self.achievement.to_dict() if self.achievement else None
        }
