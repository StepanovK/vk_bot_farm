from peewee import *
from Models.base import BaseModel


class Account(BaseModel):
    vk_id = IntegerField(100)
    login = CharField(100)
    password = CharField(150, default='')
    token = TextField(null=True)
    first_name = CharField(100, default='', null=True)
    last_name = CharField(100, default='', null=True)
    sex = CharField(10, null=True)
    birth_date = DateField(null=True)
    is_active = BooleanField(default=True)
    comment = TextField(default='')
    reg_date = DateField(null=True)

    class Meta:
        table_name = 'accounts'

    def __str__(self):
        return self.chat_name()

    def chat_name(self):
        f_name = self.full_name()
        if f_name == '':
            return f'[id{self.vk_id}]'
        else:
            return f'[id{self.vk_id}|{f_name}]'

    def full_name(self):
        f_name = f'{self.first_name} {self.last_name}'
        return f_name.strip()
