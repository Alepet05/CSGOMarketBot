from bs4 import BeautifulSoup
import query


def get_api_key():
    """Возвращает сгенерированный api-ключ аккаунта

    Returns:
        api_key (str): api-ключ
    """
    # к этому моменту мы уже создали ключ, так что считываем его
    with open('api_key.txt', 'r', encoding='utf-8') as f:
        api_key = f.read()

    return api_key

def save_api_key(api_key: str):
    """Сохраняет api-ключ в файл

    Args:
        api_key (str): api-ключ
    """
    with open('api_key.txt', 'w', encoding='utf-8') as f:
        f.write(api_key)

def create_api_key():
    """Создает личный api-ключ, который будет привязан к вашему аккаунту

    Returns:
        api_key (str): личный api-ключ
    """
    url = 'https://market.csgo.com/docs'
    action, csrf_token = get_payload() # получаем данные, необходимые для отправки post-запроса на сервер

    html = query.get_content(url, flag='key', action=action, csrf_token=csrf_token) # отправляем post-запрос для создания api-ключа на странице  
    soup = BeautifulSoup(html, 'lxml') # объект супа
    
    api_key = soup.find('div', class_='cat-descr').find('p', class_='col0').get_text(strip=True) # ищем сам ключ
    save_api_key(api_key)

def get_payload():
    """Возвращает данные, необходимые для отправки post-запроса на сервер для получения api-ключа: action и csrf-токен

    Returns:
        action, csrf_token (tuple): кортеж, хранящий action и csrf-токен
    """
    url = 'https://market.csgo.com/docs'
    html = query.get_content(url, flag='html') # get-запрос
    soup = BeautifulSoup(html, 'lxml') # объект супа

    # из спрятанных input'ов достаем action и csrf-токен 
    action = soup.find('input', attrs={'type': 'hidden', 'name':'action'}).get('value')
    csrf_token = soup.find('input', attrs={'type': 'hidden', 'name':'_csrf'}).get('value')

    return action, csrf_token