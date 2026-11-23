from exception.bank_exception import ValidationError
from bank.account.bank_account import BankAccount


class Client: 
    __id: int
    __full_name: str
    __list_bank_account: list[BankAccount]
    __contacts: list[str]
    __age: int
    __password: str
    __suspiciously: bool
    __ranking: int

    def __init__(self, id: int, full_name: str, list_bank_account: list[BankAccount], contacts: list[str], age: int, password: str, ranking: int): 
        self.__id = id
        self.__full_name = full_name
        self.__list_bank_account = list_bank_account
        self.__contacts = contacts
        self.__age = age
        self.__password = password
        self.__suspiciously = False
        self.__ranking = ranking
        self.validation_age()

    def id(self) -> int: 
        return self.__id
    def full_name(self) -> str: 
        return self.__full_name

    def list_bank_account(self) -> list[BankAccount]: 
        return self.__list_bank_account

    def contacts(self) -> list[str]: 
        return self.__contacts

    def age(self) -> int: 
        return self.__age

    def password(self) -> str: 
        return self.__password

    def validation_age(self): 
         if self.__age < 18: 
             raise ValidationError("Возраст меньше 18 лет")

    def get_suspiciously(self) -> bool: 
        return self.__suspiciously

    def set_suspiciously(self, suspiciously): 
        self.__suspiciously = suspiciously

    def ranking(self) -> int: 
        return self.__ranking

    def __str__(self): 
        return (f"{self.__full_name} {self.__age}\n"
                f"{self.str_list_bank_account()}\n"
                f"{self.__contacts}")

    def str_list_bank_account(self) -> list[str]: 
        str_list_bank_account = []
        for account in self.__list_bank_account: 
            str_list_bank_account.append(account.__str__())
        return str_list_bank_account