import requests
import login


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
        # если передали флаг json, то ожидаем получить ответ сервера в json формате
        elif kwargs['flag'] == 'json':
            # если передали параметр req, то ожидаем получить float
            if 'req' in kwargs:
                data = {'req': kwargs['req']} # передаем хэш предмета для запроса float
                response = requests.post(url, data=data) # api требует отправить post-запрос с хэшем
            else:
                response = requests.get(url)
            return response.json()
        # если передали флаг html, то ожижаем получить html страницу, соответственно отправляем заголовки
        elif kwargs['flag'] == 'html':
            response = requests.get(url, headers=headers)
            return response.content
    # если не было передано ни одного ключевого параметра, то ожидаем получить название файла базы данных, возвращаем текст ответа
    else:
        response = requests.get(url)
        return response.text