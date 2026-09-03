from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config import config

# 1. Configuración del motor con credenciales desde config.py
Engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True  # Valida la conexión antes de ejecutar consultas para evitar caídas silenciosas
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()

# 2. Modelo ORM para la tabla de prospectos
class ProspectoModel(Base):
    __tablename__ = "prospectos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    negocio = Column(String(255), nullable=False)
    contacto = Column(String(255), nullable=True)
    diagnostico = Column(Text, nullable=True)
    solucion = Column(Text, nullable=True)
    pitch_whatsapp = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

# 3. Creación automatizada de tablas en MySQL
def inicializar_db():
    """Crea las tablas en la base de datos si no existen previamente."""
    Base.metadata.create_all(bind=Engine)

# 4. Operación segura de inserción masiva
def guardar_prospectos(lista_prospectos: list[dict]):
    """
    Inserta una lista de prospectos en MySQL usando transacciones seguras.
    """
    db = SessionLocal()
    try:
        for p in lista_prospectos:
            prospecto = ProspectoModel(
                negocio=p["negocio"],
                contacto=p["contacto"],
                diagnostico=p["diagnostico"],
                solucion=p["solucion"],
                pitch_whatsapp=p["pitch_whatsapp"]
            )
            db.add(prospecto)
        
        db.commit()
        print(f"-> {len(lista_prospectos)} prospectos guardados exitosamente en la BD.")
    except Exception as e:
        db.rollback()
        print(f"-> Error de seguridad/transacción en Base de Datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("--- INICIALIZANDO TABLAS EN MYSQL WORKBENCH ---")
    inicializar_db()
    print("Tablas verificadas y listas.")