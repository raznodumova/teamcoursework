from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
# import main
import configparser
import vk_api
# from keyboard_vk import keyb
# from main import VKBot
# from tables import User, UserPrompt, Liked, Banned
# import db_funcs as db
# from random import randrange
from vk_api.utils import get_random_id

config = configparser.ConfigParser()
config.read('config.ini')

def start():
    vk_session = vk_api.VkApi(
        token=config['VK']['group_token'])  # тут чисто токен группы (который длинный)
    longpoll = VkBotLongPoll(vk_session, 227461675)  # id группы можно не менять и не удалять
    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.message.user_id
            message = event.message.text.lower()
            print(message)  # это временно, чисто чтоб видеть как сообщения приходят к нам
            if message == 'начать':
                # flag = False
                # full_name = vk_bot.get_name_user(user_id) # Тут чето не так
                # city = vk_bot.get_user_city(user_id)  # не хочет получать данные о пользователе
                # age = vk_bot.get_user_age(user_id)  # походу функции в main подшаманить нужно
                # sex = vk_bot.get_gender(user_id)
                # # sex_find = vk_bot.change_gender(user_id)
                # user = User(user_id=user_id, name=full_name, city=city, gender=sex, age=age)
                # # prompt = UserPrompt(user_id, city, sex_find, age)
                # db.create_user(user)

                start_msg = f'Привет, братишка! Мы придумали для тебя кнопочки, чтобы тебе было легче оринтироваться'
                vk.messages.send(user_id=event.message.from_id,  # через функцию не получается отправлять сообщения
                                 random_id=get_random_id(),
                                 message=start_msg)
                start_msg_2 = \
                    f'Следующий - чтобы перейти к следующему пользователю\n'
                f"Добавить в ЧС - для добавления пользователя в черный список\n"
                f'Добавить в избранное - чтобы добавить пользователя в избранное\n'
                f'Убрать лайк - чтобы убрать лайк\n'
                f'Выйти - чтобы выйти из бота'
                vk.messages.send(user_id=event.message.from_id,
                                 random_id=get_random_id(),
                                 message=start_msg_2)
                start_msg_3 = f"Давай определимся кого будем искать"
                vk.messages.send(user_id=event.message.from_id,
                                 random_id=get_random_id(),
                                 message=start_msg_3)
                vk.messages.send(user_id=event.message.from_id,
                                 random_id=get_random_id(),
                                 message="пока что всё")


if __name__ == '__main__':
    start()
