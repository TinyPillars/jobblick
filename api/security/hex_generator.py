import secrets
from datetime import datetime, timedelta
from typing import Dict

class SecurityConfigGenerator:
    def __init__(self, algorithm: str = "HS256", token_expire_minutes: int = 30):
        self.algorithm = algorithm
        self.token_expire_delta = timedelta(minutes=token_expire_minutes)
        self.secret_key = self._generate_secret_key()

    def _generate_secret_key(self) -> str:
        return secrets.token_hex(32)

    def get_config(self) -> Dict[str, str]:
        return {
            "SECRET_KEY": self.secret_key,
            "ALGORITHM": self.algorithm,
            "ACCESS_TOKEN_EXPIRE_MINUTES": str(int(self.token_expire_delta.total_seconds() / 60))
        }

    def print_config(self) -> None:
        config = self.get_config()
        for key, value in config.items():
            print(f'{key} = "{value}"')

    def get_token_expiration(self) -> datetime:
        return datetime.utcnow() + self.token_expire_delta

# Usage example
"""if __name__ == "__main__":
    generator = SecurityConfigGenerator()
    generator.print_config()
    print(generator.secret_key)
    print(f"Token will expire at: {generator.get_token_expiration()}")"""