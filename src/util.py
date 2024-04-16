from urllib.parse import quote

class StringSanitizerUtil:

    @classmethod
    def _escape_special_symbols(cls, text: str) -> str:
        return quote(text)
    
    @classmethod
    def _double_symbol(cls, text: str, symbol: str) -> str:
        return text.replace(symbol, f"{symbol}{symbol}")
    
    @classmethod
    def sanitize(cls, text: str) -> str:
        text = cls._escape_special_symbols(text)
        return text
    
    @classmethod
    def alembic_url_sanitize(cls, text: str) -> str:
        text = cls._double_symbol(text, "%")
        return text