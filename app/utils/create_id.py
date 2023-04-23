from random import choice

ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789'
PARTS = 5
LEN_PARTS = [8, 4, 4, 4, 12]


# Здесь создаем строку похожую по формату на ту, что в ТЗ
async def create_id():
    search_id = ''
    for i in range(PARTS):
        for j in range(LEN_PARTS[i]):
            search_id += choice(ALPHABET)
        search_id += '-'
    search_id = search_id[:-1]

    return search_id
