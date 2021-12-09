from config import mytoken as tok
from config import owm_key
from vk_api.longpoll import VkLongPoll
import vk_api
import requests
import mtranslate
import randfacts
import urllib
import re
import datetime
from pyowm import OWM
from random import randint as random
import wikipedia
from config import NAME_IGNORE_LIST, NAME_ADMIN_LIST

session = vk_api.VkApi(token=tok)
vk = session.get_api()
longpoll = VkLongPoll(session)


#погода
owm = OWM(owm_key)

#википедия
wikipedia.set_lang('ru')


def sender_chat(chat_id, message_id, message):
    session.method('messages.send', {
        'chat_id': chat_id,
        'message': message,
        'random_id': 0,
        'reply_to': message_id
    })

def sender_user(from_id, message_id, message):
    session.method('messages.send', {
        'user_id': from_id,
        'message': message,
        'random_id': 0,
        'reply_to': message_id
    })

def commands_for_chat():
    answer = ('Команды:    \n 1. ?Насмешка - отправляет обидную насмешку (насмешки на английском и проходят через переводчик) '
                        ' \n 2. ?Факт - отправляет случайный факт '
                        ' \n 3. ?Анекдот - отправляет случайный анекдот '
                        ' \n 4. ?рег - отправляет дату регистрации пользователя'
                        ' \n 5. ?погодa *город* - отправляет данные о погоде в заданном городе'
                        ' \n 6. ?Bики *запрос* - отправляет информацию по указанному запросу'
                        ' \n '
                        ' \n Команды администратора:'
                        ' \n 1. ?игнор + - добавить человека в черный список'
                        ' \n 2. ?игнор - - убрать человека из черного списка')
    return answer

def randomevil_chat():
    r = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
    evil = r.json()['insult']
    text = evil
    output = mtranslate.translate(text, 'ru', 'auto')
    return output

def randomfact_chat():
    r = randfacts.get_fact()
    fact = mtranslate.translate(r, 'ru', 'auto')
    return fact

def randomhumor_chat():
    r = requests.get('http://rzhunemogu.ru/RandJSON.aspx?CType=1')
    humor = r.text
    humor = humor[12:-2]
    return humor

def registration_user_date_chat(from_id):
    a = 'https://vk.com/foaf.php?id=' + str(from_id)
    with urllib.request.urlopen(a) as response:
        vk_xml = response.read().decode("windows-1251")
    parsed_xml = re.findall(r'date="(.*)"', vk_xml)


    date = datetime.datetime.strptime(parsed_xml[0][0:10], '%Y-%m-%d').date()
    date1 = date.strftime('%d.%m.%Y года')

    output = 'Твоя дата регистрации: \n' + date1
    return output

def get_weather_chat(city):
    try:
        mgr = owm.weather_manager()
        obs = mgr.weather_at_place(city)
        weather = obs.weather
        t = weather.temperature('celsius')
        t_now = t['temp']
        t_feels_like = t['feels_like']
        clouds = weather.clouds
        wind = weather.wind()['speed']
        status = weather.status
        humi = weather.humidity

        answer = (
            f'Информация о городе {city.title()} \n \n Температура сейчас: {t_now}C \n ощущается как: {t_feels_like}C \n статус: {status} \n облачность: {clouds}% \n влажность: {humi}% \n ветер: {wind}м/с')

        return answer
    except:
        answer = 'Невозможно найти такой город'
        return answer

def get_wiki_article(user_request):
    try:
        wiki_page = wikipedia.page(user_request)
        wiki_answer = f'Статья: {wiki_page.original_title} \n {wiki_page.summary}'
        if len(wiki_answer)<240:
            return wiki_answer
        else:
            wiki_answer = f'Текст слишком длинный для ВК, держи ссылку по статье {wiki_page.original_title}: \n {wiki_page.url}'
            return wiki_answer
    except:
        return 'Невозможно выполнить запрос'

def add_user_to_ignorelist(user_id, ignore_list):
    name = session.method('users.get',
                          {'user_ids': user_id})
    if str(user_id) not in ignore_list:
        f = open(NAME_IGNORE_LIST, 'a', encoding='UTF-8')
        f.write(str(user_id) + '\n')
        f.close()
        return f'Пользователь @id{user_id} ({name[0]["first_name"]}) добавлен в игнор-лист'
    else:
        return f'Пользователь @id{user_id} ({name[0]["first_name"]}) уже состоит в игнор-листе'

def remove_user_from_ignorelist(user_id, ignore_list):
    name = session.method('users.get',
                          {'user_ids': user_id})
    if str(user_id) in ignore_list:
        f = open(NAME_IGNORE_LIST, 'r+', encoding='UTF-8')
        lines = f.readlines()
        f.seek(0) #курсор в начало строки
        for line in lines:
            if line.strip("\n") != str(user_id):
                f.write(line)
        f.truncate()
        f.close()
        return f'Пользователь @id{user_id} ({name[0]["first_name"]}) удален из игнор-листа'
    else:
        return f'Пользователь @id{user_id} ({name[0]["first_name"]}) не состоял игнор-листе'

def show_ignorelist(ignore_list):
    try:
        count_blacklist_id = 0
        answer_blacklist = []
        for i in ignore_list:
            name = session.method('users.get', {'user_ids': ignore_list[count_blacklist_id]})
            print(ignore_list[count_blacklist_id])
            answer_blacklist.append(
                f'vk.com/id{ignore_list[count_blacklist_id]} {name[0]["first_name"]} {name[0]["last_name"]}')
            count_blacklist_id += 1
        answer_blacklist_info = ' \n '.join(answer_blacklist)
        return f'Список пользователей в игнор-листе: \n {answer_blacklist_info}'
    except:
        return 'Ошибка'

def show_adminlist(admin_list):
    try:
        count_admins_id = 0
        answer_blacklist = []
        for i in admin_list:
            name = session.method('users.get', {'user_ids': admin_list[count_admins_id]})
            print(admin_list[count_admins_id])
            answer_blacklist.append(
                f'vk.com/id{admin_list[count_admins_id]} {name[0]["first_name"]} {name[0]["last_name"]}')
            count_admins_id += 1
        answer_blacklist_info = ' \n '.join(answer_blacklist)
        return f'Список пользователей в админ-листе: \n {answer_blacklist_info}'
    except:
        return 'Ошибка'

def add_user_to_adminlist(user_id, admin_list):
    name = session.method('users.get',
                          {'user_ids': user_id})
    if str(user_id) not in admin_list:
        f = open(NAME_ADMIN_LIST, 'a', encoding='UTF-8')
        f.write(str(user_id) + '\n')
        f.close()
        return f'Пользователь @id{user_id} ({name[0]["first_name"]}) добавлен в админ-лист'
    else:
        return f'Пользователь @id{user_id} ({name[0]["first_name"]}) уже состоит в админ-листе'

def remove_user_from_adminlist(user_id, admin_list):
    name = session.method('users.get',
                          {'user_ids': user_id})
    if str(user_id) in admin_list:
        f = open(NAME_ADMIN_LIST, 'r+', encoding='UTF-8')
        lines = f.readlines()
        f.seek(0)  # курсор в начало строки
        for line in lines:
            if line.strip("\n") != str(user_id):
                f.write(line)
        f.truncate()
        f.close()
        return f'Пользователь @id{user_id} ({name[0]["first_name"]}) удален из админ-листа'
    else:
        return f'Пользователь @id{user_id} ({name[0]["first_name"]}) не состоял админ-листе'



def hansome_guys(chat_id, peer_id):
    info_chat = session.method('messages.getConversationMembers',
                               {
                                   'peer_id': peer_id

                               })
    count_users = 0
    list_names = []
    check = []
    for i in info_chat['profiles']:
        count_users += 1

    while len(list_names) < 3:
        random_id = random(0, count_users-1)
        if random_id not in check:
            check.append(random_id)
            list_names.append(
                f'{info_chat["profiles"][random_id]["first_name"]} {info_chat["profiles"][random_id]["last_name"]}')

    answer = '\n '.join(list_names)
    print(answer)

    sender_chat(chat_id, answer)
