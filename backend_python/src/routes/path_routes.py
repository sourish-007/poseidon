from flask import Blueprint
from src.controllers.path_controller import find_path_controller

path_bp = Blueprint('path_routes', __name__)

path_bp.route('/find', methods=['POST'])(find_path_controller)