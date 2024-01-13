import os

import dotenv


def read_env(key: str):
    return os.environ[key]


class Settings:
    def __init__(self) -> None:
        self.jp_secretKey = read_env("JP_SECRET_KEY")


dotenv.load_dotenv()
settings = Settings()
