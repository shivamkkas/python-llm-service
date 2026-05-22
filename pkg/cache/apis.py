import os
from pkg.util import cypt
class APIKeyManager:

    def __init__(self, crypto:cypt.CryptoManager, base_path):
        self.__base_path = base_path
        self.__cache = {}
        self.__crypto = crypto 

    def __get_file(self, provider):
        return os.path.join(self.__base_path, f"{provider}.enc")

    def set_key(self, provider, api_key):
        enc = self.__crypto.encrypt(api_key)

        with open(self.__get_file(provider), "wb") as f:
            f.write(enc)

        self.__cache[provider] = api_key

    def get_key(self, provider):
        if provider in self.__cache:
            return self.__cache[provider]

        with open(self.__get_file(provider), "rb") as f:
            enc = f.read()

        key = self.__crypto.decrypt(enc)
        self.__cache[provider] = key

        return key