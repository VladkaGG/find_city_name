

import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from threading import Thread
languages = ["ro", "tr", "fr", "it", "es", "en"]  # список переводимых языков.


def get_word(city: str, err_file, languag) -> str:
    try:
        response = requests.get('https://ru.wikipedia.org/wiki/{}'.format(city))
        bs = BeautifulSoup(response.content)
        grandparent_elem = bs.find('nav', attrs={'aria-labelledby': 'p-lang-label', 'id': 'p-lang'})  # ищем нужный nav
        parent_elem = grandparent_elem.find('ul', attrs={'class': 'vector-menu-content-list'})  # ищем нужный ul
        for elem in parent_elem:  # спускаемся в li
            for child in elem:  # спускаемся в a
                if child.attrs.get('lang') == languag:
                    try:
                        response = requests.get(child.attrs.get('href'))
                        result = BeautifulSoup(response.content).find('h1', attrs={'id': 'firstHeading'}).text
                        return result
                    except BaseException as err:
                        print('Проблемы с запросом {}! - {}'.format(child.attrs.get('href'), err))
                        err_file.write(city)
                        return city
        else:
            print('Возможно есть что-то еще с таким {} названием. Попытка запроса _(город)...'.format(city))
            response = requests.get('https://ru.wikipedia.org/wiki/{}_(город)'.format(city))
            bs = BeautifulSoup(response.content)
            grandparent_elem = bs.find('nav',
                                       attrs={'aria-labelledby': 'p-lang-label', 'id': 'p-lang'})  # ищем нужный nav
            parent_elem = grandparent_elem.find('ul', attrs={'class': 'vector-menu-content-list'})  # ищем нужный ul
            for elem in parent_elem:  # спускаемся в li
                for child in elem:  # спускаемся в a
                    if child.attrs.get('lang') == languag:
                        try:
                            response = requests.get(child.attrs.get('href'))
                            result = BeautifulSoup(response.content).find('h1', attrs={'id': 'firstHeading'}).text
                            return result
                        except BaseException as err:
                            print('Проблемы с запросом {}! - {}'.format(child.attrs.get('href'), err))
                            err_file.write(city)
                            return city
            else:
                print('Для города {} нет языка {}'.format(city, languag))
                err_file.write('{}\n'.format(city))
                return city
    except BaseException as er:
        print('Ошибка! - {}'.format(er))
        raise er


def set_last_id(lan, _id):
    """ Для случаев остановки запись последнего id в файл папки с переводом. """
    with open(f'{lan}/last_id.txt', 'w') as fi:
        fi.write(str(_id))
    return _id


def run(language):
    lst_id = 0
    with open('Ru_1.json', 'rb') as file:  # Получение первоначальных данных
        data = json.loads(file.read())
    try:
        with open(f'{language}/last_id.txt', 'r') as f:  # Получение последнего id
            last_id = int(f.read())
    except BaseException:
        last_id = 0
    with open(f'{language}/errors.txt', 'a') as error_file:
        for country in data['countrys']:
            if country.get('id') < last_id:
                continue
            try:
                country['cities'] = [get_word(x, error_file, language) if x else ''
                                     for x in country['cities']] if country.get('cities') else []
            except BaseException:
                lst_id = set_last_id(language, country['id'])
                break
    try:
        try:
            with open(f'{language}/{language}.json', 'rb') as f:
                last_data = json.loads(f.read())
                for old_elem, new_elem in zip(last_data['countrys'], data['countrys']):
                    if last_id <= old_elem['id'] < lst_id:
                        old_elem['cities'] = new_elem['cities']
                data = last_data
        except BaseException:
            print('Нет старых файлов, все ок по сути')
        with open(f'{language}/{language}.json', 'w') as f:
            f.write(json.dumps(data))
    except BaseException as e:
        print('Ты durakk? - {}'.format(e))
        pprint(data)


if __name__ == '__main__':
    for lang in languages:
        Thread(target=run, args=(lang,)).start()
