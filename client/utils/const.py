
class configCategoryObject():
    def __init__(self, config, nameCategory):
        self.config = config
        self.nameCategory = nameCategory

    def get(self, elm):
        return self.config.get(self.nameCategory, elm)

class Telegram(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'Telegram')
        self.token = self.get('token')
        self.alias = self.get('alias')

class Ngrok(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'Ngrok')
        self.api = self.get('api')

class Data(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'Data')
        self.usersDatabasePath = self.get('usersDatabasePath')
        self.availableLangs = self.get('availableLangs')
        self.availableLangs = self.availableLangs.split(', ')
        self.defaultLang = self.get('defaultLang')
        self.secretKey = self.get('secretKey')

class Logging():
    def __init__(self):
        self.format = '%(asctime)s %(levelname)s %(message)s'

class ConstPlenty():
    def __init__(self, config=None):
        if config: self.addConstFromConfig(config)
        self.commonPath = '/'.join(__file__.split('/')[:-2]) + '/'
        self.mainPath = '/'.join(__file__.split('/')[:-3]) + '/'
        self.logging = Logging()

    def addConstFromConfig(self, config):
        self.telegram = Telegram(config)
        self.ngrok = Ngrok(config)
        self.data = Data(config)

class UserInfo():
    def __init__(self, message):
        self.chatId = message.chat.id
        self.userId = message.from_user.id
        self.username = message.from_user.username
        self.userFirstName = message.from_user.first_name
        self.userFullName = message.from_user.full_name
        self.messageId = message.message_id
        self.userText = message.text

    def getValues(self):
        values = [self.chatId, self.userId, self.username, self.userFirstName, self.userFullName, self.messageId, self.userText]
        return values