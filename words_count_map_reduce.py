import aiohttp
import asyncio
import re
from collections import Counter
from functools import reduce
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import logging
import argparse

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Асинхронне завантаження тексту
async def download_text(url: str) -> str:
    logging.info(f"Завантаження тексту з {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                logging.info(f"Успішно завантажено текст з {url}")
                return await response.text()
            else:
                logging.error(f"Не вдалося завантажити текст з {url} (Статус: {response.status})")
                return ""

# Очищення тексту: видалення непотрібних символів
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-zа-яё0-9\s]', '', text)
    return text

# Map: розбиття на слова та підрахунок їх частоти
def map_words(text: str) -> Counter:
    words = text.split()
    return Counter(words)

# Reduce: об'єднання результатів підрахунку з усіх частин
def reduce_word_counts(counter1, counter2) -> Counter:
    return counter1 + counter2

# Візуалізація топ слів
def visualize_top_words(word_counts: Counter, title: str):
    top_words = word_counts.most_common(10)
    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 5))
    plt.bar(words, counts)
    plt.xlabel('Слова')
    plt.ylabel('Частота')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.show()

# Обробка одного URL
async def process_url(url: str):
    text = await download_text(url)
    if not text:
        return Counter()

    cleaned_text = clean_text(text)

    # Поділ тексту на частини
    num_chunks = 4
    chunk_size = len(cleaned_text) // num_chunks
    chunks = [cleaned_text[i:i + chunk_size]
              for i in range(0, len(cleaned_text), chunk_size)]

    # Обробка тексту в потоках
    with ThreadPoolExecutor() as executor:
        word_counts_list = await asyncio.gather(
            *[asyncio.to_thread(map_words, chunk) for chunk in chunks]
        )

    # Зведення результатів
    total_word_counts = reduce(reduce_word_counts, word_counts_list)
    logging.info(f"Обробка {url} завершена")
    return total_word_counts

# Основна функція
async def main(urls):
    # Паралельна обробка кількох URL
    word_counts_list = await asyncio.gather(
        *[process_url(url) for url in urls]
    )

    # Зведення результатів усіх URL
    overall_word_counts = reduce(reduce_word_counts, word_counts_list)

    # Візуалізація загальних результатів
    visualize_top_words(overall_word_counts, "Топ 10 слів із всіх URL")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Аналіз текстів за URL-адресами")
    parser.add_argument(
        "urls", nargs="+", help="URL-адреси через пробіл для аналізу"
    )
    args = parser.parse_args()

    asyncio.run(main(args.urls))
