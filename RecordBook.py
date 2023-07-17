
from collections import UserDict
import re

class Field():
    def __init__(self, value) -> None:
        self.value = value
        
class Name(Field):
    pass

class Phone(Field): 
    pass
    

#========================================================
# Класс Record, который отвечает за логику 
#  - добавления/удаления/редактирования
# необязательных полей и хранения обязательного поля Name
#=========================================================
class Record():
    def __init__(self, name: Name, phones: list[Phone]=None) -> None:
        self.name = name            # <- об'єкт name
        self.phones = []            # <- список об'єктов phone
        self.phones.extend(phones)
    
    # Done - розширюємо існуючий список телефонів особи - Done
    # НОВИМ телефоном або декількома телефонами для особи - Done
    def add_phone(self, new_phone: list[Phone]) -> str:
        self.phones.extend(new_phone)
        return f"The phones was/were added - success"
    
    # Done - видаляємо телефони із списку телефонів особи - Done!
    def del_phone(self, del_phone: Phone) -> str:
        error = True
        for phone in self.phones:
                if phone.value == del_phone.value: 
                    self.phones.remove(phone) 
                    error = False  #видалення пройшло з успіхом
                    break
        if error: return f"The error has occurred. You entered an incorrect phone number."
        else: return f"The phone {phone.value} was deleted - success"
    
    # Done = редагування запису(телефону) у книзі особи - Done
    def edit_phone(self, old_phone: Phone, new_phone: Phone) -> str:
        index = next((i for i, obj in enumerate(self.phones) if obj.value == old_phone.value), -1)
        self.phones[index]= new_phone
        return f"The person {self.name.value} has a new phone {new_phone.value} - success"
    


class AddressBook(UserDict):
    
    def add_record(self, record):
        self.data[record.name.value] = record
    
    # збереження записів книги у файлі        
    def load_database(self, book, path):
        with open(path, "r") as f_read:
            while True:                
                line = f_read.readline()
                if not line:
                    break
                if line[-1] == "\n":
                    line = line[:-1]
                
                person = line.partition(":")[0]
                name = Name(person)
                # видалемо ім'я особи із строки
                line = line.removeprefix(f"{person}:")
                
                rec = Record(name, list(map(lambda phone : Phone(re.sub(",", "", phone).strip()), line.split(", "))))
                self.add_record(rec)
        return f"The database has been loaded = {len(book)} records"
    
    # завантаження записів книги із файлу
    def save_database(self, book, path):
        with open(path, "w") as f_out:
            f_out.write("\n".join([":".join([name, ", ".join(phone.value for phone in rec_phones.phones)]) for name, rec_phones in book.data.items()]))
        return f"The database is saved = {len(book)} records"  
    
    
          
        
