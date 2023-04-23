import asyncio

from fastapi import APIRouter, HTTPException
from starlette import status

from app.database.__models import Folder, File
from app.database.db_session import create_session
from app.schemas.__schemes import FolderModel, FileModel, SearchModel
from app.utils.create_id import create_id
from app.utils.finder import finder

router = APIRouter()

# Словарь, в котором храним search_id и таску (поиск файлов)
TASKS_TRACKER = {}


# Так как в ТЗ не было указано про то, откуда брать данные о файлах и папках, я сделал ручки,
# при помощи которых, можно добавлять папки и файлы в бд

# Создание папки и добавление в бд
@router.post(
    "/create/folder",
    name='create folder',
    status_code=status.HTTP_200_OK
)
async def create_folder(folder: FolderModel):
    FolderModel.validate(folder)  # Тут проходит валидация запроса, описанная в файле со схемами
    data = folder.url.split('/')

    # Получаем родительский url (полный путь до папки без самого названия папки)
    parent_url = '/' + '/'.join(data[1:-1])

    session = create_session()

    # Проверяем, существует ли путь, по которому мы можем создать папку. Если нет, выкидывает ошибку 404.
    parent_folder = list(session.query(Folder.id).filter(Folder.folder_url == parent_url))
    if not parent_folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There is no such parent folder: {parent_url}")

    # Проверяем на то, что папка уже существует, если да, то ошибка 400 (можно было что-то другое).
    is_folder_exist = list(session.query(Folder.id).filter(Folder.folder_url == folder.url))
    if is_folder_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Folder already exists")

    # Создаем объект класс Folder (папку), добавляем в бд и сохраняем.
    new_folder = Folder(parent_id=parent_folder[0][0], folder_url=folder.url)
    session.add(new_folder)
    session.commit()


@router.post(
    "/create/file",
    name='create file',
    status_code=status.HTTP_200_OK
)
async def create_file(file: FileModel):
    # Создание фалйа работает по аналогии с созданием папки
    FileModel.validate(file)
    data = file.url.split('/')
    parent_url = '/' + '/'.join(data[1:-1])

    session = create_session()
    parent_folder = list(session.query(Folder.id).filter(Folder.folder_url == parent_url))
    if not parent_folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There is no such parent folder: {parent_url}")

    is_file_exist = list(session.query(File.id).filter(File.file_url == file.url))
    if is_file_exist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File already exists")

    new_file = File(parent_id=parent_folder[0][0], file_url=file.url, file_text=file.text,
                    size=file.size, creation_time=file.creation_time)
    session.add(new_file)
    session.commit()


@router.post(
    "/search",
    name='create search',
    status_code=status.HTTP_200_OK
)
async def create_search(search: SearchModel):
    SearchModel.validate(search)  # Валидируем запрос на поиск

    search_id = await create_id()  # Создаем индентификатор поиска
    # Создаем поиск в виде таски
    task = asyncio.create_task(finder(search.url, search.text, search.file_mask,
                                      search.size, search.creation_time, []))
    # Кладем в словарик task_tracker
    TASKS_TRACKER[search_id] = task
    return {"search_id": search_id}


@router.get(
    "/searches/{search_id}",
    name='get search',
    status_code=status.HTTP_200_OK
)
async def get_search(search_id: str):
    # Если нет такого search_id, то выдаем ошибку 404
    if TASKS_TRACKER.get(search_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There is no such search_id: {search_id}")

    # Берем таску
    task = TASKS_TRACKER[search_id]

    # Если таска выполнена, то выдаем пути и убираем ее из TASK_TRACKER,
    # иначе выдаем информацию о том, что таска не завершилась
    if task.done():
        paths = [path for path in task.result()]
        TASKS_TRACKER.pop(search_id)
        return {"finished": True, "paths": paths}
    else:
        return {"finished": False}
