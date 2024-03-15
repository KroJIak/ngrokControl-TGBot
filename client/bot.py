from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio
from utils.funcs import *
from utils.const import ConstPlenty, UserInfo
from traceback import format_exc
import json
import logging
from modules.ngrokConnect import NgrokWorker

# docker run --net=host -it -e NGROK_AUTHTOKEN=2dRFvmzXNWzlEb5jJORCJAOoyZ2_64w38XZkWqZJ7CE8TJYBZ --name ngrok-container ngrok/ngrok:latest http 2468
# SETTINGS
const = ConstPlenty()
botConfig = getConfigObject('config/bot.ini', const.commonPath)
const.addConstFromConfig(botConfig)
logging.basicConfig(level=logging.INFO, filename=f'{const.commonPath}logs/{getLogFileName()}', filemode='w', format=const.logging.format)
dbUsers = getDBWorkerObject('users', const.mainPath, const.commonPath, databasePath=const.data.usersDatabasePath)
dbLocal = getDBWorkerObject('local', const.mainPath, const.commonPath)
bot = Bot(const.telegram.token)
dp = Dispatcher()

def getTranslation(userId, key, inserts=[], lang=None):
    try:
        if not lang: lang = dbUsers.getUserLang(userId)
        with open(f'{const.commonPath}lang/{lang}.json', encoding='utf-8') as langFile:
            langJson = json.load(langFile)
        text = langJson[key]
        if not inserts: return text
        for ins in inserts: text = text.replace('%{}%', str(ins), 1)
        return text
    except Exception:
        if dbUsers.isAdmin(userId): return getTranslation(userId, 'error.message', [format_exc()])
        else: return getTranslation(userId, 'error.message', ['wwc...'])

def getUserInfo(message):
    userInfo = UserInfo(message)
    if not dbUsers.isUserExists(userInfo.userId):
        permissions = dbUsers.getPermissions()
        lowestPermission = permissions['0']
        dbUsers.addNewUser(userInfo.userId, userInfo.username, userInfo.userFullName, const.data.defaultLang, lowestPermission)
    if not dbLocal.isUserExists(userInfo.userId):
        dbLocal.addNewUser(userInfo.userId)
    if userInfo.userText == const.data.secretKey and dbUsers.isUnregistered(userInfo.userId):
        dbUsers.setUserPermission(userInfo.userId, 'guest')
    userLogInfo = ' | '.join(list(map(str, userInfo.getValues())) + [str(dbLocal.db[str(userInfo.userId)])])
    logging.info(userLogInfo)
    print(userLogInfo)
    return userInfo

def getMainKeyboard(userId):
    mainButtons = [[types.KeyboardButton(text=getTranslation(userId, 'button.sessions'))]]
    mainKeyboard = types.ReplyKeyboardMarkup(keyboard=mainButtons, resize_keyboard=True)
    return mainKeyboard

# COMMANDS
@dp.message(Command('start'))
async def startHandler(message: types.Message):
    userInfo = getUserInfo(message)
    mainKeyboard = getMainKeyboard(userInfo.userId)
    await message.answer(getTranslation(userInfo.userId, 'start.message', [userInfo.userFirstName]), reply_markup=mainKeyboard, parse_mode='HTML')
    if dbUsers.isUnregistered(userInfo.userId):
        await message.answer(getTranslation(userInfo.userId, 'permissons.getsecretkey'), parse_mode='HTML')
        return

def getNgrokSessions(ngrokApi):
    ngrokConnection = NgrokWorker(ngrokApi)
    sessions = ngrokConnection.getSessions()
    return sessions

def getTextWithNgrokUrls(session):
    localUrl, publicUrl = session['localUrl'], session['publicUrl']
    resultText = f'<b>[</b> <code>{localUrl}</code> <b>] -> [</b> <code>{publicUrl}</code> <b>]</b>'
    return resultText

def isSessionsCommand(userId, userText):
    return userText in ['/sessions', f'/sessions@{const.telegram.alias}', getTranslation(userId, 'button.sessions')]

async def sendSessions(userId):
    userNgrokAPIs = dbUsers.getUserNgrokAPIs(userId)
    for ngrokApi in userNgrokAPIs:
        ngrokSessions = getNgrokSessions(ngrokApi)
        mainKeyboard = getMainKeyboard(userId)
        if ngrokSessions:
            await bot.send_message(userId, getTranslation(userId, 'ngrok.message'), disable_notification=True, parse_mode='HTML')
            for session in ngrokSessions:
                await bot.send_message(userId, getTextWithNgrokUrls(session), reply_markup=mainKeyboard, parse_mode='HTML')
        else: await bot.send_message(userId, getTranslation(userId, 'ngrok.error'), reply_markup=mainKeyboard, parse_mode='HTML')

async def sessionsHandler(userInfo):
    if dbUsers.isUnregistered(userInfo.userId):
        await bot.send_message(userInfo.chatId, getTranslation(userInfo.userId, 'permissons.getsecretkey'), parse_mode='HTML')
        return
    await sendSessions(userInfo.userId)

def isUnknownCommand(userText):
    return userText[0] == '/'

async def unknownCommandHandler(userInfo, message):
    mainKeyboard = getMainKeyboard(userInfo.userId)
    await message.answer(getTranslation(userInfo.userId, 'unknown.command.message'), reply_markup=mainKeyboard, parse_mode='HTML')

@dp.message()
async def mainHandler(message: types.Message):
    userInfo = getUserInfo(message)
    userMode = dbLocal.getModeFromUser(userInfo.userId)
    if dbUsers.isUnregistered(userInfo.userId):
        await message.answer(getTranslation(userInfo.userId, 'permissons.getsecretkey'), parse_mode='HTML')
        return

    elif isSessionsCommand(userInfo.userId, userInfo.userText):
        await sessionsHandler(userInfo)
        return

    elif isUnknownCommand(userInfo.userText):
        await unknownCommandHandler(userInfo, message)
        return

    elif userMode > 0:
        match userMode:
            case 1: pass
        return

async def mainTelegram():
    userIds = dbUsers.getUserIds()
    for userId in userIds:
        if not dbUsers.isUnregistered(userId):
            await sendSessions(userId)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(mainTelegram())