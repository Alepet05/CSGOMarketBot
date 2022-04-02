import csv
from turtle import update
import login
import api_key_generator
import query
import json


API_KEY = api_key_generator.get_api_key() # получаем api-ключ и работаем с ним но конца сеанса, иначе каждый вызов будет генерироваться новый api-ключ

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
    with open('market_items_db.csv', 'w', encoding='utf-8') as file:
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
    url = f'https://market.csgo.com/api/GetStickers/?key={API_KEY}&lang=ru' # чтобы получить словарь стикеров, маркету необходим api-ключ
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

def get_market_items():
    """Получает из csv-файла все предметы на продаже в фиксированный момент времени

    Returns:
        market_items (list): список словарей с информацией о предмете
    """

    market_items = [] # заранее объявляем список предметов
    
    # считываем данные из csv файла
    with open('market_items.csv', encoding='utf-8') as file:
        reader = csv.reader(file) # создаем объект reader
        # пробегаемся по каждому предмету в таблице
        for row in reader:
            item_data = {} # словарь с инфой о премете

            item_data['c_classid'] = row[0].split(';')[0] # полезная инфа
            item_data['c_instanceid'] = row[0].split(';')[1] # полезная инфа
            item_data['price'] = row[0].split(';')[2] # цена предмета
            item_data['amount'] = row[0].split(';')[3] # кол-во доступных предметов
            item_data['quality'] = row[0].split(';')[6] # качество предмета
            item_data['stickers_id'] = row[0].split(';')[9] # ID стикеров для поиска названий стикеров на предмете по их ID 
            item_data['name'] = row[0].split(';')[10] # название предмета
            item_data['url'] = f"https://market.csgo.com/item/{item_data['c_classid']}-{item_data['c_instanceid']}" # на всякий ссылка на предмет
            
            market_items.append(item_data)

    return market_items

def main():
    if not login.login_to_steam():
        return False
        
    update_market_items()
    update_stickers()

    user_stickers_names = ['Наклейка: Vox Eminor | Катовице 2014', 'iBUYPOWER | Катовице 2014', 'Team Liquid | Колумбус 2016', 'Flipsid3 Tactics (голографическая) | Атланта 2017']
    user_stickers_ids = get_user_stickers_ids(user_stickers_names)
    print(user_stickers_ids)

    market_items = get_market_items()
    print(market_items[5000]) # просто для примера

if __name__ == '__main__':
    main()