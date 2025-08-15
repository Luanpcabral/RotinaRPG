from datetime import datetime, timezone, timedelta
from src.models.user import db, Task
import threading
import time

# Timezone UTC-3 (Brasil)
BRAZIL_TZ = timezone(timedelta(hours=-3))

def reset_daily_tasks():
    """Reseta todas as tarefas diárias para não completadas"""
    try:
        # Buscar todas as tarefas diárias
        daily_tasks = Task.query.filter_by(task_type='daily').all()
        
        for task in daily_tasks:
            task.completed = False
            task.completed_at = None
        
        db.session.commit()
        print(f"Reset diário executado às {datetime.now(BRAZIL_TZ).strftime('%Y-%m-%d %H:%M:%S')} (UTC-3)")
        
    except Exception as e:
        print(f"Erro no reset diário: {e}")
        db.session.rollback()

def get_next_midnight_brazil():
    """Retorna o próximo horário de meia-noite no fuso horário do Brasil"""
    now = datetime.now(BRAZIL_TZ)
    next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return next_midnight

def seconds_until_next_midnight():
    """Retorna quantos segundos faltam para a próxima meia-noite"""
    now = datetime.now(BRAZIL_TZ)
    next_midnight = get_next_midnight_brazil()
    return (next_midnight - now).total_seconds()

def schedule_daily_reset():
    """Agenda o reset diário para executar à meia-noite"""
    def run_scheduler():
        while True:
            # Calcular segundos até a próxima meia-noite
            seconds_to_wait = seconds_until_next_midnight()
            
            print(f"Próximo reset diário em {seconds_to_wait/3600:.1f} horas")
            
            # Aguardar até a meia-noite
            time.sleep(seconds_to_wait)
            
            # Executar reset
            reset_daily_tasks()
    
    # Executar em thread separada para não bloquear a aplicação
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Agendador de reset diário iniciado!")

def get_time_until_reset():
    """Retorna o tempo restante até o próximo reset em formato legível"""
    seconds = seconds_until_next_midnight()
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    
    return {
        'hours': hours,
        'minutes': minutes,
        'total_seconds': int(seconds)
    }

