import requests
import re
from collections import Counter
from functools import reduce
import matplotlib.pyplot as plt
from multiprocessing import Pool

# Завантаження тексту за URL


def download_text(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Не вдалося завантажити текст з {url}")

# Очищення тексту: видалення непотрібних символів


def clean_text(text: str):
    text = text.lower()  # Перетворюємо на нижній регістр
    # Видаляємо все, що не є літерою чи цифрою
    text = re.sub(r'[^a-zа-яё0-9\s]', '', text)
    return text

# Map: розбиття на слова та підрахунок їх частоти


def map_words(text: str):
    words = text.split()
    return Counter(words)

# Reduce: об'єднання результатів підрахунку з усіх частин


def reduce_word_counts(counter1, counter2):
    return counter1 + counter2

# Візуалізація топ слів


def visualize_top_words(word_counts):
    top_words = word_counts.most_common(10)
    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 5))
    plt.bar(words, counts)
    plt.xlabel('Слова')
    plt.ylabel('Частота')
    plt.title('Топ 10 найпоширеніших слів')
    plt.xticks(rotation=45)
    plt.show()

# Основна функція для обробки


def main():
    url = 'https://example.com'  # Замініть на вашу URL-адресу
    text = download_text(url)
    cleaned_text = clean_text(text)

    # Використовуємо багатопоточність для аналізу
    num_chunks = 4  # Кількість частин для поділу тексту
    chunk_size = len(cleaned_text) // num_chunks
    chunks = [cleaned_text[i:i + chunk_size]
              for i in range(0, len(cleaned_text), chunk_size)]

    # Використовуємо multiprocessing Pool для паралельної обробки
    with Pool() as pool:
        word_counts_list = pool.map(map_words, chunks)

    # Зводимо всі підрахунки в один
    total_word_counts = reduce(reduce_word_counts, word_counts_list)

    # Візуалізуємо результати
    visualize_top_words(total_word_counts)


if __name__ == "__main__":
    main()
