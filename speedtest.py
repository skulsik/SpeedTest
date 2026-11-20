#!/usr/bin/env python3
"""
Консольная утилита для измерения скорости скачивания данных по HTTP/HTTPS.
"""

import argparse
import sys
import time

from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


# Количество последовательных запросов
REQUEST_COUNT = 10

# Размер блока при чтении ответа — 64 КБ
CHUNK_SIZE = 64 * 1024

# Максимальное время ожидания ответа от сервера
TIMEOUT_SECONDS = 30


def validate_url(url: str) -> None:
    """Проверяет корректность URL и поддерживаемую схему подключения."""

    parsed_url = urlsplit(url)

    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        raise ValueError(
            "Некорректный URL. Используйте адрес с http:// или https://"
        )


def download_once(url: str) -> tuple[int, float]:
    """
    Выполняет один запрос и полностью скачивает ответ.

    Возвращает:
        Количество скачанных байтов и время выполнения запроса в секундах.
    """

    # Формируем HTTP-запрос с указанием User-Agent
    request = Request(
        url,
        headers={"User-Agent": "simple-speedtest/1.0"}
    )

    byte_count = 0

    # Начинаем измерение времени
    started_at = time.perf_counter()

    # Открываем соединение и читаем ответ до конца
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        while True:
            chunk = response.read(CHUNK_SIZE)

            # Пустой блок означает, что данные закончились
            if not chunk:
                break

            byte_count += len(chunk)

    # Вычисляем продолжительность запроса
    elapsed_seconds = time.perf_counter() - started_at

    return byte_count, elapsed_seconds


def main() -> int:
    """Основная функция программы."""

    # Настраиваем обработку аргументов командной строки
    parser = argparse.ArgumentParser(
        description="Измерение скорости скачивания данных по HTTP/HTTPS."
    )

    parser.add_argument(
        "url",
        help="Адрес файла или ресурса для скачивания"
    )

    args = parser.parse_args()

    try:
        # Проверяем переданный адрес
        validate_url(args.url)

        total_bytes = 0
        total_seconds = 0.0

        print(f"Начинаем измерение скорости: {args.url}\n")

        # Выполняем запросы последовательно
        for number in range(1, REQUEST_COUNT + 1):
            byte_count, elapsed_seconds = download_once(args.url)

            total_bytes += byte_count
            total_seconds += elapsed_seconds

            print(
                f"Запрос {number}/{REQUEST_COUNT}: "
                f"{byte_count:,} байт за {elapsed_seconds:.3f} с"
            )

        # Рассчитываем среднее время одного запроса
        average_seconds = total_seconds / REQUEST_COUNT

        # Рассчитываем среднюю скорость скачивания в MB/s
        download_speed = total_bytes / total_seconds / 1_000_000

        # Выводим итоговую статистику
        print("\n--- Результаты измерения ---")
        print(f"Выполнено запросов: {REQUEST_COUNT}")
        print(f"Общий объём скачанных данных: {total_bytes:,} байт")
        print(f"Общий объём: {total_bytes / 1_000_000:.3f} MB")
        print(f"Среднее время запроса: {average_seconds:.3f} с")
        print(f"Средняя скорость скачивания: {download_speed:.3f} MB/s")

        return 0

    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        print(f"\nОшибка: {error}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nИзмерение прервано пользователем.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
