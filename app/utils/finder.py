import asyncio
import re

import pytz

from app.database.__models import Folder, File
from app.database.db_session import create_session


# Сделал Z функцию для поиска подстроки в строке
async def find_subseq(pattern: str, text: str):
    def z_function(a: str):
        pref_arr = [0] * len(a)
        for i in range(1, len(a)):
            j = pref_arr[i - 1]
            if a[i] == a[j]:
                pref_arr[i] = j + 1
            else:
                while j > 0 and a[i] != a[j]:
                    j = pref_arr[j - 1]
                    if a[i] == a[j]:
                        pref_arr[i] = j + 1
        return pref_arr

    res = z_function(pattern + '#' + text)
    for i in range(len(res)):
        if len(pattern) == res[i]:
            return True
    return False


# Здесь происходит фильтрация файла по тексту, маске, размеру и времени.
async def file_filter(file, text, file_mask, size, creation_time):
    file_name = file.file_url.split('/')[-1]
    try:
        if not re.match(file_mask, file_name):
            return False
    except re.error:
        raise 'nothing to repeat at position 0'

    if size.operator == 'eq':
        if file.size != size.value:
            return False
    elif size.operator == 'gt':
        if file.size <= size.value:
            return False
    elif size.operator == 'lt':
        if file.size >= size.value:
            return False
    elif size.operator == 'ge':
        if file.size < size.value:
            return False
    elif size.operator == 'le':
        if file.size > size.value:
            return False

    utc = pytz.UTC
    if creation_time.operator == 'eq':
        if file.creation_time.replace(tzinfo=utc) != creation_time.value:
            return False
    elif creation_time.operator == 'gt':
        if file.creation_time.replace(tzinfo=utc) <= creation_time.value:
            return False
    elif creation_time.operator == 'lt':
        if file.creation_time.replace(tzinfo=utc) >= creation_time.value:
            return False
    elif creation_time.operator == 'ge':
        if file.creation_time.replace(tzinfo=utc) < creation_time.value:
            return False
    elif creation_time.operator == 'le':
        if file.creation_time.replace(tzinfo=utc) > creation_time.value:
            return False

    if not await find_subseq(text, file.file_text):
        return False

    return True


# Поиск файлов (работает по типу BFS)
async def finder(url, text, file_mask, size, creation_time, result_paths):
    await asyncio.sleep(5) # это важное замечание. Делаю sleep, чтобы смоделировать работу поиска на больших данных.
    session = create_session()

    # Ищем текущую директорию
    current_folder_id = list(session.query(Folder.id).filter(Folder.folder_url == url))[0][0]
    # Ищем папки, которые лежат в текущей директории
    tmp_folders = list(session.query(Folder).filter(Folder.parent_id == current_folder_id))

    # Рекурсивно обходим каждую папку, набирая новые папки
    for tmp_folder in tmp_folders:
        if tmp_folder.folder_url != '/':
            await finder(tmp_folder.folder_url, text, file_mask, size, creation_time, result_paths)

    # Собираем файлы в текущей папке. Из-за рекурсии, мы соберем из каждой папки все файлы
    tmp_files = list(session.query(File).filter(File.parent_id == current_folder_id))

    # Здесь происходит фильтрация файлов. Если файл прошел фильтрацию, то мы добавляем в список путь до фалйа.
    for tmp_file in tmp_files:
        if await file_filter(tmp_file, text, file_mask, size, creation_time):
            result_paths.append(tmp_file.file_url)
    # Возвращаем пути до подходящих файлов.
    return result_paths
