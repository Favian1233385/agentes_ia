import os
import itertools
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # Recolecta las claves individuales
        keys = [
            os.getenv("GOOGLE_API_KEY_1"),
            os.getenv("GOOGLE_API_KEY_2"),
            os.getenv("GOOGLE_API_KEY_3"),
            os.getenv("GOOGLE_API_KEY")
        ]
        # Filtra valores nulos, vacíos y elimina duplicados
        self.api_keys = list(dict.fromkeys([k.strip() for k in keys if k and k.strip()]))
        
        if not self.api_keys:
            raise ValueError("❌ No se encontró ninguna GOOGLE_API_KEY válida en el archivo .env")
            
        self._key_cycle = itertools.cycle(self.api_keys)

    def obtener_siguiente_key(self) -> str:
        """Devuelve explícitamente la siguiente API Key del ciclo."""
        return next(self._key_cycle)

    @property
    def GOOGLE_API_KEY(self) -> str:
        """Devuelve la primera clave activa por defecto."""
        return self.api_keys[0]

    DESARROLLADOR_NOMBRE = os.getenv("DESARROLLADOR_NOMBRE", "Favian C.")
    AGENCIA_NOMBRE = os.getenv("AGENCIA_NOMBRE", "Technologies LapShop")
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/agentes_db")

config = Config()