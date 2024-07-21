import requests

class MessagingHistory:

    def __init__(self):
        pass

    def get_chats(self, request):
        url = "https://fusionworks-dev-api.cloudjet.site/chat/history"
        params = {
            "queryType": "database",
        }
        headers = {
            "Content-Type": "application/json",
            "Cookie": "jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NiwiZW1haWwiOiJiaW5hcnkuYmFyazFAZW1haWwuY29tIiwiaWF0IjoxNzIxNTIyOTE4LCJleHAiOjE3MjE2MDkzMTh9.zzBp7MKHDkcH4ySG_3L4mb3qddRmfmcjhhnC3Qq2gqs"
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
            "Cookie": "jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NiwiZW1haWwiOiJiaW5hcnkuYmFyazFAZW1haWwuY29tIiwiaWF0IjoxNzIxNTIyOTE4LCJleHAiOjE3MjE2MDkzMTh9.zzBp7MKHDkcH4ySG_3L4mb3qddRmfmcjhhnC3Qq2gqs"
        }

        response = requests.put(url, json=payload, headers=headers)
        print(response)
        return True
