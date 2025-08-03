import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from src.routes.path_routes import path_bp
from src.utils.data_loader import load_dataset

load_dotenv()

app = Flask(__name__)
app.config['ROUTE_CACHE'] = {}

try:
    gebco_path = os.getenv('GEBCO_FILE_PATH')
    if not gebco_path or not os.path.exists(gebco_path):
        raise FileNotFoundError(f"GEBCO file not found at path: {gebco_path}")
    
    app.config['GEBCO_DATASET'] = load_dataset(gebco_path)

except Exception as e:
    app.config['GEBCO_DATASET'] = None

app.register_blueprint(path_bp, url_prefix='/path')

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)