import unittest
from unittest.mock import patch
from words_count_map_reduce import (
    download_text, clean_text, map_words,
    reduce_word_counts, visualize_top_words, main
)
from collections import Counter


class TestWordFrequencyAnalysis(unittest.TestCase):

    @patch('requests.get')
    def test_download_text_success(self, mock_get):
        # Мокаємо успішний запит
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = \
            "This is a test text for the word frequency analysis test."

        url = 'https://example.com'
        result = download_text(url)

        self.assertEqual(
            result,
            "This is a test text for the word frequency analysis test."
        )
        mock_get.assert_called_once_with(url)

    @patch('requests.get')
    def test_download_text_failure(self, mock_get):
        # Мокаємо неуспішний запит
        mock_get.return_value.status_code = 404

        url = 'https://example.com'
        with self.assertRaises(Exception):
            download_text(url)

    def test_clean_text(self):
        # Тестуємо очищення тексту
        text = "Hello, world! This is a test."
        cleaned_text = clean_text(text)

        self.assertEqual(cleaned_text, "hello world this is a test")

    def test_map_words(self):
        # Тестуємо підрахунок слів
        text = "hello hello world test test test"
        word_count = map_words(text)

        expected_count = Counter({'test': 3, 'hello': 2, 'world': 1})
        self.assertEqual(word_count, expected_count)

    def test_reduce_word_counts(self):
        # Тестуємо злиття результатів підрахунку
        counter1 = Counter({'hello': 2, 'world': 1})
        counter2 = Counter({'test': 3, 'hello': 1})

        result = reduce_word_counts(counter1, counter2)
        expected = Counter({'hello': 3, 'test': 3, 'world': 1})

        self.assertEqual(result, expected)

    @patch('matplotlib.pyplot.show')
    def test_visualize_top_words(self, mock_show):
        # Тестуємо візуалізацію
        word_counts = Counter(
            {'hello': 3, 'test': 5, 'world': 2, 'analysis': 1})

        # Викликаємо візуалізацію
        visualize_top_words(word_counts)

        # Перевіряємо, чи була викликана функція для відображення графіка
        mock_show.assert_called_once()

    @patch('requests.get')
    @patch('matplotlib.pyplot.show')
    def test_main(self, mock_show, mock_get):
        # Мокаємо успішний запит
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = \
            "This is a simple text to test the analysis process."

        # Перевіряємо, що все працює як потрібно (всі функції виконуються)
        with patch('builtins.print'):
            main()

        # Перевіряємо, чи була викликана візуалізація
        mock_show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
