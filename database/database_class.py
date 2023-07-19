import sqlite3
from sqlite3 import Error


class Database:
    def __init__(self):
        from config import NAME_DB
        # коннект к базе данных
        self.con = self.__connection_db__(NAME_DB)
        self.con.create_function("lower", 1, self.__lower_string__)

    @staticmethod
    def __connection_db__(name_db: str):
        try:

            con = sqlite3.connect(name_db)

            return con

        except Error:

            print(Error)

    @staticmethod
    def __lower_string__(_str: str) -> str:
        return _str.lower()

    def create_table(self, request: str) -> None:
        cursor = self.con.cursor()
        cursor.execute(request)
        self.con.commit()
        cursor.close()

    def select_fetchall(self, request: str) -> list:
        cursor = self.con.cursor()

        response = cursor.execute(request).fetchall()
        cursor.close()
        return response

    def select_fetchone(self, request: str) -> tuple:
        cursor = self.con.cursor()
        response = cursor.execute(request).fetchone()
        cursor.close()
        return response

    def insert(self, request: str, values: tuple) -> None:
        cursor = self.con.cursor()
        cursor.execute(request, values)
        self.con.commit()
        cursor.close()

    def update(self, request: str) -> None:
        cursor = self.con.cursor()
        cursor.execute(request)
        self.con.commit()
        cursor.close()

    def delete(self, request: str, values: tuple) -> None:
        cursor = self.con.cursor()
        cursor.execute(request, values)
        self.con.commit()
        cursor.close()
