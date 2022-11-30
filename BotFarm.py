import datetime

import config
from config import logger
from common.exeptions import *
from Models.base import db
from Models.Accounts import Account
from Models.Tasks import Task, BotTask, ActionTypes
from utils.connection_holder import ConnectionsHolder

from typing import Optional

import random


class VKBot:
    def __init__(self, account: Optional[Account] = None, auto_connect=True):
        self.account = account
        self.vk_id = account.vk_id
        if auto_connect:
            self.connect()
        else:
            self.vk_connection = None
            self.vk_api = None

    def connect(self, force=False):
        self.vk_connection = self._get_vk_connection(force)
        self.vk_api = self._get_vk_api(force)

    def _get_vk_connection(self, force):
        return ConnectionsHolder().get_vk_user_connection(self.account.vk_id, self.account.login,
                                                          self.account.password, self.account.token, force)

    def _get_vk_api(self, force):
        return ConnectionsHolder().get_vk_user_api(self.account.vk_id, self.account.login,
                                                   self.account.password, self.account.token, force)

    def execute(self, task: Task, params=None):
        if task.action == ActionTypes.ADD_POST_LIKE.value:
            self._add_post_like(url=task.vk_object_url)

    def _add_post_like(self, url: str):
        owner_id, post_id = self._owner_and_post_id_from_url(url)
        res = self.vk_api.likes.add(
            type='post',
            owner_id=owner_id,
            item_id=post_id,
        )
        if config.debug:
            logger.info(f'Добавление лайка к посту {url}: {res}')

    @staticmethod
    def _owner_and_post_id_from_url(url: str) -> tuple[int, int]:
        owner_id_post_id = url.replace('https://vk.com/wall', '')
        owner_id_post_id = owner_id_post_id.replace('vk.com/wall', '')
        owner_id_post_id = owner_id_post_id.replace('wall', '')
        owner_id_post_id = owner_id_post_id.replace('/', '')
        owner_id_post_id_list = owner_id_post_id.split('_')
        if len(owner_id_post_id_list) != 2:
            raise WrongURLException(f'Wrong post url {url}!')
        owner_id = owner_id_post_id_list[0]
        post_id = owner_id_post_id_list[1]
        try:
            owner_id = int(owner_id)
        except ValueError:
            raise WrongURLException(f'Wrong post url {url}! Owner ID is not digital ({owner_id}).')
        try:
            post_id = int(post_id)
        except ValueError:
            raise WrongURLException(f'Wrong post url {url}! Post ID is not digital ({post_id}).')

        return owner_id, post_id


def schedule_tasks():
    task_query = Task.select().where(
        (Task.from_date <= datetime.datetime.now())
        and (Task.is_scheduled == False)
    )
    with db.atomic():
        for task in task_query.execute():
            _schedule_task(task)
            task.is_scheduled = True
            task.save()


def _schedule_task(task: Task):
    available_accounts = Account.select().limit(task.number_of_bots).where(
        (Account.is_active == True)
    ).execute()

    if len(available_accounts) < task.number_of_bots:
        raise NotEnoughAccountsException(
            msg=f'Недостаточно аккаунтов для выполнения задания {task} '
                f'(доступно: {len(available_accounts)}, требуется: {task.number_of_bots})')

    for account in available_accounts:
        bot_task = _schedule_task_for_account(task, account)


def _schedule_task_for_account(task: Task, account: Account) -> BotTask:
    bot_task = BotTask()
    bot_task.task = task
    bot_task.account = account
    bot_task.date = _randomize_date(task.from_date, task.to_date)
    bot_task.save()
    return bot_task


def _randomize_date(from_date: Optional[datetime.datetime] = None,
                    to_date: Optional[datetime.datetime] = None) -> datetime.datetime:
    date_from = datetime.datetime.now() if from_date is None else from_date
    if to_date is None:
        return date_from

    seconds = (to_date - date_from).seconds
    new_date = date_from + datetime.timedelta(seconds=random.randint(0, seconds))
    return new_date


def execute_tasks():
    bot_tasks = BotTask.select().where(
        (BotTask.is_completed == False) &
        (BotTask.date <= datetime.datetime.now())
    ).order_by(BotTask.account, BotTask.date).execute()

    account = None
    bot = None
    for bot_task in bot_tasks:
        if bot_task.account != account:
            account = bot_task.account
            bot = VKBot(account=account, auto_connect=True)
        try:
            bot.execute(task=bot_task.task, params=bot_task.params)
            bot_task.is_completed = True
            bot_task.date_of_completion = datetime.datetime.now()
        except Exception as ex:
            logger.error(f'Во время выполнения задачи {bot_task.task} ботом {account} возникла ошибка:\n{ex}')
            bot_task.errors = (bot_task.errors + f'\n{ex}').strip()
            bot_task.is_completed = True
        bot_task.save()
