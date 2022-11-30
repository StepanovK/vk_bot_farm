from utils.singleton import Singleton
from vk_api import vk_api
import config as config


class ConnectionsHolder(metaclass=Singleton):
    def __init__(self):
        self._vk_connections = {}
        self._vk_api = {}

    @staticmethod
    def close():
        ConnectionsHolder.instance._vk_connections = {}
        ConnectionsHolder.instance._vk_api = {}
        if config.debug:
            config.logger.info("All connections closed")

    def get_vk_user_api(self, vk_id: int,
                        login: str = None, password: str = None,
                        token: str = None, force=False):
        if not force:
            api = self._vk_api.get(vk_id)
            if api is not None:
                return api

        connection = self.get_vk_user_connection(vk_id, login, password, token, force)

        if connection is not None:
            try:
                api = connection.get_api()
                self._vk_api[vk_id] = api
            except Exception as ex:
                config.logger.error(f"Failed to get user id{vk_id} api: {ex}")

        return api

    def get_vk_user_connection(self, vk_id: int,
                               login: str = None, password: str = None,
                               token: str = None, force=False):
        connection = self._vk_connections.get(vk_id)

        if connection is None or force:
            try:
                if token is not None:
                    connection = vk_api.VkApi(token=token, api_version=config.vk_api_version)
                else:
                    connection = vk_api.VkApi(login=login, password=password, api_version=config.vk_api_version)
                if config.debug:
                    config.logger.info(f'User id{vk_id} is connected!')
                self._vk_connections[vk_id] = connection
            except Exception as ex:
                config.logger.error(f"Failed to connect user id{vk_id}: {ex}")

        return connection
