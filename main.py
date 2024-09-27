import vk_api
import configparser
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
import requests

config = configparser.ConfigParser()
config.read('config.ini')  # отсюда токен достаем

def two_factor():
    code = input('Code? ')
    remember_device = True
    return code, remember_device

# так значится, тут у нас класс вк бота
class VKBot:
    def __init__(self):
        # login, password = "87475124705", "123456SAma"
        # vk_session = vk_api.VkApi(login, password, auth_handler=two_factor)
        # vk_session.auth(token_only=True)
        self.vk = vk_api.VkApi(login="87475124705", token=config['VK']['user_token']).auth(token_only=True)  # сюда вставляем
        self.vk_user = vk_api.VkApi(login="87475124705", token=config['VK']['group_token']).auth(token_only=True)  # и сюда тоже

    def longpoll(self):
        return VkLongPoll(self.vk)  # слушаем сообщения

    # метод для получения города пользователя
    def get_user_city(self, user_id):
        city = self.vk.method('users.get', {
            'user_ids': user_id,
            'fields': 'city'
        })[0]
        return city['city']['title']

    # метод для получения возраста пользователя (получаем дату рождения и считаем от нынешнего года)
    def get_user_age(self, user_id):
        age = self.vk.method('users.get', {
            'user_ids': user_id,
            'fields': 'bdate'
        })[0]
        if age['bdate'] is not None:
            now_date = datetime.datetime.now()
            bdate = datetime.datetime.strptime(age['bdate'], '%d.%m.%Y')
            user_age = now_date.year - bdate.year
            return user_age
        else:
            user_age = input('Укажите возраст: ')
            return user_age

    # метод для получения пола
    def get_gender(self, user_id):
        gender = self.vk.method('users.get', {
            'user_ids': user_id,
            'fields': 'sex'
        })[0]
        if gender['sex'] == 1:
            return 'Женский'
        else:
            return 'Мужской'

    # метод для замены пола на противоположный
    def change_gender(self, user_id):
        gender = self.vk.method('users.get', {
            'user_ids': user_id,
            'fields': 'sex'
        })[0]
        if gender['sex'] == 1:
            return 2
        else:
            return 1

    # метод для получения имени
    def get_name_user(self, user_id):
        name = self.vk.method('users.get', {
            'user_ids': user_id,
            'fields': 'first_name, last_name'
        })[0]
        full_name = name['first_name'] + ' ' + name['last_name']
        return full_name

    # метод для поиска по параметрам пользователя
    def find_user(self, user_id):
        BASE_URL = 'https://api.vk.com/method/'
        params = {
            'access_token': config['VK']['token'],
            'user_ids': user_id,
            'fields': 'is_closed, first_name, last_name, id',
            'sex': self.get_gender(user_id),
            'city': self.get_user_city(user_id),
            'age_from': self.get_user_age(user_id),
            'age_to': self.get_user_age(user_id) + 2,
            'status': 1 or 6,
            'v': 5.199
        }

        response = requests.get(BASE_URL + 'users.search', params=params)
        response_json = response.json()
        user_data = response_json['response']['items']

        for i in user_data:
            if not i.get('is_closed'):  # если пользователь не в ЧС
                i_id = i.get('id')
                i_name = i.get('first_name') + ' ' + i.get('last_name')
                i_link = 'https://vk.com/id' + str(i_id)
                yield i_id, i_name, i_link
            else:
                continue

    # метод для получения трех самых популярных фотографий
    def get_photos(self, user_id):
        # Получаем список всех фотографий пользователя
        photos = self.vk.method('photos.get', {
            'owner_id': user_id,
            'album_id': 'profile',  # Получаем фотографии из профиля
            'count': 100,  # Максимально возможное количество (опять же 100)
            'extended': 1,  # Чтобы получить дополнительную информацию о фото
            'v': 5.199
        })

        # Проверяем, что фотографии получены
        if 'items' not in photos or not photos['items']:
            return []

        # Сортируем фотографии по количеству лайков
        sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)

        # Берем три самые популярные фотки
        top_photos = sorted_photos[:3]

        # Получаем фотки с наибольшими размерами
        max_size_photos = []
        for photo in top_photos:
            max_size_photo = max(photo['sizes'], key=lambda size: size['width'] * size['height'])
            max_size_photos.append(max_size_photo['url'])  # URL самого большого изображения

        return max_size_photos
