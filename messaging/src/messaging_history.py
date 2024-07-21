import requests

class MessagingHistory:

    def __init__(self):
        pass

    def get_chats(self, request):

        cookies = request.COOKIES

        url = "https://fusionworks-dev-api.cloudjet.site/chat/history"
        params = {
            "queryType": "database",
        }
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"jwt={cookies.get('jwt')}"
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code in [200, 202]:
            data = response.json()
            if data['data'] is None:
                return []
            print(data['data'])
            return data['data']['messages']
        else:
            print(f"Request failed with status code {response.status_code}")

    def add_new_chat(self, request, user_msg, ai_msg):

        cookies = request.COOKIES
        
        url = "https://fusionworks-dev-api.cloudjet.site/chat/history"
        payload = {
            "queryType": "database",
            "messages": [
                {
                    "sender": "Human",
                    "message": user_msg,
                },
                {
                    "sender": "System",
                    "message": ai_msg,
                }
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"jwt={cookies.get('jwt')}"
        }

        response = requests.put(url, json=payload, headers=headers)
        return True
