from keyboard_vk import keyb
from main import VKBot
from vk_api.longpoll import VkLongPoll, VkEventType
from tables import User, UserPrompt, Liked, Banned
from random import randrange


def write_message(user_id, message):

    vk_bot = VKBot()
    vk_bot.longpoll = VkLongPoll(vk_bot.vk)
    attachments = []
    swap_user = {}
    flag = True

    vk_bot.vk.method('messages.send', {'user_id': user_id,
                                       'message': message,
                                       'random_id': randrange(10 ** 10),
                                       'keyboard': keyb,
                                       'attachment': ','.join(attachments)})

    for event in vk_bot.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            message = event.text.lower()

            if message == 'начать':
                flag = False
                if user_id not in swap_user:
                    swap_user[user_id] = vk_bot.find_user(user_id)

                next_user = swap_user[user_id]

                full_name = vk_bot.get_name_user(user_id)
                city = vk_bot.get_user_city(user_id)
                age = vk_bot.get_user_age(user_id)
                sex = vk_bot.get_gender(user_id)
                sex_find = vk_bot.change_gender(user_id)
                user = User(user_id, full_name, city, sex, age)
                prompt = UserPrompt(user_id, city, sex_find, age)

                db_bot.create_user(user)
                db_bot.crete_prompt(prompt)

                write_message(user_id, f'Привет, {full_name}! Мы придумали для тебя кнопочки, чтобы тебе было легче оринтироваться\n'
                                       f'Следующий - чтобы перейти к следующему пользователю\n'
                                       f'Добавить в ЧС - для добавления пользователя в черный список\n'
                                       f'Добавить в избранное - чтобы добавить пользователя в избранное\n'
                                       f'Убрать лайк - чтобы убрать лайк\n'
                                       f'Выйти - чтобы выйти из бота')

            elif message == 'следующий':
                if not flag:
                    try:
                        tmp_user = next_user.__next__()

                        tmp_id = tmp_user[0]
                        tmp_name = tmp_user[1:3]
                        tmp_link = tmp_user[3]
                        tmp_message = f'{tmp_id} {tmp_name} {tmp_link}'

                        if tmp_id not in db_bot.ban(user_id, tmp_id):
                            attachments = vk_bot.get_photo(tmp_id)
                            write_message(user_id, tmp_message, attachments)
                        else:
                            write_message(f'{user_id}, {tmp_name}{tmp_link} у тебя в ЧС')

                    except StopIteration:
                        write_message(user_id, 'Конец списка, чтобы начать сначала нажми "Начать"')
                else:
                    write_message(user_id, 'Нажми "Начать"')

            elif message == 'Начать сначала':
                if not flag:
                    swap_user[user_id] = vk_bot.find_user(user_id)
                    next_user = swap_user[user_id]

                    message = 'Нажми "Следующий" для перехода к следующему пользователю'
                    try:
                        del tmp_id
                        write_message(user_id, message)
                    except NameError:
                        write_message(user_id, message)

                else:
                    write_message(user_id, 'Нажми "Начать"')

            elif message == 'Добавить в ЧС':
                if not flag:
                    try:
                        if not db_bot.ban(user_id, user_id):
                            ban = Banned(user_id=user_id, banned_user_id=user_id)
                            db_bot.ban(ban)
                            write_message(user_id, 'Пользователь добавлен в ЧС')
                        else:
                            write_message(user_id, 'Пользователь уже в ЧС')

                    except NameError:
                        write_message(user_id, 'Нажми "Начать"')

                else:
                    write_message(user_id, 'Нажми "Начать"')

            elif message == 'Добавить в избранное':
                if not flag:
                    try:
                        if not db_bot.like(user_id, user_id):
                            like = Liked(user_id=user_id, liked_user_id=user_id)
                            db_bot.like(like)
                            write_message(user_id, 'Пользователь добавлен в избранное')
                        else:
                            write_message(user_id, 'Пользователь уже в избранном')

                    except NameError:
                        write_message(user_id, 'Нажми "Начать"')

                else:
                    write_message(user_id, 'Нажми "Начать"')

            elif message == 'Выйти':
                if not flag:
                    flag = True
                    del swap_user[user_id]
                    del next_user
                    db_bot.drop_tables()
                    write_message(user_id, 'Вы вышли из бота')

                else:
                    write_message(user_id, 'Нажми "Начать"')

            else:
                write_message(user_id, 'Я не понимаю тебя, попробуй ещё раз')

