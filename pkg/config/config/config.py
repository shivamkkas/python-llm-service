import os
import yaml
from dataclasses import dataclass, field, asdict
from functools import lru_cache


# -------------------- Core Models --------------------

@dataclass
class Service:
    host: str = "0.0.0.0"
    port: int = 50053


@dataclass
class Setting:
    MAX_WORKER: int = 10
    MAX_MESSAGE_LENGTH: int = 100


@dataclass
class Provider:
    enable: bool = False
    base_url: str = ""


@dataclass
class Models:
    anthropic: Provider = field(default_factory=Provider)
    ollama: Provider = field(default_factory=Provider)
    openai: Provider = field(default_factory=Provider)
    gemini: Provider = field(default_factory=Provider)
    mcp: Provider = field(default_factory=Provider)


@dataclass
class RotationConfig:
    type: str = "size"
    when: str = "midnight"
    interval: int = 1
    backupCount: int = 7


@dataclass
class LogConfig:
    LOG_CONSOLE_ENABLED: bool = True
    LOG_FILE: str = "log/app.log"
    LOG_FILE_LEVEL: str = "INFO"
    LOG_LEVEL: str = "DEBUG"
    LOG_MAX_BACKUPS: int = 7
    ROTATION: RotationConfig = field(default_factory=RotationConfig)


@dataclass
class AppConfig:
    server: Service = field(default_factory=Service)
    models: Models = field(default_factory=Models)
    log: LogConfig = field(default_factory=LogConfig)
    setting: Setting = field(default_factory=Setting)


# -------------------- Config Loader --------------------

class Config:
    _instance = None

    def __new__(cls, filepath: str = "config.yaml"):
        if cls._instance is None or cls._instance._filepath != filepath:
            cls._instance = super().__new__(cls)
            cls._instance._filepath = filepath
            cls._instance._load()
        return cls._instance

    def _load(self):
        if not os.path.exists(self._filepath):
            raise FileNotFoundError(f"Config file not found: {self._filepath}")

        with open(self._filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.app = self._parse_app(data)

    def _parse_app(self, data: dict) -> AppConfig:
        """Safe nested parsing (Go-style unmarshalling)"""

        # -------- Server --------
        server_data = data.get("server", {}) or {}
        server = Service(**server_data)

        # -------- Models --------
        models_data = data.get("models", {}) or {}

        models = Models(
            anthropic=Provider(**models_data.get("anthropic", {})),
            ollama=Provider(**models_data.get("ollama", {})),
            openai=Provider(**models_data.get("openai", {})),
            gemini=Provider(**models_data.get("gemini", {})),
            mcp = Provider(**models_data.get("mcp", {})),
        )

        # -------- Log --------
        log_data = data.get("LOG", {}) or {}
        rotation_data = log_data.get("ROTATION", {}) or {}

        rotation = RotationConfig(**rotation_data)

        log = LogConfig(
            LOG_CONSOLE_ENABLED=log_data.get("LOG_CONSOLE_ENABLED", True),
            LOG_FILE=log_data.get("LOG_FILE", "log/app.log"),
            LOG_FILE_LEVEL=log_data.get("LOG_FILE_LEVEL", "INFO"),
            LOG_LEVEL=log_data.get("LOG_LEVEL", "DEBUG"),
            LOG_MAX_BACKUPS=log_data.get("LOG_MAX_BACKUPS", 7),
            ROTATION=rotation
        )

        # -------- Setting --------
        setting_data = data.get("setting", {}) or {}
        setting = Setting(**setting_data)

        return AppConfig(
            server=server,
            models=models,
            log=log,
            setting=setting
        )

    def reload(self):
        self._load()

    def as_dict(self):
        return asdict(self.app)

    @classmethod
    @lru_cache(maxsize=10)
    def load(cls, filepath: str = "config.yaml"):
        return cls(filepath)