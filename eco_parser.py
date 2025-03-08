from bs4 import BeautifulSoup
import requests
import random
import time

RIA_URL = "https://ria.ru/ecology/"

def get_random_eco_news():
    try:
        response = requests.get(RIA_URL)
        time.sleep(2)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при получении новостей: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("a", class_="list-item__title color-font-hover-only")

    news_list = []
    for article in articles[:10]:
        title = article.text.strip()
        link = article["href"]
        news_list.append({"title": title, "link": link})

    return random.choice(news_list) if news_list else None
