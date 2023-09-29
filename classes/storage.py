from telegram import User as TG_user
from database.database_class import Database
from classes.exercise_class import Exercise
from datetime import datetime


class Storage:
    def __init__(self, database: Database):
        self.database = database
        self.__check_struct_db__()
        self.__fill_exercise_names__()

    def __check_struct_db__(self) -> None:
        # Таблица пользователей
        request = ("CREATE TABLE if not exists users(id integer PRIMARY KEY, name text, "
                   "username text, full_name text, link text, role text, joining_date timestamp)")

        self.database.create_table(request)

        # таблица с названиями упражнений
        request = "CREATE TABLE if not exists exercise_names(id integer PRIMARY KEY, name_ru text, name_eng text)"
        self.database.create_table(request)

        # таблица с упражнениями
        request = ("CREATE TABLE if not exists exercise_sets(id integer PRIMARY KEY AUTOINCREMENT, "
                   "user_id integer, exercise_id integer, count integer, weight int, time int, date timestamp)")
        self.database.create_table(request)

    def __fill_exercise_names__(self) -> None:
        """
        Наполняет таблицу exercise_names названиями упражнений
        при каждом запуске перезаписывается
        """
        exercise_names = [
            (1, 'приседания', 'squat'),
            (2, 'отжимания', 'push-ups'),
            (3, 'подтягивания', 'pull-ups'),
            (4, 'пресс', 'abs'),
            (5, 'брусья', 'dips'),
        ]

        for exercise_id, name_ru, name_eng in exercise_names:
            request = f"INSERT INTO exercise_names(id, name_ru, name_eng) " \
                      f"VALUES(?, ?, ?) on conflict (id) do update set name_ru = '{name_ru}', name_eng = '{name_eng}'"
            self.database.insert(request, (exercise_id, name_ru, name_eng))

    def __get_user_data__(self, user_id: int) -> tuple:
        request = """SELECT id, name, username, full_name, link, role,  
        joining_date FROM users WHERE id = {user_id}""".format(user_id=user_id)

        response = self.database.select_fetchone(request)
        return response

    def __add_new_user__(self, user: TG_user, role: str) -> None:
        """
        Args:
            user: add user in database

        Returns:
            None
        """
        request = "INSERT INTO users(id, name, username, full_name, link, role, joining_date) " \
                  "VALUES(?, ?, ?, ?, ?, ?, ?)"
        values = (
            user.id, user.name, user.username,
            user.full_name, user.link, role, datetime.now()
        )
        self.database.insert(request, values)

    def add_user(self, user: TG_user, role: str = 'user') -> None:
        """
        Args:
            user: объект телеграм пользователя
            role: роль пользователя

        Returns: None
        """
        # добавление пользователя в бд
        user_data = self.__get_user_data__(user_id=user.id)

        if not user_data:
            self.__add_new_user__(user=user, role=role)

    # def get_users_ids(self):
    #     request = '''SELECT id FROM users'''
    #     response = self.database.select_fetchall(request)
    #     return response

    def get_user_statistic(self, user_id: int, start_data: int) -> list:
        """
        :param user_id:
        :param start_data:  количество дней за которое нужно достать статистику
        :return: [(название упражнения, общее количество повторений), ...]
        """
        request = '''SELECT en.name_ru as 'exercise_name', SUM(es.count) as 'count', count(es.count) as 'sets'
FROM exercise_sets es 
JOIN exercise_names en ON es.exercise_id = en.id 
WHERE user_id = ? AND es.date >= ?
GROUP BY es.exercise_id'''

        response = self.database.select_fetchall(request, values=(user_id, start_data))
        return response

    def get_exercise_list(self, language='ru'):
        """
        :return: список названий упражнений в зависимости от языка
        """
        # todo
        langs = {
            'ru': 'name_ru',
            'eng': 'name_eng'
        }
        res = {}
        if langs.get(language):
            column_name = langs.get(language)
        else:
            column_name = 'name_ru'
        request = f"SELECT id, {column_name} FROM exercise_names"
        for i in self.database.select_fetchall(request):
            # print(i)
            res['exercise_' + str(i[0])] = i[1]
        # print(res)
        return res

    def save_exercise(self, exercise: Exercise):
        # сохранение упражнения в бд
        # когда можно сохранить упражнение а когда нет? (каких данных может не хватать)
        # todo проверять exercise на минимум данных которые нужны для сохранения
        request = ("INSERT INTO exercise_sets (user_id, exercise_id,count,weight, time, date)"
                   "VALUES(?, ?, ?, ?, ?, ?)")
        values = (
            exercise.user_id, exercise.id, exercise.count,
            exercise.weight, exercise.time, datetime.now()
        )
        self.database.insert(request, values)
        # print(exercise.show())


if __name__ == "__main__":
    memes_db = Database()
    storage = Storage(memes_db)
    ex = Exercise(user_id=123, id=112, count=20, name='пресс')
    storage.save_exercise(ex)
    # print(storage.get_exercise_list())
    # pass
