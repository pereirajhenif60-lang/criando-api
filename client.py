import requests
from config import Config

class WTTRClient:
    def __init__(self):
        self.base_url = Config.BASE_URL

    def fetch_weather(self, city: str, lang: str = Config.DEFAULT_LANG):
        city = city.strip()
        if not city:
            raise ValueError("Cidade é obrigatória.")

        url = f"{self.base_url}/{city}"
        params = {"format": "j1", "lang": lang}
        headers = {"User-Agent": "weather-app/1.0"}

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()