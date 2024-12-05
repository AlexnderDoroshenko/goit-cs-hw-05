import shutil
import asyncio
import logging
from pathlib import Path
from argparse import ArgumentParser

# Налаштування логування
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Асинхронна функція для копіювання файлів


async def copy_file(file_path: Path, output_folder: Path,
                    before_copy_callback=None, after_copy_callback=None):
    try:
        # Отримуємо розширення без крапки
        extension = file_path.suffix.lower()[1:]
        if not extension:
            return  # Пропускаємо файли без розширення

        # Якщо є колбек для перевірки перед копіюванням, викликаємо його
        if before_copy_callback:
            valid = await before_copy_callback(file_path)
            if not valid:
                logging.warning(
                    f"Файл {file_path} не пройшов валідацію перед копіюванням."
                )
                return

        # Створюємо підпапку для цього розширення, якщо вона ще не існує
        dest_folder = output_folder / extension
        dest_folder.mkdir(parents=True, exist_ok=True)

        # Копіюємо файл в потрібну папку
        shutil.copy(file_path, dest_folder)
        logging.info(f"Файл {file_path} успішно скопійовано в {dest_folder}")

        # Якщо є колбек для перевірки після копіювання, викликаємо його
        if after_copy_callback:
            await after_copy_callback(file_path, dest_folder)

    except Exception as e:
        logging.error(f"Помилка при копіюванні файлу {file_path}: {e}")

# Асинхронна функція для рекурсивного читання всіх файлів з папки


async def read_folder(
        source_folder: Path, output_folder: Path,
        before_copy_callback=None, after_copy_callback=None):
    try:
        # Проходимо по всіх файлах та підпапках в папці
        tasks = []
        for item in source_folder.rglob('*'):
            if item.is_file():
                tasks.append(
                    copy_file(
                        item, output_folder,
                        before_copy_callback, after_copy_callback))

        # Запускаємо всі асинхронні завдання
        await asyncio.gather(*tasks)

    except Exception as e:
        logging.error(f"Помилка при обробці папки {source_folder}: {e}")

# Колбек для перевірки файлів перед копіюванням
#  (наприклад, перевірка розширення)


async def before_copy_callback(file_path: Path):
    allowed_extensions = {'txt', 'pdf', 'png'}  # Потрібні розширення
    extension = file_path.suffix.lower()[1:]
    if extension not in allowed_extensions:
        logging.info(f"Файл {file_path} не підтримується для копіювання.")
        return False
    return True

# Колбек для перевірки після копіювання (наприклад, логування)


async def after_copy_callback(file_path: Path, dest_folder: Path):
    logging.info(
        f"Після копіювання: файл {file_path} знаходиться в {dest_folder}")

# Основна функція для обробки аргументів і запуску процесу


async def main():
    # Обробка аргументів командного рядка
    parser = ArgumentParser(description="Сортування файлів за розширенням")
    parser.add_argument('source', type=str, help="Шлях до вихідної папки")
    parser.add_argument('output', type=str, help="Шлях до папки призначення")
    args = parser.parse_args()

    source_folder = Path(args.source)
    output_folder = Path(args.output)

    if not source_folder.exists() or not source_folder.is_dir():
        logging.error(
            f"Вихідна папка {source_folder} не існує або не є директорією")
        return
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    # Запускаємо асинхронне читання та копіювання файлів
    await read_folder(
        source_folder, output_folder,
        before_copy_callback, after_copy_callback
    )

if __name__ == "__main__":
    asyncio.run(main())
