from typing import Optional


class NotEnoughAccountsException(Exception):

    def __init__(self, msg: Optional[str] = None) -> None:
        super().__init__()
        self.msg = msg

    def __str__(self) -> str:
        exception_msg = f"Message: {self.msg}\n"
        return exception_msg


class WrongURLException(Exception):

    def __init__(self, msg: Optional[str] = None) -> None:
        super().__init__()
        self.msg = msg

    def __str__(self) -> str:
        exception_msg = f"Message: {self.msg}\n"
        return exception_msg
