class User:
    id:int
    full_name:str
    age:int

    def __init__(self, id:int, full_name:str, age:int):
        self.id = id
        self.full_name = full_name
        self.age = age

    def __str__(self):
        return f"{self.full_name}"