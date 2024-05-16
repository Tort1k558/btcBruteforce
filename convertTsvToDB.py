import csv
import sqlite3

# Путь к вашему tsv файлу
tsv_file = 'dbAB.tsv'

# Путь к базе данных SQLite
db_file = 'dbAB.db'


# Функция для создания базы данных SQLite и таблицы
def create_database():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS balances (
                        address TEXT PRIMARY KEY,
                        balance FLOAT
                    )''')
    conn.commit()
    conn.close()


# Функция для вставки данных из TSV-файла в базу данных SQLite
def insert_data():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    with open(tsv_file, 'r') as file:
        tsv_reader = csv.reader(file, delimiter='\t')
        data_to_insert = []
        total_rows = sum(1 for _ in tsv_reader)
        file.seek(0)

        for i, row in enumerate(tsv_reader, 1):
            address, balance = row
            data_to_insert.append((address, float(balance) / 10 ** 8))
            progress = i / total_rows * 100
            print(f'{progress:.1f}% готово', end='\r')

        cursor.executemany('''INSERT OR IGNORE INTO balances (address, balance) VALUES (?, ?)''', data_to_insert)
        conn.commit()
        conn.close()
    print('100% готово')


# Создание базы данных и таблицы
create_database()

# Вставка данных из TSV-файла
insert_data()

print("Данные успешно добавлены в базу данных SQLite.")
