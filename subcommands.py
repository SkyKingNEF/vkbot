from comands_for_privatemessages import *


def bool_elem_list(list, element_num):
    try:
        if list[element_num] in list:
            x = True
    except:
            x = False
    return x

def text_to_list(text):
    list = text.split()
    return list

def user_id(user_link):
    try:
        if 'https://vk.com/' in user_link:
            x = user_link[15:]
            user_id = session.method('utils.resolveScreenName', {'screen_name': x})
        elif 'http://vk.com/' in user_link:
            x = user_link[14:]
            user_id = session.method('utils.resolveScreenName', {'screen_name': x})
        elif 'vk.com/' in user_link:
            x = user_link[7:]
            user_id = session.method('utils.resolveScreenName', {'screen_name': x})
        return user_id['object_id']
    except:
        return -1




