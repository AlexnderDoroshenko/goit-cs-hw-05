import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import asyncio

# Тут імпортуємо функції з основного коду
from file_sort_async import read_folder, copy_file


class TestAsyncFileSorter(unittest.TestCase):
    @patch('shutil.copy')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.rglob')
    async def test_read_folder(self, mock_rglob, mock_mkdir, mock_copy):
        """
        Тестуємо асинхронне зчитування папки та копіювання файлів
        з відповідними перевірками колбеків.
        """
        # Моки
        mock_rglob.return_value = [
            Path('test_folder/file1.txt'),
            Path('test_folder/file2.png')
        ]
        mock_copy.return_value = None
        mock_mkdir.return_value = None

        # Колбеки
        # Завжди дозволяємо копіювати
        before_callback = MagicMock(return_value=True)
        after_callback = MagicMock()

        source_folder = Path('test_folder')
        output_folder = Path('output_folder')

        # Викликаємо асинхронну функцію
        await read_folder(
            source_folder,
            output_folder,
            before_callback,
            after_callback
        )

        # Перевірка, чи був викликаний mock_copy для двох файлів
        self.assertEqual(mock_copy.call_count, 2)

        # Перевірка, чи був викликаний колбек перед копіюванням
        before_callback.assert_called()

        # Перевірка, чи був викликаний колбек після копіювання
        after_callback.assert_called()

    @patch('shutil.copy')
    @patch('pathlib.Path.mkdir')
    async def test_before_copy_callback_invalid_extension(
            self, mock_mkdir, mock_copy):
        """
        Тестуємо випадок, коли колбек перед копіюванням 
        повертає False для файлів з неприпустимим розширенням.
        """
        mock_copy.return_value = None
        mock_mkdir.return_value = None

        # Файл не проходить валідацію
        before_callback = MagicMock(return_value=False)
        after_callback = MagicMock()

        file_path = Path('test_folder/file_invalid.xyz')
        output_folder = Path('output_folder')

        # Перевірка, що файл не буде скопійований
        await copy_file(
            file_path, output_folder, before_callback, after_callback)

        mock_copy.assert_not_called()  # Файл не був скопійований
        before_callback.assert_called_once()
        # Колбек перед копіюванням був викликаний
        after_callback.assert_not_called()
        # Колбек після копіювання не був викликаний

    @patch('shutil.copy')
    @patch('pathlib.Path.mkdir')
    async def test_valid_file_copy(self, mock_mkdir, mock_copy):
        """
        Тестуємо випадок, коли файл із допустимим розширенням 
        копіюється в цільову папку.
        """
        mock_copy.return_value = None
        mock_mkdir.return_value = None

        # Завжди дозволяємо копіювати
        before_callback = MagicMock(return_value=True)
        after_callback = MagicMock()

        file_path = Path('test_folder/file_valid.txt')
        output_folder = Path('output_folder')

        # Викликаємо копіювання
        await copy_file(
            file_path, output_folder, before_callback, after_callback)

        # Перевірка, що файл скопійовано
        mock_copy.assert_called_once_with(file_path, output_folder / 'txt')
        before_callback.assert_called_once()
        # Колбек перед копіюванням був викликаний
        after_callback.assert_called_once()
        # Колбек після копіювання був викликаний

    @patch('shutil.copy')
    @patch('pathlib.Path.mkdir')
    async def test_skip_file_with_no_extension(self, mock_mkdir, mock_copy):
        """
        Тестуємо випадок, коли файл без розширення не копіюється.
        """
        mock_copy.return_value = None
        mock_mkdir.return_value = None

        # Завжди дозволяємо копіювати
        before_callback = MagicMock(return_value=True)
        after_callback = MagicMock()

        file_path = Path('test_folder/file_without_extension')
        output_folder = Path('output_folder')

        # Викликаємо копіювання
        await copy_file(
            file_path, output_folder, before_callback, after_callback)

        # Перевірка, що файл не був скопійований,
        #  оскільки він не має розширення.
        mock_copy.assert_not_called()
        before_callback.assert_called_once()
        after_callback.assert_not_called()


if __name__ == "__main__":
    # Запуск тестів асинхронно
    asyncio.run(unittest.main())
