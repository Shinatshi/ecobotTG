import requests

url = "https://tass.ru/ekologiya"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
print(response.text)  # Выводим HTML страницы
