from dataclasses import dataclass


@dataclass
class Exercise:
    user_id: int
    id: int = 0
    count: int = 0
    name: str = ""
    weight: int = 0
    time: int = 0

    def show(self):
        """
        :return: отформатированный текст для печати упражнения
        """

        #todo сделать вывод в зависимости от языка (возможно прокидывать язык пользователя в упражнении)
        s = f'Упражнение: {self.name}\nКоличество: {self.count}'
        if self.weight:
            s += f'\nВес: {self.weight} кг'
        return s

    @staticmethod
    def get_names():
        return "Приседания", "Отжимания", "Подтягивания", "Пресс", "Бег"

    # todo перенести данные из таблицы exercise_names в класс

    # todo сделать маппинги id -> name, name -> id

    # функция получения всех названий упражнений (дня отрисовки кнопок)
    @staticmethod
    def get_name_by_id(exercise_id, lang='ru'):
        names_ru = {
            1: 'приседания',
            2: 'отжимания',
            3: 'подтягивания',
            4: 'пресс'
        }
        names_eng = {
            1: 'squat',
            2: 'push-ups',
            3: 'pull-ups',
            4: 'abs',
        }
        if lang == 'eng':
            return names_eng.get(exercise_id)

        return names_ru.get(exercise_id)

        # функция получения id упражнения по названию


if __name__ == "__main__":
    ex = Exercise(user_id=1)
    ex.name = "Приседания"
    ex.count = 10
    ex.weight = 100
    print(ex.show())

    print(isinstance(ex, Exercise))
