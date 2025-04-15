import json

import requests

data = {
    'APIKey': 'b3116332c2596701ef69',
    'loc_id': 718,
    'limit': 100,
    'offset': 0

}

def events_load():
    js_data = True
    res_data = []
    with open('package.json', 'a', encoding='utf-8') as f:
        f.seek(0)
        f.truncate(0)
        while js_data:
            js_data = requests.post("https://api.afisha7.ru/v1.0/events/", data=data).json()['events']
            if not js_data:
                break
            res_data.extend(js_data)
            data['offset'] += 100
            print(js_data)
        json.dump(res_data, f, ensure_ascii=False)


def json_to_table():
    # Загрузка данных из файла JSON (замените название файла на реальное)
    with open('package.json', encoding='utf-8') as file:
        data = json.load(file)
        print(data)

    # Вставка всех данных из JSON в таблицу SQLite
    for item in data:
        ('''
        INSERT INTO events (id, idfull, pref, cat_id, cat_url, loc_id, name, date_start, date_end, logo, logo_p, anons, is_free, min_price, max_price, age, vip, places)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(item['id']),
            item['idfull'],  # idfull содержит цифры и текст, оставим только цифры
            item['pref'],
            int(item['cat_id']),
            item['cat_url'],
            int(item['loc_id']),
            item['name'],
            int(item['date_start']),
            int(item['date_end']),
            item['logo'],
            item['logo_p'],
            item['anons'] if item['anons'] else "",  # если null, то пустая строка
            int(item['is_free']),
            int(item['min_price']) if item['min_price'] else 0,
            int(item['max_price']) if item['max_price'] else 0,
            item['age'],
            int(item['vip']),
            json.dumps(item['places'], ensure_ascii=False)  # сериализация списка в JSON строку
        ))

    # Сохранение и закрытие данных
    conn.commit()
    conn.close()

    print("Все данные успешно добавлены в базу данных.")