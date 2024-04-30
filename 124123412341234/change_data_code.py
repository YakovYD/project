import requests

url = 'http://127.0.0.1:5000//change_data'

user_data = {
    'id': 2,
    'name': 'ССС',
    'phone': '9999'
}

response = requests.post(url, json=user_data)

if response.status_code == 200:
    print('Пользователь успешно добавлен или изменен.')
else:
    print('Ошибка при добавлении или изменении пользователя:',
          response.text)
