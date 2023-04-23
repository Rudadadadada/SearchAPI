import uvicorn
from fastapi import FastAPI

from app.config import DATABASE
from app.database.__models import Folder
from app.database.db_session import global_init
from app.routers import router


def get_application() -> FastAPI:
    # Запускаем фастапи
    application = FastAPI(title="API File Search")
    # Подключаем ручки
    application.include_router(router.router)
    return application


app = get_application()

# Создаем таблицы
global_init(DATABASE)
# Создаем корневую директорию /
Folder.create_root()

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
