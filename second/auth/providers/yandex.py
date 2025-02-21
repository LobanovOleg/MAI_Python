import requests
from auth.utils import get_user_info

class YandexAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_auth_url(self):
        return f"https://oauth.yandex.ru/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}"

    def get_token(self, code):
        try:
            response = requests.post(
                "https://oauth.yandex.ru/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                },
            )
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            print("Yandex token error:", e)
            return None

    def get_user_info(self, token):
        response = requests.get(
            "https://login.yandex.ru/info",
            headers={"Authorization": f"OAuth {token}"},
        )
        data = response.json()
        return {
            "id": data["id"],
            "login": data["login"],
            "real_name": data.get("real_name", "Unknown")
        }