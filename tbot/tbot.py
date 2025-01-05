from pathlib import Path
import time
from rich import print, inspect
import telebot
import re
import datetime 
try:
    from tbot_secrets import tokken, name, lastname, username
except:
    from .tbot_secrets import tokken, name, lastname, username
try:
    from basecontrol import Directory, DefaultsValues
except:
    from tbot.basecontrol import Directory, DefaultsValues


"""
команды бота:
/start, /help
1. stat - получение о кол-ве фото в базе и архиве, установленных настройках
2. get кол-во фото - получить указанное кол-во фото из базы, 
                     если не указано, то равное установленному значению.
                     фото из базы перемещаются в архив
3. getlast кол-во фото - получить фото из базы, последние. фото из базы перемещаются в архив
4. dget кол-во фото - то же, что и get, но фото удаляются из базы
5. dgetlast кол-во фото - то же, что и getlast, но фото удаляются из базы
6. del кол-во фото - удалить из базы
7. arch кол-во фото - перенести в архив
8. archlast кол-во фото - перенести в архив с конца
9. dellast кол-во фото - удалить с конца
10. setget - установка кол-ва получаемых фото
11. setarch - кол-во переносимых в архив фото
12. setdel - кол-во удаляемых фото
13. clear - полное удаление фото с базы
14. cleararch - очистить архив
"""


base_path = '/home/baron/coding/Python/EagleEye/tbot/test_save'
base_path = '/home/baron/coding/Python/EagleEye/saving/'
archive_path = '/home/baron/coding/Python/EagleEye/tbot/test_archive'
archive_path = '/home/baron/coding/Python/EagleEye/archive/'

    
base = Directory(base_path)
archive = Directory(archive_path)

dvals = DefaultsValues()

bot = telebot.TeleBot(token=tokken, parse_mode=None)

def send_photos_helper(bot:telebot.TeleBot, msg, base_dir:Directory, arch_dir:Directory|None=None, 
                       num_photos:int=dvals.num_get_photos, side:int=0, delete=False):
    send_files_list = []
    delete_files_list = []
    if side == 0:
        files = base.files('.jpg', '.jpeg')[:num_photos]
    elif side == 1:
        files = base.files('.jpg', '.jpeg')[-num_photos:]
    if not files:
        bot.send_message(msg.chat.id, 'Нет фотографий в базе')
        print("Запрос на получение фото с базы. Отправка не возможна, база пуста.")
        return
    for f in files:
        try:
            file = open(f, 'rb')
            send_files_list.append(telebot.types.InputMediaPhoto(file))
            delete_files_list.append(f)
        except:
            pass
    if not delete:
        base.moves_files(archive, files=delete_files_list)
        # bot.send_message(msg.chat.id, f'Отправлено и перенесено в архив: {len(delete_files_list)} фото.')
        print(f'Отправлено и перенесено в архив: {len(delete_files_list)} фото.')
    else:
        base.delete(delete_files_list)
        # bot.send_message(msg.chat.id, f'Отправлено и удалено из базы: {len(delete_files_list)} фото.')
        print(f'Отправлено и удалено из базы: {len(delete_files_list)} фото.')
    bot.send_media_group(msg.chat.id, send_files_list)


def is_valid_user(message):
    data = message.from_user
    first_name = data.first_name == name
    last_name = data.last_name == lastname
    user_name = data.username == username
    return first_name and last_name and user_name


@bot.message_handler(commands=['start'])
def start(message):
    if not is_valid_user(message):
        return
    text = "Для плучения списка команд введите /help"
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['help'])
def help(message):
    text = "список команд:\n"\
    "/stat - сведенья о кол-ве фото в базе и архиве, установленных настройках\n\n"\
    "/get {n} - получить n фото из базы, "\
    "если не указано, то равное установленному значению. "\
    "фото из базы перемещаются в архив\n\n"\
    "/getlast {n} - получить n последних фото. фото из базы перемещаются в архив\n\n"\
    "/dget {n} - то же, что и get, но фото удаляются из базы\n\n"\
    "/dgetlast {n} - то же, что и getlast, но фото удаляются из базы"\
    "/delete {n} - удалить из базы"\
    "/archive {n} - перенести в архив\n\n"\
    "/archivelast {n} - перенести в архив с конца\n\n"\
    "/deletelast {n} - удалить из базы с конца\n\n"\
    "/setget {n} - установка кол-ва получаемых фото\n\n"\
    "/setarchive {n} - кол-во переносимых в архив фото\n\n"\
    "/setdelete {n} - кол-во удаляемых фото\n\n"\
    "/clear - полное удаление фото с базы\n\n"\
    "/cleararch - очистить архив\n\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['stat'])
def stat (message):
    if not is_valid_user(message):
        return
    text = f"Фото в базе: {base.count_files}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler()
def messages_parser(msg):
    send_files_list = []
    delete_files_list = []
    if not is_valid_user(msg):
        return
    cmd = str(msg.text.lower()).split()
    cmd = list(filter(lambda x: x.strip(), cmd))
    if len(cmd) > 2 or len(cmd) == 0: return
    elif len(cmd) > 1:
        try:
            cmd, num = cmd[0].strip(), int(cmd[1])
        except: return
        match cmd:
            case '/get':
                print(f'command: {cmd.replace("/", "")}, val: {num}')
                send_photos_helper(bot, msg, base, archive, num)
            case '/getlast':
                print(f'command: {cmd.replace("/", "")}, val: {num}')
                send_photos_helper(bot, msg, base, archive, num, 1)
            case '/dget':
                print(f'command: {cmd.replace("/", "")}, val: {num}')
                send_photos_helper(bot, msg, base, num_photos=num, delete=True)
            case '/dgetlst': 
                print(f'command: {cmd.replace("/", "")}, val: {num}')
                send_photos_helper(bot, msg, base, num_photos=num, delete=True, side=1)
            case '/del': 
                print(f'command: {cmd.replace("/", "")}, val: {num}')
                print(f'Удалено из базы: {num} фото')
                bot.send_message(msg.chat.id, f'Удалено из базы {num} фото')
                base.clear(num_files=num)
            case '/dellast':
                print(f'command: {cmd.replace("/", "")}, val: {num}')
                print(f'Удалено из базы: {num} фото')
                bot.send_message(msg.chat.id, f'Удалено из базы {num} фото')
                base.clear(num_files=num, side=1)
            case '/arch': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}, val: {num}')
            case '/archlast': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}, val: {num}')
            case '/setget': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}, val: {num}')
            case '/setarch': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}, val: {num}')
            case '/setdel': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}, val: {num}')
            case _: bot.send_message(msg.chat.id, f'command not found, {cmd}')
    elif len(cmd) == 1:
        cmd = cmd[0]
        match cmd:
            case '/get':
                print(f'command: {cmd.replace("/", "")}, val: {dvals.num_get_photos}')
                send_photos_helper(bot, msg, base, archive)
            case '/getlast':
                print(f'command: {cmd.replace("/", "")}, val: {dvals.num_get_photos}')
                send_photos_helper(bot, msg, base, archive, side=1)
            case '/dget': 
                print(f'command: {cmd.replace("/", "")}, val: {dvals.num_get_photos}')
                send_photos_helper(bot, msg, base, num_photos=dvals.num_get_photos, delete=True)
            case '/dgetlst': 
                print(f'command: {cmd.replace("/", "")}, val: {dvals.num_get_photos}')
                send_photos_helper(bot, msg, base, num_photos=dvals.num_get_photos, delete=True, side=1)
            case '/del':
                num = dvals.num_del_photos
                print(f'command: {cmd.replace("/", "")}, val: {num}')
                print(f'Удалено из базы: {num} фото')
                bot.send_message(msg.chat.id, f'Удалено из базы {num} фото')
                base.clear(num_files=num)
            case '/dellast':
                num = dvals.num_del_photos
                print(f'command: {cmd.replace("/", "")}, val: {num}')
                print(f'Удалено из базы: {num} фото')
                bot.send_message(msg.chat.id, f'Удалено из базы {num} фото')
                base.clear(num_files=num, side=1)
            case '/arch': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}')
            case '/archlast': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}')
            case '/setget': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}')
            case '/setarch': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}')
            case '/setdel': bot.send_message(msg.chat.id, f'command: {cmd.replace("/", "")}')
            case _: bot.send_message(msg.chat.id, f'command not found, {cmd}')
    else:
        bot.send_message(msg.chat.id, f'command not found, {cmd}')


if __name__ == "__main__":
    bot.infinity_polling()













