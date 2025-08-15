from flask import Blueprint, jsonify
from flask_cors import cross_origin
from src.utils.daily_reset import get_time_until_reset

timer_bp = Blueprint('timer', __name__)

@timer_bp.route('/timer/daily-reset', methods=['GET'])
@cross_origin()
def get_daily_reset_timer():
    """Retorna o tempo restante até o próximo reset diário"""
    time_info = get_time_until_reset()
    return jsonify(time_info)

