from peewee import *
from Models.base import BaseModel


class TelegramUser(BaseModel):
    id = BigIntegerField(primary_key=True)
    login = CharField(100, null=True)
    first_name = CharField(150, default='')
    last_name = CharField(150, default='')

    class Meta:
        table_name = 'telegram_users'

    def __str__(self):
        if self.gl_login and self.web_url != '':
            return f'@{self.gl_login}'
        elif self.first_name != '' or self.last_name != '':
            return (self.first_name + ' ' + self.last_name).strip()
        else:
            return f'ID{self.tg_id}'
