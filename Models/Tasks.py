from peewee import *
from Models.base import BaseModel
from Models.Accounts import Account
from Models.Telegram import TelegramUser
import enum


class Script(BaseModel):
    name = CharField(150, default='')
    is_scheduled = BooleanField(default=False)
    from_user = ForeignKeyField(TelegramUser, null=True)
    comment = TextField(default='')

    class Meta:
        table_name = 'scripts'


class Task(BaseModel):
    action = CharField(100)
    vk_object_url = CharField(250, default='')
    number_of_executions = IntegerField(default=1)
    number_of_bots = IntegerField(default=1)
    from_date = DateTimeField(null=True, formats=['%Y-%m-%d %H:%M:%S'])
    to_date = DateTimeField(null=True, formats=['%Y-%m-%d %H:%M:%S'])
    param1 = CharField(150, null=True)
    param2 = CharField(150, null=True)
    param3 = CharField(150, null=True)
    params = TextField(null=True)
    is_scheduled = BooleanField(default=False)
    from_user = ForeignKeyField(TelegramUser, null=True)
    script = ForeignKeyField(Script, null=True)
    comment = TextField(default='')

    class Meta:
        table_name = 'tasks'

    def __str__(self):
        return f'{self.action} {self.vk_object_url}'


class BotTask(BaseModel):
    account = ForeignKeyField(Account)
    task = ForeignKeyField(Task)
    date = DateTimeField(formats=['%Y-%m-%d %H:%M:%S'])
    is_completed = BooleanField(default=False)
    date_of_completion = DateTimeField(null=True, formats=['%Y-%m-%d %H:%M:%S'])
    params = TextField(null=True)
    errors = TextField(default='')

    class Meta:
        table_name = 'bot_tasks'

    def __str__(self):
        return f'@{self.account} {self.task}'


class ActionTypes(enum.Enum):
    ADD_POST_LIKE = 'ADD_POST_LIKE'
    REMOVE_POST_LIKE = 'REMOVE_POST_LIKE'
    ADD_COMMENT_LIKE = 'ADD_COMMENT_LIKE'
    REMOVE_COMMENT_LIKE = 'REMOVE_COMMENT_LIKE'
    JOIN_GROUP = 'JOIN_GROUP'
    LEAVE_GROUP = 'LEAVE_GROUP'
