import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Credenciales del Desarrollador / Agencia
    DESARROLLADOR_NOMBRE = os.getenv("DESARROLLADOR_NOMBRE", "Favian C.")
    AGENCIA_NOMBRE = os.getenv("AGENCIA_NOMBRE", "LapShop Tecnologias")
    
    # Base de Datos
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:@localhost:3306/agentes_db"
    )

config = Config()