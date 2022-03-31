from selenium import webdriver
import time
import config
import json


def login_to_steam():
    """Аутентификация Steam

    Также получает cookies текущей сессии и сохраняет их в файл

    Returns:
        bool: статус выполнения функции. Если False - дальнейшая работа бота невозможна
    """
    # если адрес для входа в стим по каким то причинам поменялся, то раскомментить код
    # driver.get('https://market.csgo.com')
    # time.sleep(2)

    # login_url = driver.find_element_by_xpath("//div[@class='authblock']/a[@class='signin btn-signin']").get_attribute('href')
    # driver.get(login_url)
    # time.sleep(2)

    options = webdriver.ChromeOptions() # инициализируем опции
    options.add_argument('--headless') # аргумент для работы браузера в фоновом режиме
    driver = webdriver.Chrome(executable_path='chromedriver\\chromedriver.exe', options=options) # инициализируем объект драйвера

    driver.get('https://market.csgo.com/login') # сразу переходим на страницу входа
    time.sleep(2) # пауза для прогрузки страницы

    login_form = driver.find_element_by_xpath("//form[@id='loginForm']") # ищем форму с полями ввода данных

    username_input = login_form.find_element_by_name('username') # ищем поле для ввода имени пользователя
    username_input.send_keys(config.USERNAME) # отправляем указанное в конфиге имя пользователя

    password_input = login_form.find_element_by_name('password') # ищем поле для ввода пароля
    password_input.send_keys(config.PASSWORD) # отправляем указанный в конфиге пароль

    login_button = driver.find_element_by_id('login_btn_signin').find_element_by_tag_name('input') # ищем кнопку входа
    login_button.click() # нажимаем на нее
    time.sleep(2)

    # ищем окно с двухфакторной аутентификацией и пытаемся ввести код
    try:
        driver.find_element_by_class_name('newmodal') # всплывающее окно

        twofactor_code_input = driver.find_element_by_id('twofactorcode_entry') # ищем поле для ввода кода 2факторки
        twofactor_code_input.send_keys(config.TWOFACTOR_CODE) # отправляем код из конфига

        submit_button = driver.find_element_by_id('login_twofactorauth_buttonsets').find_element_by_class_name('auth_button') # подтверждение
        submit_button.click()
        time.sleep(2) # пауза для проверки кода на сервере
        # если код двухфакторной аутентификации не прошел, то, вероятнее всего, он устарел
        try:
            driver.find_element_by_class_name('auth_icon_lock')
            print('Ошибка входа: неверный код двухфакторной аутентификации')
            print('Убедитесь в актуальности кода двухфакторной аутентификации и обновите config.py')
            return False # возвращаем False, т.к. дальнейшая работа бота невозможна
        # в случае, если код корректный, выводим сообщение и продолжаем работу
        except:
            print('Код двухфакторной аутентификации успешно прошел проверку')
    # попадаем сюда, если у пользователя выключена двухфакторная аутентификация
    except:
        print('Было бы неплохо включить двухфакторную аутентификацию :D')

    time.sleep(10) # большая пауза для прогрузки главной страницы (редирект), и, соответственно, нужных куки, т.к. куки страницы входа стима нам не нужны
    
    # получаем и сохраням куки
    cookies = driver.get_cookies()
    save_cookies_to_file(cookies)

    # завершаем работу драйвера
    driver.close() # закрывает только одну вкладку
    driver.quit() # полностью выходит из браузера

    return True # если не был возвращен False, то продолжаем работу бота

def save_cookies_to_file(cookies: list):
    """Сохраняем cookies в файл

    Args:
        cookies (list): список словарей, хранящих cookie текущей сессии
    """
    # сохраняем куки в файл, удобнее всего в json
    with open('cookies.json', 'w', encoding='utf-8') as f:
        json.dump(cookies, f, indent=4, ensure_ascii=False)
    
def get_cookies():
    """Возвращает куки в отформатированном виде

    Returns:
        cookies (str): строка с отформатированными cookies
    """
    # считываем куки из файла
    with open('cookies.json', 'r', encoding='utf-8') as f:
        cookies = json.load(f)

    # приводим куки в нужный формат для их дальнейшей передачи в заголовках: _ym_uid=1642943714246294679; _ym_d=1642943714; и тд
    formatted_cookies = [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
    cookies = '; '.join(formatted_cookies)

    return cookies