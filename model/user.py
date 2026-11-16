class User:
    __id:int
    __full_name:str
    __age:int

    def __init__(self, id:int, full_name:str, age:int):
        self.__id = id
        self.__full_name = full_name
        self.__age = age

    def __str__(self):
        return f"{self.__id} {self.__full_name}"