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

        # todo сделать вывод в зависимости от языка (возможно прокидывать язык пользователя в упражнении)
        s = f'{self.name} : {self.count}'
        return s


if __name__ == "__main__":
    # ex = Exercise(user_id=1)
    # ex.name = "Приседания"
    # ex.count = 10
    # ex.weight = 100
    # print(ex.show())
    #
    # print(isinstance(ex, Exercise))
    pass
