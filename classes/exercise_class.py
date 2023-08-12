from dataclasses import dataclass


@dataclass
class Exercise:
    user_id: int
    name: str = ""
    count: int = 0
    # todo в зависимости от языка
    # todo возможность настроить свой список упражнений
    names: tuple = ("Приседания", "Отжимания", "Подтягивания", "Пресс", "Бег")

    def save_exercise(self):
        # сохранение упраждения в бд
        # когда можно сохранить упражнение а когда нет? (каких данных может не хватать)
        print(self)

    def show(self):
        """

        :return: отформатированный текст для печати упражнения
        """
        return f"Доделать вывод!\n{self}"
        pass

    @staticmethod
    def get_names():
        return "Приседания", "Отжимания", "Подтягивания", "Пресс", "Бег"

    # функция получения всех названий упражнений (дня отрисовки кнопок)

    # функция получения id упражнения по названию


if __name__ == "__main__":
    ex = Exercise(user_id=1)
    ex.name = "Приседания"
    ex.count = 20
    # print(ex.user_id,ex.name,ex.count,ex.names)
