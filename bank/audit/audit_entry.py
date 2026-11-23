from datetime import datetime

from util.audit_level import AuditLevel


class Audit:

    __timestamp: datetime
    __level: AuditLevel
    __action: str
    __client_name: str
    __account_number: str
    __details: str


    def __init__(self, level: AuditLevel, action: str, client_name: str,
                 account_number: str, details: str):
        self.__timestamp = datetime.now()
        self.__level = level
        self.__action = action
        self.__client_name = client_name
        self.__account_number = account_number
        self.__details = details

    def get_timestamp(self) -> datetime:
        return self.__timestamp

    def set_timestamp(self, timestamp: datetime):
        self.__timestamp = timestamp

    def get_level(self) -> AuditLevel:
        return self.__level

    def set_level(self, level: AuditLevel):
        self.__level = level

    def get_action(self) -> str:
        return self.__action

    def get_client_name(self) -> str:
        return self.__client_name

    def set_client_name(self, client_name: str):
        self.__client_name = client_name

    def get_account_number(self) -> str:
        return self.__account_number

    def set_account_number(self, account_number: str):
        self.__account_number = account_number

    def get_details(self) -> str:
        return self.__details

    def __str__(self):
        return (f"{self.__timestamp:%Y-%m-%d %H:%M:%S}  [{self.__level.value}]  "
                f"{self.__action}  {self.__client_name}  {self.__account_number}  {self.__details}")
