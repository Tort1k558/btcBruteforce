# Bitcoin Wallet Brute Forcer

This Python program is designed to brute force Bitcoin wallets across three standards: BIP44, BIP49, and BIP84. It uses multiprocessing to generate seed phrases, derive Bitcoin addresses, and check their balances against a pre-populated database. If a balance is found, it logs the wallet details to a file.

For the program to work it needs a database with wallets that have at least one satoshi, this is all stored in btc.db

You can download this base here - https://mega.nz/file/puNmyJQJ#DYIpca88oXCqLDGYvF1pBPWP2-YBMpJPOWPpUOE2TPA

## Features

- **Multi-process Support**: Utilizes multiple processes to maximize performance and check wallets in parallel.
- **Three Bitcoin Standards**: Supports BIP44, BIP49, and BIP84 standards for address generation.
- **SQLite Database Integration**: Integrates with SQLite databases to store and retrieve address balances. You can remove the comments and add a little code to cache wallets that have already been processed
- **Mnemonic Seed Generation**: Uses BIP39 mnemonic phrases to generate wallet seeds.
- **Real-time Wallet Processing Rate**: Displays the number of wallets processed per second.

## Dependencies

- `mnemonic`
- `colorama`
- `bip-utils`


## Installation

To run this program, you'll need to install the required Python packages. You can do this using `pip`:

```sh
pip install mnemonic colorama bip-utils
