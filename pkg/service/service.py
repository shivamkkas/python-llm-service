class LLMService:
    _instance = None

    def __new__(cls, models=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_models(models or {})
        return cls._instance

    def _init_models(self, models):
        self.models = models

    def Get_model(self, model_name):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not registered")
        return self.models[model_name]