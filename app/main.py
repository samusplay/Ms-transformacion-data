from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure import models
from app.infrastructure.database import check_db_connection
from app.routers.api import api_router


#gestor de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\033[94m⚙️  Configurando servicios internos...\033[0m")
    
    # 🚨 ESTO ES LO QUE TE FALTA SAMUEL, ¡EL MOTOR!
    from app.infrastructure.database import Base, engine
    try:
        # Aquí es donde SQLAlchemy crea las tablas que importaste en 'models'
        Base.metadata.create_all(bind=engine)
        print("\033[92m✅ Tablas de TRANSFORMACIÓN creadas/verificadas\033[0m")
    except Exception as e:
        print(f"\033[91m🚨 Error creando tablas: {e}\033[0m")

    if check_db_connection():
        print("\033[92m✅ PERSISTENCIA: Conectado a PostgreSQL\033[0m")
    else:
        print("\033[91m🚨 PERSISTENCIA: Fallo al conectar a PostgreSQL\033[0m")
    
    yield
    print("\033[93m\nFinalizando procesos...\033[0m")

#Instaciamos app
app=FastAPI(
    title="Api transformación de datos",
    description="Responsable de procesar y calcular datos",
    lifespan=lifespan
)
#llamada a rutas 
app.include_router(api_router)