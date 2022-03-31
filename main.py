import requests
import login
import api_key_generator

def get_content(url: str, **kwargs):
    """Возвращает содержимое ответа сервера

    Args:
        url (str): url-адрес
    Returns:
        str or dict: ответ сервера
    """
    cookies = login.get_cookies()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.66',
        'cookie': cookies
    }
    if kwargs:
        # если передали флаг key, то ожидаем получить api_key аккаунта через post-запрос
        if kwargs['flag'] == 'key':
            payload = {
                'action': kwargs['action'],
                '_csrf': kwargs['csrf_token']
            }
            response = requests.post(url, data=payload, headers=headers) # post-запрос для генерации токена
            return response.content
        # если передали флаг json, то ожидаем получить информацию о текущем имени файла базы данных
        elif kwargs['flag'] == 'json':
            response = requests.get(url) # get запрос на сервер
            return response.json()
        # если передали флаг html, то ожижаем получить html страницу, соответственно отправляем заголовки
        elif kwargs['flag'] == 'html':
            response = requests.get(url, headers=headers)
            return response.content
    # если не было передано ни одного ключевого параметра, то ожидаем получить название файла базы данных, возвращаем текст ответа
    else:
        response = requests.get(url)
        return response.text
        
def get_market_items_db(current_db_file_name: str):
    """Возвращает базу данных всех вещей на продаже в фиксированный момент времени

    Args:
        current_db_file_name (str): имя файла базы данных, формат csv

    Returns:
        market_items_db (str): CSV-файл с данными в формате строки
    """
    db_file_url = f'https://market.csgo.com/itemdb/{current_db_file_name}' # url-адрес файла базы данных
    market_items_db = get_content(db_file_url) # получаем базу данных вещей
    return market_items_db 

def get_current_db_file_name():
    """Возвращает текущее имя файла базы данных

    Returns:
        current_db_file_name (str): имя файла базы данных, формат csv
    """
    url = 'https://market.csgo.com/itemdb/current_730.json' # адрес имени файла базы данных
    current_db_file_name = get_content(url, flag='json')['db'] # получение имени БД
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

def main():
    if not login.login_to_steam():
        return False
    print(api_key_generator.get_api_key())
if __name__ == '__main__':
    main()