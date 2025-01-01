from pathlib import Path
import time
from rich import print, inspect
import telebot
import re
import datetime 

from tbot_secrets import tokken

"""
команды бота:
1. stat - получение о кол-ве фото в базе и архиве, установленных настройках
2. get кол-во фото - получить указанное кол-во фото из базы, 
                     если не указано, то равное установленному значению.
                     фото из базы перемещаются в архив
3. getlast кол-во фото - получить фото из базы, последние. фото из базы перемещаются в архив
4. dget кол-во фото - то же, что и get, но фото удаляются из базы
5. dgetlast кол-во фото - то же, что и getlast, но фото удаляются из базы
6. delete кол-во фото - удалить из базы
7. archive кол-во фото - перенести в архив
8. archivelast кол-во фото - перенести в архив с конца
9. deletelast кол-во фото - удалить с конца
10. setget - установка кол-ва получаемых фото
11. setarchive - кол-во переносимых в архив фото
12. setdelete - кол-во удаляемых фото
13. clear - полное удаление фото с базы
14. cleararch - очистить архив
"""



bot = telebot.TeleBot(token=tokken, parse_mode=None)


@bot.message_handler(commands=['start'])
def start(message):
    text = "Для плучения списка команд введите /help"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['help'])
def start(message):
    text = "список команд:\n"\
    "/stat - сведенья о кол-ве фото в базе и архиве, установленных настройках\n\n"\
    "/get {n} - получить n фото из базы, "\
    "если не указано, то равное установленному значению. "\
    "фото из базы перемещаются в архив\n\n"\
    "/getlast {n} - получить n последних фото. фото из базы перемещаются в архив\n\n"\
    "/dget {n} - то же, что и get, но фото удаляются из базы\n\n"\
    "/dgetlast {n} - то же, что и getlast, но фото удаляются из базы"\
    "/delete {n} - удалить из базы"\
    "/archive {n} - перенести в архив\n"\
    "/archivelast {n} - перенести в архив с конца\n"\
    "/deletelast кол-во фото - удалить из базы с конца\n"\
    "/setget {n} - установка кол-ва получаемых фото\n"\
    "/setarchive - кол-во переносимых в архив фото\n"\
    "/setdelete - кол-во удаляемых фото\n"\
    "/clear - полное удаление фото с базы\n"\
    "/cleararch - очистить архив\n"
    bot.send_message(message.chat.id, text)



bot.infinity_polling()













