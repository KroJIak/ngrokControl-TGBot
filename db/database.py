import json
import os
import shutil

class dbWorker():
    def __init__(self, databasePath, fileName, defaultDBFileName='default.json'):
        self.databasePath = databasePath
        self.fileName = fileName
        if not self.isExists():
            shutil.copyfile(databasePath + defaultDBFileName,
                            databasePath + fileName)

    def isExists(self):
        files = os.listdir(self.databasePath)
        return self.fileName in files

    def get(self):
        with open(self.databasePath + self.fileName) as file:
            dbData = json.load(file)
        return dbData

    def save(self, dbData):
        with open(self.databasePath + self.fileName, 'w', encoding='utf-8') as file:
            json.dump(dbData, file, indent=4, ensure_ascii=False)

class dbLocalWorker():
    def __init__(self):
        self.db = {}

    def isUserExists(self, userId):
        return str(userId) in self.db

    def addNewUser(self, userId):
        self.db[str(userId)] = dict(mode=-1)

    def setModeInUser(self, userId, mode):
        self.db[str(userId)]['mode'] = mode

    def getModeFromUser(self, userId):
        return self.db[str(userId)]['mode']

class dbUsersWorker(dbWorker):
    def getUserIds(self):
        dbData = self.get()
        userIds = tuple(dbData['users'].keys())
        return userIds

    def getPermissions(self):
        dbData = self.get()
        permissions = dbData['permissions']
        return permissions

    def getPermission(self, userId):
        dbData = self.get()
        permisson = dbData['users'][str(userId)]['permission']
        return permisson

    def isUnregistered(self, userId):
        permisson = self.getPermission(userId)
        return permisson == 'default'

    def isGuest(self, userId):
        permisson = self.getPermission(userId)
        return permisson == 'guest'

    def isAdmin(self, userId):
        permisson = self.getPermission(userId)
        return permisson == 'admin'

    def isUserExists(self, userId):
        dbData = self.get()
        return str(userId) in dbData['users']

    def addNewUser(self, userId, login, fullname, lang, permission='default'):
        dbData = self.get()
        newUser = dict(login=login,
                       fullname=fullname,
                       lang=lang,
                       permission=permission,
                       ngrokapi=None)
        dbData['users'][str(userId)] = newUser
        self.save(dbData)

    def getFromUser(self, userId, key):
        dbData = self.get()
        return dbData['users'][str(userId)][str(key)]

    def setInUser(self, userId, key, value):
        dbData = self.get()
        dbData['users'][str(userId)][str(key)] = value
        self.save(dbData)

    def getUserLang(self, userId):
        lang = self.getFromUser(userId, 'lang')
        return lang

    def setUserPermission(self, userId, permission):
        self.setInUser(userId, 'permission', permission)

    def getUserNgrokAPIs(self, userId):
        ngrokApi = self.getFromUser(userId, 'ngrokapis')
        return ngrokApi