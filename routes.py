from pathlib import Path
from flask import Flask, Blueprint, jsonify, render_template, request
from weather.service import WeatherService

BASE_DIR = Path(__file__).resolve().parent.parent
service = WeatherService()
weather_blueprint = Blueprint("weather", __name__)

@weather_blueprint.route("/")
def home():
    return render_template("index.html")

@weather_blueprint.route("/api/weather/goias")
def weather_goias():
    return jsonify(service.get_weather_for_goias())

@weather_blueprint.route("/api/weather")
def weather_api():
    city = request.args.get("city", "").strip()
    state = request.args.get("state", "").strip()
    if not city:
        return jsonify({"erro": "Parâmetro 'city' é obrigatório."}), 400
    try:
        resultado = service.get_weather_by_city(city, state)
        return jsonify(resultado)
    except Exception as exc:
        return jsonify({"erro": str(exc)}), 500

def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.register_blueprint(weather_blueprint)
    return app