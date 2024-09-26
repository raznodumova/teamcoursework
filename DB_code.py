from sqlalchemy import Column, Text, Integer, ForeignKey, UniqueConstraint
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import psycopg2
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

Base = declarative_base()


# Создаем таблицы
class User(Base):
    __tablename__ = "user"

    user_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    gender = Column(Text, nullable=False)
    age = Column(Integer, nullable=False)

    prompts = relationship("UserPrompt", backref="user", cascade="all, delete")
    ban = relationship("Banned", backref="user", cascade="all, delete")
    like = relationship("Liked", backref="user", cascade="all, delete")

class UserPrompt(Base):
    __tablename__ = "user_prompt"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Text, ForeignKey("user.user_id"), nullable=False, unique=True)
    city = Column(Text, nullable=False)
    gender = Column(Text, nullable=False)
    age = Column(Integer, nullable=False)


class Liked(Base):
    __tablename__ = "liked"

    option_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text, ForeignKey("user.user_id"), nullable=False)
    liked_user_id = Column(Text, nullable=False)

    UniqueConstraint("user_id", "liked_user_id", name="uq_like")

class Banned(Base):
    __tablename__ = "banned"

    option_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text, ForeignKey("user.user_id"), nullable=False)
    banned_user_id = Column(Text, nullable=False)

    UniqueConstraint("user_id", "banned_user_id", name="uq_ban")

class DB:
    """Class for initialization and work with Database"""
    def __init__(self, db_name):  # необходимо имя BD с которой будем работать
        self.db_name = db_name
        self.main_engine = sa.create_engine(f"postgresql://postgres:5728821q@localhost:5432/{db_name}", echo=True)
        self.session = sessionmaker(binds={Base: self.main_engine, }, expire_on_commit=False)()

    def connection(self):  # устанавливаем соединение с БД
        conn = psycopg2.connect(
            dbname="vk_bot",
            user="postgres",
            password="5728821q",  # укажите ваш пароль от суперпользователя
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        return conn

    def create_db(self):  # создание новой БД
        with self.connection().cursor() as cur:
            try:
                cur.execute(f"CREATE DATABASE {self.db_name};")
                print("База данных успешно создана")
                self.connection().commit()
                self.connection().close()
            except psycopg2.errors.DuplicateDatabase:
                print("База данных уже существует")

    def create_tables(self):  # создаем новые таблицы
        Base.metadata.create_all(self.main_engine)

    def drop_tables(self):  # удаляем все из БД
        Base.metadata.drop_all(self.main_engine)

    def create_user(self, user):
        try:
            with self.session as s:
                s.add(user)
                s.commit()
                print("Пользователь Добавлен")

        except IntegrityError as e:
            assert isinstance(e.orig, UniqueViolation)  # проверка на существование такой же записи
            print("Такой пользователь уже существует")

    # def delete_user(self, id):  # не успел разобраться что там не так с удалением 
    #     try:
    #         with self.session as s:
    #             user_to_delete = self.session.query(User).filter_by(user_id=id).first()
    #             s.delete(user_to_delete)
    #             s.commit()
    #     except psycopg2.errors.UniqueViolation:
    #         print("такой пользователь не существует")

    def crete_prompt(self, prompt):
        try:
            with self.session as s:
                s.add(prompt)
                s.commit()
                print("Запрос добавлен")

        except IntegrityError as e:
            assert isinstance(e.orig, UniqueViolation)  # проверка на существование такой же записи
            print("Пользователь уже добавил запрос")

    def like(self, user, who_liked):
        try:
            with self.session as s:
                like = Liked(user_id=user, liked_user_id=who_liked)
                s.add(like)
                s.commit()
                print("Лайк добавлен")

        except IntegrityError as e:
            print(e)

    def ban(self, user, user_for_ban):
        try:
            with self.session as s:
                ban = Banned(user_id=user, banned_user_id=user_for_ban)
                s.add(ban)
                s.commit()
                print("Бан добавлен")

        except IntegrityError as e:
            print(e)


# if __name__ == "__main__":
#     test_db = DB("vk_bot")
#     try:  #  тут просто тестирую как все работает
#         New_User = User(user_id=14, name="Vanya", city="moskow", gender="male", age=26)
#         # test_db.delete_user(New_User)
#         test_db.drop_tables()
#         test_db.create_tables()
#         test_db.create_user(New_User)
#         new_prompt = UserPrompt(user_id=14, city="Piter", gender="female" , age="20")
#         test_db.crete_prompt(new_prompt)
#         user_2 = User(user_id=22, name="Masha", city="Piter", gender="female", age=20)
#         test_db.create_user(user_2)
#         test_db.like(14, 22)
#         test_db.ban(14,22)
#     except Exception as e:
#         print(e)
#



