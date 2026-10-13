"""Разбор books.csv в функциональном стиле: только map, filter и lambda, без циклов."""
import csv
from itertools import islice


def get_books(path):
    """Задание 1: [['isbn', 'title', 'author', quantity, price], ...]"""
    with open(path, encoding='utf-8', newline='') as f:
        rows = islice(csv.reader(f, delimiter='|'), 1, None)  # пропускаем заголовок
        return list(map(lambda r: [r[0], r[1], r[2], int(r[3]), float(r[4])], rows))


def filtered_books(books, substring):
    """Задание 2: книги с подстрокой в названии (без учёта регистра),
    title и author склеены в один элемент."""
    return list(map(
        lambda b: [b[0], f'{b[1]}, {b[2]}', b[3], b[4]],
        filter(lambda b: substring.lower() in b[1].lower(), books),
    ))


def total_cost(books):
    """Задание 3: [('isbn', quantity * price), ...]"""
    return list(map(lambda b: (b[0], round(b[-2] * b[-1], 2)), books))


if __name__ == '__main__':
    from pathlib import Path
    from pprint import pprint

    books = get_books(Path(__file__).with_name('books.csv'))
    pprint(books)
    python_books = filtered_books(books, 'python')
    pprint(python_books)
    pprint(total_cost(python_books))
