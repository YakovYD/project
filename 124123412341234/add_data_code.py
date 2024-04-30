import requests

calls_data = [
    {
        "datetime": "9999-09-30 20:00",
        "phonea": "+11101222567",
        "phoneb": "+00007222321",
        "direction": "in",
        "billsec": 300,
        "linkedid": "1055550003.100005"
    },
]

response = requests.post("http://127.0.0.1:5000/add_data",
                         json=calls_data)

if response.status_code == 200:
    print("Данные успешно отправлены")
else:
    print("Ошибка при отправке данных:", response.status_code)
