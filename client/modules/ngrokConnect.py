import requests

class NgrokWorker():
    def __init__(self, api):
        self.endPointUrl = 'https://api.ngrok.com/tunnels'
        self.api = api

    def getSessions(self):
        response = self.getResponse()
        if 'error_code' in response: return []
        if not response['tunnels']: return []
        sessions = []
        for tnl in response['tunnels']:
            sessions.append(dict(publicUrl=tnl['public_url'],
                                 localUrl=tnl['forwards_to']))
        return sessions

    def getResponse(self):
        response = requests.get(self.endPointUrl, headers=self.getHeaders(self.api))
        return response.json()

    def getHeaders(self, api):
        headers = {
            "Authorization": f"Bearer {api}",
            "Ngrok-Version": "2"
        }
        return headers