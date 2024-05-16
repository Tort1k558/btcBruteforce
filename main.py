import sqlite3
import time

from mnemonic import Mnemonic
from colorama import Fore, Back, init
from multiprocessing import Process, Queue, Lock, Value

from bip_utils import Bip39SeedGenerator, Bip44, Bip84, Bip49, Bip84Coins, Bip44Coins, Bip49Coins, Bip44Changes

num_processes = 4
wallet_per_commit = 150


def check_balance(address, cursor):
    try:
        cursor.execute('''SELECT balance FROM balances WHERE address = ?''', (address,))
        result = cursor.fetchone()
        if result is not None and result[0] > 0.0:
            return result[0]
        else:
            return 0.0
    except Exception as e:
        print("Ошибка при выполнении запроса:", e)
        return 0.0


def bip44(mnemonic_words, cursor):
    seed_bytes = Bip39SeedGenerator(mnemonic_words).Generate()

    bip44_wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_acc_ctx = bip44_wallet.Purpose().Coin().Account(0)
    bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)

    address = bip44_chg_ctx.AddressIndex(0).PublicKey().ToAddress()
    balance = check_balance(address, cursor)

    return address, balance


def bip49(mnemonic_words, cursor):
    seed_bytes = Bip39SeedGenerator(mnemonic_words).Generate()

    bip49_wallet = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
    bip49_acc_ctx = bip49_wallet.Purpose().Coin().Account(0)
    bip49_chg_ctx = bip49_acc_ctx.Change(Bip44Changes.CHAIN_EXT)

    address = bip49_chg_ctx.AddressIndex(0).PublicKey().ToAddress()
    balance = check_balance(address, cursor)

    return address, balance


def bip84(mnemonic_words, cursor):
    seed_bytes = Bip39SeedGenerator(mnemonic_words).Generate()

    bip84_wallet = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    bip84_acc_ctx = bip84_wallet.Purpose().Coin().Account(0)
    bip84_chg_ctx = bip84_acc_ctx.Change(Bip44Changes.CHAIN_EXT)

    address = bip84_chg_ctx.AddressIndex(0).PublicKey().ToAddress()
    balance = check_balance(address, cursor)

    return address, balance


def worker(q, lock, processed_wallets):
    """
    conn_wallets = sqlite3.connect('wallets.db', timeout=30)
    cursor_wallets = conn_wallets.cursor()
    """

    conn_balance = sqlite3.connect('btc.db', timeout=30)
    cursor_balance = conn_balance.cursor()

    insert_count = 0
    insert_values = []
    while True:
        seed_phrase = q.get()

        for bip_method in [(bip44, "BIP44"), (bip49, "BIP49"), (bip84, "BIP84")]:
            address, balance = bip_method[0](seed_phrase, cursor_balance)

            """
            try:
                insert_values.append((address, seed_id, balance))
                insert_count += 1

                if insert_count >= wallet_per_commit:
                    try:
                        cursor_wallets.executemany(
                            "INSERT INTO btc (address, seed_id, balance) VALUES (?, ?, ?)",
                            insert_values)
                        conn_wallets.commit()
                        insert_values = []
                        insert_count = 0
                    except Exception as e:
                        print(e)
             except Exception as e:
                print(e)
            """

            if balance > 0.000000000001:
                with lock:
                    with open("goods.txt", "a") as goods_file:
                        goods_file.write(
                            f"Address ({bip_method[1]}): {address} | Seed Phrase: {seed_phrase} | BTC: {balance}\n")
                print(
                    f"{Back.YELLOW}{Fore.WHITE} Address ({bip_method[1]}): {Fore.CYAN}{address} {Fore.GREEN}| {Fore.RED}BTC: {balance}")
            else:
                pass
                # print(f"{Fore.WHITE} Address ({bip_method[1]}): {Fore.CYAN}{address} {Fore.GREEN} | {Fore.RED}BTC: {balance}")

        with processed_wallets.get_lock():
            processed_wallets.value += 3


def print_processed_wallets(processed_wallets):
    while True:
        time.sleep(1)
        with processed_wallets.get_lock():
            print(f"{processed_wallets.value} wallet/sec")
            processed_wallets.value = 0


def start():
    q = Queue()
    lock = Lock()
    processed_wallets = Value('i', 0)

    """
    conn_wallets = sqlite3.connect('wallets.db')
    cursor_wallets = conn_wallets.cursor()

    create_table_query = '''
        CREATE TABLE IF NOT EXISTS btc (
            address TEXT PRIMARY KEY,
            seed_id INTEGER,
            balance REAL,
            FOREIGN KEY (seed_id) REFERENCES seeds(seed_id)
        );

        CREATE TABLE IF NOT EXISTS seeds (
            seed_id INTEGER PRIMARY KEY AUTOINCREMENT,
            seed_phrase TEXT UNIQUE
        );

        CREATE INDEX IF NOT EXISTS idx_seed_phrase ON seeds (seed_phrase);
    '''

    cursor_wallets.executescript(create_table_query)

    conn_wallets.commit()
    """

    processes = []
    for _ in range(num_processes):
        p = Process(target=worker, args=(q, lock, processed_wallets))
        p.start()
        processes.append(p)

    p = Process(target=print_processed_wallets, args=(processed_wallets,))
    p.start()
    processes.append(p)

    while True:
        if q.qsize() < 50000:
            try:
                seed_phrase = Mnemonic("english").generate(128)
                """
                cursor_wallets.execute("SELECT seed_phrase FROM seeds WHERE seed_phrase = ?", (seed_phrase,))
                result = cursor_wallets.fetchone()
                if result is None:
                """
                q.put(seed_phrase)

            except Exception as e:
                print(e)
                

if __name__ == "__main__":
    init()
    start()
