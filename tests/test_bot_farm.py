import datetime
import config_test
import pytest

from Models.create_db import recreate_database, delete_database
from Models.base import db
from Models.Accounts import Account
from Models.Tasks import Task, BotTask, ActionTypes
from config import logger, test_user_id, test_user_login, test_user_pass, test_user_token, test_post_url
import BotFarm

from common.exeptions import NotEnoughAccountsException, WrongURLException

from time import sleep


def test_post_add_like():
    db.close()
    recreate_database()

    time_to_wait = 3

    account = _add_test_account()
    accounts = Account.select().execute()
    assert len(accounts) == 1
    assert accounts[0] == account

    # Добавляем задачу лайкнуть пост
    task_like = _add_task_like(time_to_wait)
    tasks = Task.select().execute()
    assert len(tasks) == 1
    assert tasks[0] == task_like

    # Планируем задачи
    BotFarm.schedule_tasks()
    bot_tasks = BotTask.select().execute()
    assert len(bot_tasks) == 1
    bot_task = bot_tasks[0]
    assert bot_task.date >= task_like.from_date
    assert bot_task.date <= task_like.to_date
    assert bot_task.task == task_like
    assert bot_task.account == account
    assert not bot_task.is_completed

    # Запускаем выполнение задач
    _execute_tasks(time_to_wait)
    bot_tasks = BotTask.select().execute()
    assert len(bot_tasks) == 1
    bot_task = bot_tasks[0]
    assert bot_task.is_completed

    db.close()
    delete_database()


def test_exception_not_enough_accounts():
    db.close()
    recreate_database()

    task_likes = _add_task_like(2)
    with pytest.raises(NotEnoughAccountsException):
        BotFarm.schedule_tasks()

    account = _add_test_account()
    account.is_active = False
    account.save()
    with pytest.raises(NotEnoughAccountsException):
        BotFarm.schedule_tasks()

    task_likes.number_of_bots = 5
    task_likes.save()
    account.is_active = True
    account.save()
    with pytest.raises(NotEnoughAccountsException):
        BotFarm.schedule_tasks()

    db.close()
    delete_database()


def test_exception_wrong_url():
    db.close()
    recreate_database()

    time_to_wait = 1

    _add_test_account()

    task_likes = _add_task_like(time_to_wait)
    task_likes.vk_object_url = ''
    task_likes.save()

    task_likes = _add_task_like(time_to_wait)
    task_likes.vk_object_url = 'https://vk.com/5654646?w=wall-49453498_1345345593'
    task_likes.save()

    BotFarm.schedule_tasks()
    _execute_tasks(time_to_wait)

    not_completed_bot_tasks = BotTask.select().where(BotTask.is_completed == False).execute()
    assert len(not_completed_bot_tasks) == 0

    completed_bot_tasks = BotTask.select().where(BotTask.is_completed == True).execute()
    assert len(completed_bot_tasks) == 2

    for bot_task in completed_bot_tasks:
        assert bot_task.errors != ''

    db.close()
    delete_database()


def _add_test_account() -> Account:
    account, _ = Account.get_or_create(
        vk_id=test_user_id,
        login=test_user_login,
        password=test_user_pass,
        token=test_user_token,
    )
    return account


def _add_task_like(time_to_wait) -> Task:
    task, _ = Task.get_or_create(
        action=ActionTypes.ADD_POST_LIKE.value,
        vk_object_url=test_post_url,
        number_of_bots=1,
    )

    task.from_date = datetime.datetime.now()
    task.to_date = datetime.datetime.now() + datetime.timedelta(seconds=time_to_wait)
    task.save()

    return task


def _execute_tasks(time_to_wait):
    stop_at = datetime.datetime.now() + datetime.timedelta(seconds=time_to_wait)
    while True:
        BotFarm.execute_tasks()
        if stop_at < datetime.datetime.now():
            break
        sleep(1)

#
# if __name__ == '__main__':
#     test_post_add_like()
