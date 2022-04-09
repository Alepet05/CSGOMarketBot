import csv
import time
import login
import api_key_generator
import query
import json


def get_market_items_db(current_db_file_name: str):
    """Возвращает базу данных всех вещей на продаже в фиксированный момент времени

    Args:
        current_db_file_name (str): имя файла базы данных, формат csv

    Returns:
        market_items_db (str): CSV-файл с данными в формате строки
    """
    db_file_url = f'https://market.csgo.com/itemdb/{current_db_file_name}' # url-адрес файла базы данных
    market_items_db = query.get_content(db_file_url) # получаем базу данных вещей
    return market_items_db 

def get_current_db_file_name():
    """Возвращает текущее имя файла базы данных

    Returns:
        current_db_file_name (str): имя файла базы данных, формат csv
    """
    url = 'https://market.csgo.com/itemdb/current_730.json' # адрес имени файла базы данных
    current_db_file_name = query.get_content(url, flag='json')['db'] # получение имени БД
    return current_db_file_name

def write_market_items_to_file(market_items_db: str):
    """Сохраняет базу данных вещей на продаже в фиксированный момент времени в csv-файл

    Args:
        market_items_db (str): CSV-файл с данными в формате строки
    """
    with open('market_items.csv', 'w', encoding='utf-8') as file:
        file.write(market_items_db)

def update_market_items():
    """Обновляет базу данных всех вещей на продаже в фиксированный момент времени

    Информация о предметах на главной странице сайте строится из предложений продавцов, 
    находящихся в данный момент онлайн на сайте. Она хранится в специальной базе данных и обновляется раз в минуту.
    Таким образом, сканировать главную или выполнять поиск по предметам чаще, чем раз в минуту, 
    не имеет смысла и создаёт избыточную нагрузку на наш сервер. (c) CSGO Market
    """
    current_db_file_name = get_current_db_file_name() # имя файла базы данных
    market_items_db = get_market_items_db(current_db_file_name) # сама база данных вещей
    write_market_items_to_file(market_items_db) # сохранение
    # write_market_items_to_file(get_market_items_db(get_current_db_file_name()))

def update_stickers():
    """Обновляет файл со стикерами, полученных с сервера.
    """
    api_key = api_key_generator.get_api_key()
    url = f'https://market.csgo.com/api/GetStickers/?key={api_key}&lang=ru' # чтобы получить словарь стикеров, маркету необходим api-ключ
    stickers = query.get_content(url, flag='json') # получаем стикеры в json формате
    write_stickers_to_file(stickers) # сохраняем стикеры

def get_stickers():
    """Возвращает все возможные стикеры с их идентификаторами на торговой площадке.

    Returns:
        list: список словарей со стикерами
    """
    # считываем стикеры из файла
    with open('stickers.json', 'r', encoding='utf-8') as file:
        stickers = json.load(file)
    return stickers['stickers'] # возвращаем непосредственно список словарей со стикерами

def write_stickers_to_file(stickers):
    """Сохраняет все стикеры в json-файл
    """
    with open('stickers.json', 'w', encoding='utf-8') as file:
        json.dump(stickers, file, indent=4, ensure_ascii=False)

def get_user_stickers_ids(user_stickers_names: list):
    """Ищет пользовательские стикеры по их названию в базе всех стикеров.
    Возвращает список ID всех найденных пользовательских стикеров в базе всех стикеров

    Зачем? Дело в том, что у предметов на торговой площадке указываются не названия стикеров, а ID стикеров
    Args:
        user_stickers_name (list): список указанных пользователем названий стикеров

    Returns:
        user_stickers_ids (list): список ID всех указанных пользователем стикеров, которые удалось найти базе данных всех стикеров
    """
    stickers = get_stickers() # получаем стикеры из базы данных
    # проходимся по каждому стикеру в базе данных
    # и проверяем, есть ли название этого стикера в списке названий пользовательских стикеров;
    # если да, то записываем его ID в список ID всех указанных пользователем стикеров
    user_stickers_ids = [sticker['id'] for sticker in filter(lambda sticker: sticker['name'] in user_stickers_names, stickers)]
    return user_stickers_ids

# по каким-то причинам сервер https://float.csgo.com/ лежит, возвращает ошибки типа 500
# def get_item_float_hash(classid: str, instanceid: str):
#     """Получает хэш предмета для запроса Float Value (потертость) со специального сервера

#     Args:
#         classid (str): ClassID предмета в Steam
#         instanceid (str): InstanceID предмета в Steam

#     Returns:
#         float_hash (str): хэш для получения float предмета
#     """
#     api_key = api_key_generator.get_api_key()  
#     url = f'https://market.csgo.com/api/GetFloatHash/{classid}_{instanceid}/?key={api_key}'
#     float_hash = query.get_content(url, flag='json')['hash']
#     return float_hash

# def get_item_float(classid: str, instanceid: str):
#     """Получает значения Float предмета: Float Value (потертость), Seed, Index

#     Args:
#         classid (str): ClassID предмета в Steam
#         instanceid (str): InstanceID предмета в Steam

#     Returns:
#         item_float (dict): информация float: непосредственно значение float, seed и index
#     """
#     url = 'https://float.csgo.com/'
#     float_hash = get_item_float_hash(classid, instanceid)
#     content = query.get_content(url, flag='json', req=float_hash)
#     if content['status']:
#         item_float = {
#             'float': content['paintwear'], 
#             'seed': content['paintseed'],
#             'index': content['paintindex']
#         }
#     else:
#         item_float = {}
#     return item_float

def get_item_float(classid: str, instanceid: str):
    """Получает значения Float предмета: Float Value (потертость), Seed, Index

    Args:
        classid (str): ClassID предмета в Steam
        instanceid (str): InstanceID предмета в Steam

    Returns:
        item_float (dict): информация float: непосредственно значение float, seed и index
    """
    url = f'https://market.csgo.com/float/{classid}/{instanceid}'
    content = query.get_content(url, flag='json')
    if content['status']:
        item_float = {
            'float_value': content['paintwear'], 
            'seed': content['paintseed'],
            'index': content['paintindex']
        }
    else:
        item_float = {}
    return item_float

def get_market_items():
    """Получает из csv-файла все предметы на продаже в фиксированный момент времени

    Returns:
        market_items (list): список словарей с информацией о предмете
    """

    market_items = [] # заранее объявляем список предметов
    
    # считываем данные из csv файла
    with open('market_items.csv', encoding='utf-8') as file:
        reader = csv.reader(file) # создаем объект reader
        headers = next(reader) # первая строка csv таблицы вида c_classid;c_instanceid;c_price;c_offers;c_popularity...
        # пробегаемся по каждому предмету в таблице
        for row in reader:
            item_data = {} # словарь с инфой о премете

            item_data['c_classid'] = row[0].split(';')[0] # ClassID предмета в Steam
            item_data['c_instanceid'] = row[0].split(';')[1] # InstanceID предмета в Steam
            item_data['price'] = row[0].split(';')[2] # цена предмета
            item_data['amount'] = row[0].split(';')[3] # кол-во доступных предметов
            item_data['quality'] = row[0].split(';')[6] # качество предмета
            item_data['sticker_ids'] = row[0].split(';')[9] # ID стикеров для поиска названий стикеров на предмете по их ID 
            item_data['name'] = row[0].split(';')[10] # название предмета
            try:
                item_data['hash_name'] = row[0].split(';')[12] # hash название предмета, некоторые методы api его требуют
            except IndexError: # не все предметы имеют hash name
                item_data['hash_name'] = ''
            item_data['url'] = f"https://market.csgo.com/item/{item_data['c_classid']}-{item_data['c_instanceid']}" # на всякий ссылка на предмет
            
            market_items.append(item_data)

    return market_items

def get_formatted_price(price: str):
    """Вывод цены в удобочитаемом формате

    Args:
        price (str): цена

    Returns:
        str: цена в нужном формате
    """

    price_list = list(price) # разбиваем строку на отдельные символы
    price_list.insert(-2, '.') # разделяем копейки от рублей 12999 -> 129.99
    return ''.join(price_list) # склеиваем строку обратно

def get_market_item_sticker_names(sticker_ids: list):
    """Ищет стикеры конкретного предмета по их ID в базе всех стикеров.
    Возвращает названия всех найденных на предмете стикеров.

    Args:
        sticker_ids (list): список ID стикеров на предмете

    Returns:
        srt: названия всех найденных на предмете стикеров, разделенных ', ' 
    """
    sticker_ids_list = sticker_ids.split('|') # разбиваем строку на отдельные ID например, (9272819286|9144421154|5227247238|)
    stickers = get_stickers() # получаем стикеры
    # проходимся по каждому стикеру в базе данных
    # и проверяем, есть ли ID этого стикера в списке ID стикера предмета;
    # если да, то записываем его название в список названий всех найденных на предмете стикеров
    sticker_names = [sticker['name'] for sticker in filter(lambda sticker: sticker['id'] in sticker_ids_list, stickers)]
    return ', '.join(sticker_names)

def print_item_info(item: dict):
    """Выводит информацию переданного предмета

    Args:
        item (dict): предмет маркета
    """
    print('#'*60)
    print('Новый предмет!')
    print(f"Предмет: {item['name']}")
    print(f"Цена: {get_formatted_price(item['price'])} RUB")
    print(f"Стикеры: {get_market_item_sticker_names(item['sticker_ids'])}")
    # получение флот занимает много времени, т.к. нужна пауза между запросами во избежание бана
    # item_float = get_item_float(item['c_classid'], item['c_instanceid'])
    # if item_float:
    #     print(f"Float: {item_float['float_value']}\nSeed: {item_float['seed']}\nIndex: {item_float['index']}")
    print(f"Ссылка: {item['url']}")
    print('#'*60)
    print('\n')

def search_market_items_by_stickers(market_items: list, user_stickers_ids: list, searched_items: list):
    """Ищет по стикерам предметы в базе данных всех вещей на продаже

    Args:
        market_items (list): список словарей с информацией о предмете
        user_stickers_ids (list): список ID пользовательских стикеров
        searched_items (list): найденные предметы

    Returns:
        searched_items (list): найденные предметы
    """
    for item in market_items: # проходимся по каждому предмету на площадке
        #if any(map(lambda user_sticker_id: user_sticker_id in item['sticker_ids'].split('|') and item not in searched_items, user_stickers_ids))
        for user_sticker_id in user_stickers_ids: # проходимся по каждому ID пользовательских стикеров
            # если очередной ID стикера пользователя в списке ID стикеров предмета и не в списке найденных предметов,
            # то добавляем предмет в список найденных и выводим его инфу
            if user_sticker_id in item['sticker_ids'].split('|') and item not in searched_items:
                searched_items.append(item)
                print_item_info(item)
    # оставляем в списке найденных предметов только те предметы, которые есть в списке всех предметов маркета
    # таким образом, длина списка найденных предметов никогда не будет превышать длину списка всех предметов маркета
    searched_items = list(filter(lambda item: item in market_items, searched_items))
    return searched_items

def write_searched_items_to_file(searched_items: list):
    """Записывает найденные предметы в json файл

    Args:
        searched_items (list): найденные предметы маркета
    """
    with open('searched_items.json', 'w', encoding='utf-8') as file:
        json.dump(searched_items, file, indent=4, ensure_ascii=False)

def get_user_stickers_from_file():
    """Получает стикеры пользователя из файла

    Returns:
        user_stickers (list): список стикеров пользователя
    """
    with open('user_stickers.txt', encoding='utf-8') as f:
        user_stickers = f.read().split('\n')
    return user_stickers

def main():
    if not login.login_to_steam():
        return False

    api_key_generator.create_api_key() # генерируем api-ключ
    update_stickers() # обновляем стикеры

    user_stickers_names = get_user_stickers_from_file() # достаем пользовательские стикеры
    user_stickers_ids = get_user_stickers_ids(user_stickers_names) # получаем ID пользовательских стикеров
    searched_items = [] # инициализируем список найденных вещей
    # предпологается, что бот постоянно уведомляет о новых предметах
    while True:
        update_market_items() # обновляем бд предметов на продаже
        market_items = get_market_items() # получаем предметы маркета 
        searched_items = search_market_items_by_stickers(market_items, user_stickers_ids, searched_items) # поиск нужных предметов
        write_searched_items_to_file(searched_items) # на всякий перезаписываем каждый раз список найденных предметов, таким образом в файле всегда относительно актуальные предметы
        time.sleep(60) # пауза между обновлением бд предметов

if __name__ == '__main__':
    main()