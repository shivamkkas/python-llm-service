class Models:
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"

    @classmethod
    def list(cls):
        return [cls.CLAUDE, cls.OPENAI, cls.GEMINI, cls.OLLAMA]

    @classmethod
    def validate(cls, model: str) -> bool:
        return model in cls.list()

class ModelRegistry:

    CLAUDE_MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]

    OPENAI_MODELS = [
        "gpt-4o",
        "gpt-4o-mini"
    ]

    GEMINI_MODELS = [
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]