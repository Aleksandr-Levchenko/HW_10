from pathlib import Path
import os
import platform  # для clearscrean()
from RecordBook import AddressBook, Record, Name, Phone, Field
import re

path = Path("D:\Git\HW_09\database_09.csv")
book = AddressBook()


# Головна функція роботи CLI(Command Line Interface - консольного скрипту)  
def main():
    cmd = ""
   
    # головний цикл обробки команд користувача
    while True:
        # 1. Отримаємо команду від користувача
        cmd = input(">> ")    
        
        # 2. Виконуємо розбір командної строки
        cmd, prm = parcer_commands(cmd)
        
        # 3. Отримуємо handler_functions тобто ДІЮ
        if cmd: handler = get_handler(cmd)
        else: 
            print("Command was not recognized")
            continue
            
        # 4. Визначемо параметри для handler() 
        #    та виконаємо Команду користувача
        if run_handler(handler, cmd, prm) == "Good bye!":
            print("Good bye!")
            break
        
        
        
# Декоратор для Обробки командної строки
def input_error(func):
    def inner(handler, cmd, prm):
        try:
            result = func(handler, cmd, prm)
            if not result == "Good bye!": print(result) 
            else: return result
        
        # Обробка виключних ситуацій
        except FileNotFoundError:    # Файл бази даних Відсутній
            print("The database isn't found")
        except ValueError:
            print("Incorect data or unsupported format while writing to the file")
        except KeyError:
            print("Record isn't in the database")
    return inner


# Декоратор для Додавання нової людини у базу
def dec_func_add_rec(func):
    def inner(prm):
        return func(prm)
    return inner


# Декоратор для Друкування всієї бази даних
def dec_func_all_phone(func):
    def inner(_):
        return func(_)
    return inner


# Декоратор для Внесення змін у базу даних
def dec_func_change_phone(func):
    def inner(prm):
        return func(prm)
    return inner


# Декоратор для Завершення роботи      
def dec_func_exit(func):
    def inner(_):
        return func(_)  
    return inner


# Декоратор для команди Вітання      
def dec_func_greeting(func):
    def inner(_):
        return func(_)
    return inner
 

# Декоратор для Знайденя телефону за Ім'ям особи
def dec_func_phone(func):
    def inner(prm):
        return func(prm)
    return inner
 

 # Декоратор для Завантаження бази даних із файлу
def dec_load_phoneDB(func):
    def inner(_):
        return book.load_database(book, path)
    return inner


# Декоратор для Збереження бази даних у файл
def dec_save_phoneDB(func):
    def inner(_):
        return book.save_database(book, path)   
    return inner 
 
 
# Функція викликає оброботчик команд
@input_error 
def run_handler(handler, cmd, prm):

    if cmd in ["add", "phone", "add phone", "del phone", "change phone"]:
        result = handler(prm)
    elif cmd in ["close", "exit", "good bye"]:
        result = handler("")
    elif cmd in ["save", "load"]:
        result = handler(path)            
    elif cmd in ["show all", "hello", "cls"]:
        result = handler("")
    return result
     
     
# Повертає адресу функції, що обробляє команду користувача
def get_handler(operator):
    return OPERATIONS[operator]    


#=========================================================
# >> add ...  DONE
# По этой команде бот сохраняет в памяти (в словаре например) новый контакт. 
# Вместо ... пользователь вводит ИМЯ и НОМЕР телефона, обязательно через пробел.
#=========================================================
@dec_func_add_rec
def func_add_rec(prm):
    
    # порахуємо кількість параметрів
    count_prm = get_count_prm(prm)
        
    if prm and (count_prm >= 2):
        # Якщо ключ (ІМ'Я) що користувач хоче ДОДАТИ не ІСНУЄ тобто можемо додавати
        if not prm.partition(" ")[0].capitalize() in book.keys():
            new_name = Name(prm.partition(" ")[0].capitalize())
            
            # формуємо список телефонів
            lst_phones = list(map(lambda phone: Phone(phone.strip()), prm.partition(" ")[2].split(",")))
            rec = Record(new_name, lst_phones)
            book.add_record(rec)
            
            return "1 record was successfully added"
        else: return "The person is already in database"  # Повернемо помилку -> "Неможливо дадати існуючу людину"
    else:
        return f"Expected 2 arguments, but {count_prm} was given.\nHer's an example >> add Name 0499587612"
     
     
#=========================================================
# >> show all         Done
# По этой команде бот выводит все сохраненные контакты 
# с номерами телефонов в консоль.
#=========================================================
@dec_func_all_phone
def func_all_phone(_)->str:
    result = ""
    result = "\n".join([f"{n}: {', '.join(map(lambda phone: phone.value, record.phones))}" for n, record in book.data.items()])
        
    if result == "": return "The database is empty"
    else: return result


#=========================================================
# >> change phone... Done
# По этой команде бот сохраняет в памяти новый номер телефона 
# для существующего контакта. 
# Вместо [...] пользователь вводит [Ім'я] [старий Номер телефона] [Новий номер], 
# Увага: обязательно через пробел!!!
# >> change phone Mike +38099 +38050777
#=========================================================
@dec_func_change_phone  
def func_change_phone(prm):
    # порахуємо кількість параметрів
    count_prm = get_count_prm(prm)
    if prm and (count_prm >= 3):
        name = prm.partition(" ")[0].lower().capitalize()
            
        if name in book.keys():
            lst = prm.split()
            
            # перевіремо наявність телефону що будемо замінювати у базі даних
            number_exists = any(phone.value == lst[1] for phone in book[name].phones)
            if number_exists:
                return book[name].edit_phone(Phone(lst[1]), Phone(lst[2]))
            else:
                return f"The phone {lst[1]} for {name} isn't in the database"
        else:
            return f"The record {name} wasn't found in the database"
    else: 
        return f"Expected 3 arguments, but {count_prm} was given.\nHer's an example >> change phone Mike +0449587612 +380995437856"


#=========================================================
# >> "good bye", "close", "exit"
# По любой из этих команд бот завершает свою роботу 
# после того, как выведет в консоль "Good bye!".
#=========================================================
@dec_func_exit
def func_exit(_):
    return "Good bye!"


#=========================================================
# >> hello
# Отвечает в консоль "How can I help you?"
#=========================================================
@dec_func_greeting
def func_greeting(_):
    return "How can I help you?"


#=========================================================
# >> phone ... Done
# По этой команде бот выводит в консоль номер телефона для указанного контакта.
# Вместо ... пользователь вводит Имя контакта, чей номер нужно показать.
# >> phone Ben
#=========================================================
@dec_func_phone
def func_phone(prm):
    prm = prm.split(" ")
    if prm[0] == "": return f'Missed "Name" of the person'
    name = prm[0].lower().capitalize()
    if name in book.keys():   
        if prm: return ", ".join([phone.value for phone in book[name].phones])
        else: return f"Expected 1 argument, but 0 was given.\nHer's an example >> phone Name"
    else:
        return f"The {name} isn't in the database"  
    

#=========================================================
# >> add phone    Done
# функція розширює новіми телефонами існуючий запис особи Mike   
# >> add phone Mike +380509998877, +380732225566
#=========================================================
def func_add_phone(prm):
    # порахуємо кількість параметрів
    count_prm = get_count_prm(prm)
    
    prm = prm.split(" ")
    if prm[0] == "": return f'Missed "Name" of the person'
    
    if prm and (count_prm >= 2):
        name = prm[0].lower().capitalize()
        if name in book.keys():   
            prm.remove(name)  
            # приберемо коми із телефонів
            lst_add_phones = list(map(lambda phone: Phone(re.sub(",", "", phone)), prm))
            return book[name].add_phone(lst_add_phones)  # викликаємо Метод класу 
        else:
            return f"The {name} isn't in database"
    else: return f"Expected 2 arguments, but {count_prm} was given.\nHer's an example >> add phone Mike +380509998877"
        
    

#=========================================================
# >> del phone    Done
# функція видаляє телефон або список телефонів в існуючому записі особи Mike   
# >> del phone Mike +380509998877, +380732225566
#=========================================================    
def func_del_phone(prm):
    # порахуємо кількість параметрів
    count_prm = get_count_prm(prm)
    
    prm = prm.split(" ")
    if prm[0] == "": return f'Missed "Name" of the person'
    
    if prm and (count_prm >= 2):
        name = prm[0].lower().capitalize()
        if name in book.keys():
            prm.remove(name)  
            
            # перевіремо наявність телефону що будемо видаляти із бази даних
            number_exists = any(phone.value == prm[0] for phone in book[name].phones)
            if number_exists:
                # приберемо коми із телефонів
                # формуємо список  об'єктів Phone, тому що на майбутнє хочу реалізувати видалення декількох телефонів 
                lst_del_phones = list(map(lambda phone: Phone(re.sub(",", "", phone)), prm)) 
                return book[name].del_phone(lst_del_phones[0])
            else:
                return f"The phone {prm[0]} isn't in the database"
            
        else:
            return f"The name {name} isn't in database."
    else: return f"Expected 2 arguments, but {count_prm} was given.\nHer's an example >> del phone Mike +380509998877"


#=========================================================
# Функція читає базу даних з файлу - ОК
#========================================================= 
@dec_load_phoneDB
def load_phoneDB(path):
    return book.load_database(book, path)


#=========================================================
# Функція виконує збереження бази даних у файл *.csv - OK
#========================================================= 
@dec_save_phoneDB
def save_phoneDB(path):
    return book.save_database(book, path)
    
    
#=========================================================
# Функція виконує парсер команд та відповідних параметрів
#=========================================================
def parcer_commands(cmd_line):
    lst, tmp, cmd, prm  = [[], [], "", ""]
    
    if cmd_line:
        tmp = cmd_line.split()
        
        # перевіремо ПОДВІЙНУ команду
        if len(tmp) > 1 and f"{tmp[0]} {tmp[1]}".lower() in COMMANDS:
            cmd = f"{tmp[0]} {tmp[1]}".lower()
            prm = cmd_line.partition(cmd)[2].strip()
            
        # перевіремо ОДИНАРНУ команду
        elif tmp[0].lower() in COMMANDS:
            cmd = tmp[0].lower()
            prm = cmd_line.partition(" ")[2]
    return cmd, prm


def clear_screen(_):
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        os.system('cls')
    elif os_name == 'linux' or os_name == 'darwin':
        os.system('clear')
    return ""


# Рахує та повертає кількість параметрів
def get_count_prm(prm: list):
    if len(prm) > 0: 
        count_prm = prm.count(" ", 0, -1) + 1
    else: count_prm = 0
    return count_prm


COMMANDS = ["good bye", "close", "exit",
            "hello", "add", "phone", "show all", "save", "load", "cls", "add phone", "del phone", "change phone"]

OPERATIONS = {"good bye": func_exit, "close": func_exit, "exit": func_exit,
              "hello": func_greeting, 
              "add": func_add_rec,
              "phone": func_phone, 
              "show all": func_all_phone,
              "save": save_phoneDB,
              "load": load_phoneDB,
              "cls": clear_screen,
              "add phone": func_add_phone,
              "del phone": func_del_phone,              
              "change phone": func_change_phone,}

        
if __name__ == "__main__":
    main()
    