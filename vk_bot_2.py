import main
import configparser
import vk_api
from keyboard_vk import keyb
from main import VKBot
from vk_api.longpoll import VkLongPoll, VkEventType
from tables import User, UserPrompt, Liked, Banned, create_tables, drop_all
import db_funcs as db
from random import randrange
from vk_api.utils import get_random_id
config = configparser.ConfigParser()
config.read('config.ini')
#
# def write_message(user_id, message):
vk_bot = VKBot()
attachments = []
swapped_user = {}
flag = True
vk_session = vk_api.VkApi(login="87475124705", token=config['VK']['token']).auth(token_only=True)
longpool = VkLongPoll(vk_session, group_id=227461675)

def write_message(reciver_id, msg):
    vk_bot.vk.method('messages.send', {'user_id': reciver_id,
                                       'message': msg,
                                       'random_id': randrange(10 ** 10),
                                       'keyboard': keyb,
                                       'attachment': ','.join(attachments)})


while True:
    try:
        for event in longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                user_id = event.user_id
                message = event.text.lower()

                if message == 'начать':
                    flag = False
                    full_name = vk_bot.get_name_user(user_id)
                    city = vk_bot.get_user_city(user_id)
                    age = vk_bot.get_user_age(user_id)
                    sex = vk_bot.get_gender(user_id)
                    # sex_find = vk_bot.change_gender(user_id)
                    user = User(user_id=user_id, name=full_name, city=city, gender=sex, age=age)
                    # prompt = UserPrompt(user_id, city, sex_find, age)
                    db.create_user(user)

                    start_msg = f'Привет, {full_name}! Мы придумали для тебя кнопочки, чтобы тебе было легче оринтироваться'
                    write_message(user_id, start_msg)
                    start_msg_2 = \
                        f'Следующий - чтобы перейти к следующему пользователю\n'
                    f"Добавить в ЧС - для добавления пользователя в черный список\n"
                    f'Добавить в избранное - чтобы добавить пользователя в избранное\n'
                    f'Убрать лайк - чтобы убрать лайк\n'
                    f'Выйти - чтобы выйти из бота'
                    write_message(user_id, start_msg_2)
                    start_msg_3 = f"Давай определимся кого будем искать"
                    write_message(user_id, start_msg_3)
                    write_message(user_id, "на этом пока что все")
    except Exception as e:
        print(e)