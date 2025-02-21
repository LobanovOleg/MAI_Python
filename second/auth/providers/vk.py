import requests

class VKAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_auth_url(self):
        return f"https://oauth.vk.com/authorize?client_id={self.client_id}&redirect_uri={self.redirect_uri}&response_type=code"

    def get_token(self, code):
        response = requests.get(
            "https://oauth.vk.com/access_token",
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "code": code,
            },
        )
        return response.json().get("access_token")

    def get_user_info(self, token):
        response = requests.get(
            "https://api.vk.com/method/users.get",
            params={"access_token": token, "v": "5.131"},
        )
        data = response.json().get("response")[0]
        return {
            "id": data["id"],
            "email": f"{data['id']}@vk.ru",
            "first_name": data.get("first_name", "Unknown"),
            "last_name": data.get("last_name", "Unknown")
        }