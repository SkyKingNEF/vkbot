from subcommands import *
from config import MAJOR_ADMIN_ID
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import traceback


session = vk_api.VkApi(token=tok)
vk = session.get_api()
longpoll = VkLongPoll(session)


def chat_bot_vk():
    while True:
        try:
            ignore_list = open(NAME_IGNORE_LIST, encoding='utf-8').read().split()
            for event in longpoll.listen():

                if event.type == VkEventType.MESSAGE_NEW:
                    from_id = event.user_id
                    msg_text = event.text.lower()

                    ignore_list = open(NAME_IGNORE_LIST, encoding='utf-8').read().split()
                    admin_list = open(NAME_ADMIN_LIST, encoding='utf-8').read().split()
                    if str(from_id) not in ignore_list: #проверка на игнор лист

                        if event.from_chat:
                            peer_id = event.peer_id
                            chat_id = event.chat_id
                            message_id = event.message_id
                            from_id = event.user_id
                            user_name = session.method('users.get', {
                                'user_ids': from_id
                            })
                            print(str(peer_id) + ' ' + str(from_id) + ' ' + user_name[0]['first_name'] + ': ' + msg_text)
                            if msg_text == '?команды':
                                sender_chat(chat_id, message_id, commands_for_chat())
                            elif msg_text == '?насмешка':
                                sender_chat(chat_id, message_id, randomevil_chat())
                            elif msg_text=='?факт':
                                sender_chat(chat_id, message_id, randomfact_chat())
                            elif msg_text == '?анекдот':
                                sender_chat(chat_id, message_id, randomhumor_chat())
                            elif msg_text == '?рег':
                                sender_chat(chat_id, message_id, registration_user_date_chat(from_id))
                            elif '?погода' in msg_text:
                                list_text = msg_text.split()
                                this_chat_id = chat_id
                                if list_text[0]=='?погода':
                                    if bool_elem_list(list_text, 1):
                                        city = list_text[1]
                                        sender_chat(chat_id, message_id, get_weather_chat(city))
                                    else:
                                        #нестабильно
                                        sender_chat(chat_id, message_id, 'Напиши название города')
                                        for event in longpoll.check():
                                            if event.type == VkEventType.MESSAGE_NEW:
                                                msg_text = event.text.lower()
                                                for event in longpoll.check():
                                                    if event.type == VkEventType.MESSAGE_NEW:
                                                        msg_text = event.text.lower()
                                                        message_id = event.message_id
                                                        city = msg_text
                                                        chat_id = event.chat_id
                                                        if this_chat_id == chat_id:
                                                            sender_chat(chat_id, message_id, get_weather_chat(city))
                            elif '?вики' in msg_text:
                                list_text = msg_text.split()
                                if list_text[0] == '?вики':
                                    user_request = msg_text[6:]
                                    sender_chat(chat_id, message_id, get_wiki_article(user_request))
                            elif msg_text == '?игнор список':
                                sender_chat(chat_id, message_id, show_ignorelist(ignore_list))
                            elif '?игнор' in msg_text:
                                list_text = msg_text.split()
                                if str(from_id) in admin_list or from_id == MAJOR_ADMIN_ID:
                                    if list_text[1] == '+':
                                        if 'vk.com' in msg_text:
                                            user_link = user_id(list_text[2])
                                            if str(user_link) in admin_list:
                                                sender_chat(chat_id, message_id, 'Невозможно добавить администратора в '
                                                                                 'игнор-лист')
                                            else:
                                                sender_chat(chat_id, message_id,
                                                            add_user_to_ignorelist(user_link, ignore_list))
                                        else:
                                            count_replies = 0
                                            for i in event.raw[6]['mentions']:
                                                user_link = str(event.raw[6]['mentions'][count_replies])
                                                if str(user_link) in admin_list:
                                                    sender_chat(chat_id, message_id,'Невозможно добавить администратора в '
                                                                                    'игнор-лист')
                                                else:
                                                    sender_chat(chat_id, message_id, add_user_to_ignorelist(user_link, ignore_list))
                                                count_replies+=1
                                    elif list_text[1] == '-':
                                        if 'vk.com' in msg_text:
                                            user_link = user_id(list_text[2])
                                            sender_chat(chat_id, message_id, remove_user_from_ignorelist(user_link, ignore_list))
                                        else:
                                            count_replies = 0
                                            for i in event.raw[6]['mentions']:
                                                user_link = str(event.raw[6]['mentions'][count_replies])
                                                sender_chat(chat_id, message_id,
                                                            remove_user_from_ignorelist(user_link, ignore_list))
                                                count_replies += 1
                                else:
                                    sender_chat(chat_id, message_id, 'Только администраторы могут пользоваться этой командой')
                            elif msg_text=='?админ список':
                                sender_chat(chat_id, message_id, show_adminlist(admin_list))
                            elif '?админ' in msg_text:
                                list_text = msg_text.split()
                                if from_id == MAJOR_ADMIN_ID:
                                    if list_text[1] == '+':
                                        if 'vk.com' in msg_text:
                                            user_link = user_id(list_text[2])
                                            if str(user_link) in ignore_list:
                                                sender_chat(chat_id, message_id, 'Невозможно назначить администратором пользователя в игнор-листе')
                                            else:
                                                sender_chat(chat_id, message_id, add_user_to_adminlist(user_link, admin_list))
                                        else:
                                            count_replies = 0
                                            for i in event.raw[6]['mentions']:
                                                user_link = str(event.raw[6]['mentions'][count_replies])
                                                if str(user_link) in ignore_list:
                                                    sender_chat(chat_id, message_id, 'Невозможно назначить администратором пользователя в игнор-листе')
                                                else:
                                                    sender_chat(chat_id, message_id,
                                                                add_user_to_adminlist(user_link, admin_list))
                                                count_replies += 1
                                    if list_text[1] == '-':
                                        if 'vk.com' in msg_text:
                                            user_link = user_id(list_text[2])
                                            sender_chat(chat_id, message_id,
                                                    remove_user_from_adminlist(user_link, admin_list))
                                        else:
                                            count_replies = 0
                                            for i in event.raw[6]['mentions']:
                                                user_link = str(event.raw[6]['mentions'][count_replies])
                                                sender_chat(chat_id, message_id,
                                                            remove_user_from_adminlist(user_link, admin_list))
                                                count_replies += 1







                        if event.from_user:
                            user_id = event.user_id
                            message_id = event.message_id
                            from_id = event.user_id
                            user_name = session.method('users.get', {
                                'user_ids': user_id
                            })
                            print(str(user_id) + ' ' + user_name[0]['first_name'] + ' ' + msg_text)

                            if msg_text == '?команды':
                                sender_user(from_id, message_id, commands_for_chat())
                            elif msg_text == '?насмешка':
                                sender_user(from_id, message_id, randomevil_chat())
                            elif msg_text=='?факт':
                                sender_user(from_id, message_id, randomfact_chat())
                            elif msg_text == '?анекдот':
                                sender_user(from_id, message_id, randomhumor_chat())
                            elif msg_text == '?рег':
                                sender_user(from_id, message_id, registration_user_date_chat(from_id))
                            elif '?погода' in msg_text:
                                list_text = msg_text.split()
                                this_chat_id = from_id
                                if list_text[0]=='?погода':
                                    if bool_elem_list(list_text, 1):
                                        city = list_text[1]
                                        sender_user(from_id, message_id, get_weather_chat(city))
                                    else:
                                        #лучше не использовать - нестабильно
                                        sender_user(from_id, message_id, 'Напиши название города')
                                        for event in longpoll.check():
                                            if event.type == VkEventType.MESSAGE_NEW:
                                                msg_text = event.text.lower()
                                                for event in longpoll.check():
                                                    if event.type == VkEventType.MESSAGE_NEW:
                                                        msg_text = event.text.lower()
                                                        message_id = event.message_id
                                                        city = msg_text
                                                        from_id = event.user_id
                                                        if this_chat_id == from_id:
                                                            sender_user(from_id, message_id, get_weather_chat(city))
                            elif '?вики' in msg_text:
                                list_text = msg_text.split()
                                if list_text[0] == '?вики':
                                    user_request = msg_text[6:]
                                    sender_user(from_id, message_id, get_wiki_article(user_request))
                            elif msg_text == '?игнор список':
                                sender_user(from_id, message_id, show_ignorelist(ignore_list))
                            elif '?игнор' in msg_text:
                                list_text = msg_text.split()
                                if str(from_id) in admin_list:
                                    if list_text[1] == '+':
                                        if 'vk.com' in msg_text:
                                            user_link = user_id(list_text[2])
                                            if str(user_link) in admin_list:
                                                sender_user(from_id, message_id, 'Невозможно добавить администратора в '
                                                                                 'игнор-лист')
                                            else:
                                                sender_user(from_id, message_id,
                                                            add_user_to_ignorelist(user_link, ignore_list))
                                        else:
                                            count_replies = 0
                                            for i in event.raw[6]['mentions']:
                                                user_link = str(event.raw[6]['mentions'][count_replies])
                                                if str(user_link) in admin_list:
                                                    sender_user(from_id, message_id,'Невозможно добавить администратора в '
                                                                                    'игнор-лист')
                                                else:
                                                    sender_user(from_id, message_id, add_user_to_ignorelist(user_link, ignore_list))
                                                count_replies+=1
                                    elif list_text[1] == '-':
                                        if 'vk.com' in msg_text:
                                            user_link = user_id(list_text[2])
                                            sender_user(from_id, message_id, remove_user_from_ignorelist(user_link, ignore_list))
                                        else:
                                            count_replies = 0
                                            for i in event.raw[6]['mentions']:
                                                user_link = str(event.raw[6]['mentions'][count_replies])
                                                sender_user(from_id, message_id,
                                                            remove_user_from_ignorelist(user_link, ignore_list))
                                                count_replies += 1
                                else:
                                    sender_user(from_id, message_id, 'Только администраторы могут пользоваться этой командой')
                            elif msg_text=='?админ список':
                                sender_user(from_id, message_id, show_adminlist(admin_list))
                            elif '?админ' in msg_text:
                                list_text = msg_text.split()
                                if str(from_id) in admin_list:
                                    if list_text[1] == '+':
                                        if 'vk.com' in msg_text:
                                            user_link = user_id(list_text[2])
                                            if str(user_link) in ignore_list:
                                                sender_user(from_id, message_id, 'Невозможно назначить администратором пользователя в игнор-листе')
                                            else:
                                                sender_user(from_id, message_id, add_user_to_adminlist(user_link, admin_list))
                                        else:
                                            count_replies = 0
                                            for i in event.raw[6]['mentions']:
                                                user_link = str(event.raw[6]['mentions'][count_replies])
                                                if str(user_link) in ignore_list:
                                                    sender_user(from_id, message_id, 'Невозможно назначить администратором пользователя в игнор-листе')
                                                else:
                                                    sender_user(from_id, message_id,
                                                                add_user_to_adminlist(user_link, admin_list))
                                                count_replies += 1
                                    if list_text[1] == '-':
                                        if 'vk.com' in msg_text:
                                            user_link = user_id(list_text[2])
                                            sender_user(from_id, message_id,
                                                    remove_user_from_adminlist(user_link, admin_list))
                                        else:
                                            count_replies = 0
                                            for i in event.raw[6]['mentions']:
                                                user_link = str(event.raw[6]['mentions'][count_replies])
                                                sender_user(from_id, message_id,
                                                            remove_user_from_adminlist(user_link, admin_list))
                                                count_replies += 1

                    else: #если в игноре
                        continue

        except FileNotFoundError:
            f = open(NAME_IGNORE_LIST, 'w')
            f.close()
            f = open(NAME_ADMIN_LIST, 'w')
            f.close()
        except:
            print(traceback.format_exc())


chat_bot_vk()