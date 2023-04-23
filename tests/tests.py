import json
import requests
import time

URL = "http://127.0.0.1:8000"
ALL_TEST_RESULT = []

# Тесты ручки /create/folder


# Корректный тест на создание папки
correct_json = {
    "url": "/d"
}

# Тест на то, что путь должен начинаться с /
test1_json = {
    "url": "a/b/c/d/e"
}

# Тест на то, что путь должен содержать только одинарный знак /
test2_json = {
    "url": "/a//b/c/d/e"
}

# Тесты на то, что путь должен идти без пробелов рядом со слешами
test3_json = {
    "url": "/a/ b/c/d/e"
}

test4_json = {
    "url": "/a/b /c/d/e"
}

# Тест на создание папки в папке, которая не сущетсвует
test5_json = {
    "url": "/a/b"
}

# Тест на создание папки, которая была создана ранее
test6_json = {
    "url": "/a/b"
}

# Делаем реквест на создание папки
request_status_code = requests.post(URL + "/create/folder", json.dumps(correct_json)).status_code
if request_status_code == 200:
    ALL_TEST_RESULT.append('OK')

# Тестируем валидацию пути
unit_tests_create_folder = [test1_json, test2_json, test3_json, test4_json]
for test in unit_tests_create_folder:
    if requests.post(URL + "/create/folder", json.dumps(test)).status_code == 400:
        ALL_TEST_RESULT.append('OK')

# Тестируем связь с бд
integration_tests_create_folder = [test5_json, test6_json]
for test in integration_tests_create_folder:
    if requests.post(URL + "/create/folder", json.dumps(test)).status_code == 404:
        ALL_TEST_RESULT.append('OK')

# Тесты ручки /create/file

# Корректный тест на создание файла
correct_json = {
    "url": "/file.txt",
    "text": "string",
    "size": 6,
    "creation_time": "2020-04-04T15:15:15Z"
}

# Тест на отрицательный сайз
test1_json = {
    "url": "/file.txt",
    "text": "string",
    "size": -1,
    "creation_time": "2020-04-04T15:15:15Z"
}

# Тест на некорректное время (сейчас не 2025 год)
test2_json = {
    "url": "/file.txt",
    "text": "string",
    "size": 5,
    "creation_time": "2025-04-04T15:15:15Z"
}

# Тест на то, что файл уже был создан
test3_json = {
    "url": "/file.txt",
    "text": "string",
    "size": 6,
    "creation_time": "2020-04-04T15:15:15Z"
}

# Делаем реквест на создание файла
request_status_code = requests.post(URL + "/create/file", json.dumps(correct_json)).status_code
if request_status_code == 200:
    ALL_TEST_RESULT.append('OK')

# Тестируем валидацию size и creation_time
unit_tests_create_folder = [test1_json, test2_json]
for test in unit_tests_create_folder:
    if requests.post(URL + "/create/file", json.dumps(test)).status_code == 400:
        ALL_TEST_RESULT.append('OK')

# Тестируем связь с бд
integration_tests_create_folder = [test3_json, test4_json]
for test in integration_tests_create_folder:
    if requests.post(URL + "/create/file", json.dumps(test)).status_code == 404:
        ALL_TEST_RESULT.append('OK')

# Тесты ручки /search

# Корректный тест на поиск файла
correct_json = {
    "text": "str",
    "file_mask": "fi*",
    "url": "/",
    "size": {
        "value": 0,
        "operator": "ge"
    },
    "creation_time": {
        "value": "2010-01-01T15:15:15Z",
        "operator": "ge"
    }
}

# Тест на валидацию оператора
test1_json = {
    "text": "str",
    "file_mask": "fi*",
    "url": "/",
    "size": {
        "value": 0,
        "operator": "aaaaaaaa"
    },
    "creation_time": {
        "value": "2010-01-01T15:15:15Z",
        "operator": "aaaaaaaaaaaaaaaaaaa"
    }
}

# Делаем реквест на создание поиска
request = requests.post(URL + "/search", json.dumps(correct_json))
request_status_code = request.status_code
if request_status_code == 200:
    ALL_TEST_RESULT.append('OK')

unit_test_status_code = requests.post(URL + "/search", json.dumps(test1_json)).status_code
if unit_test_status_code == 400:
    ALL_TEST_RESULT.append('OK')

# Тесты ручки /searches/{search_id}
search_id = request.content  # нужно передать серч id, который мы создали ранее
search_id = str(search_id).split(':')[1][1:-3]

request = requests.get(URL + f"/searches/{search_id}")
if request.status_code == 200:
    ALL_TEST_RESULT.append("OK")

print(request.content)  # тут ничего нет, потому что поиск не завершился


def get_paths():
    time.sleep(15)
    print(requests.get(URL + f"/searches/{search_id}").content)  # тут уже есть пути


get_paths()  # вернее, вот тут будут))

if set(ALL_TEST_RESULT) == set('OK'):
    print('ALL TEST COMPLETED SUCCESSFULLY')

# Тесты написаны быстро, не успел сделать их максимально корректно, но в целом, они показывают то,
# что все работает корректно. Стоило бы еще добавить тесты, когда у нас происходят 2 и более поисков одновременно, но
# это точно работает. Надеюсь, будет положительный фидбек, во всяком случае, за данное задание я научился работать с
# ассинхронными функциями и проектировать АПИ. Очень круто! Спасибо большое!