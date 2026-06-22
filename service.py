from weather.client import WTTRClient
from config import Config

class WeatherService:
    GOIAS_CITIES = Config.GOIAS_CITIES
    INVALID_CITY_NAMES = {"shouchengfen"}

    def __init__(self):
        self.client = WTTRClient()

    def _normalize(self, data: dict, query: str = ""):
        current = data.get("current_condition", [{}])[0]
        area = data.get("nearest_area", [{}])[0]

        city_name = area.get("areaName", [{}])[0].get("value")
        if city_name and city_name.lower() in self.INVALID_CITY_NAMES:
            city_name = query

        return {
            "cidade": city_name,
            "pais": area.get("country", [{}])[0].get("value"),
            "temperatura": current.get("temp_C"),
            "sensacao_termica": current.get("FeelsLikeC"),
            "descricao": current.get("weatherDesc", [{}])[0].get("value"),
            "umidade": current.get("humidity"),
            "vento_kmph": current.get("windspeedKmph"),
        }

    def get_weather_by_city(self, city: str, state: str = ""):
        if not city:
            raise ValueError("Cidade é obrigatória.")
        query = city.strip()
        if state:
            query = f"{query},{state.strip()}"
        data = self.client.fetch_weather(query)
        return self._normalize(data, query)

    def get_weather_for_goias(self):
        resultados = []
        for city in self.GOIAS_CITIES:
            try:
                data = self.client.fetch_weather(city)
                resultados.append(self._normalize(data, city))
            except Exception as e:
                resultados.append({
                    "cidade": city,
                    "erro": f"Não foi possível obter os dados: {str(e)}"
                })
        return resultados