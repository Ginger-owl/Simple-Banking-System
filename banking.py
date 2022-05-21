import random
import sqlite3


class BankingSystem:
    def __init__(self):
        self.card_data = None
        self.database()

    def base_menu(self) -> None:
        """Base loop for imitate main menu, takes user choice if known makes  appropriate action"""
        while True:
            print("1. Create an account\n2. Log into account\n0. Exit")
            user_choice: str = input()
            if user_choice == '0':
                print('Bye!')
                exit()
            elif user_choice == '1':
                self.create_account()
            elif user_choice == '2':
                self.log_into_account()
            else:
                print('Unknown option!\n Type 1, 2 or 0.')

    @staticmethod
    def database(card=None, pin=None, balance=None) -> None:
        """Creates a table if it is not exist and no args provided, with arguments inserts new values in the table"""
        with sqlite3.connect('card.s3db') as data:
            cur = data.cursor()
            if not card:
                cur.execute('''
                CREATE TABLE IF NOT EXISTS card (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                number TEXT NOT NULL UNIQUE,
                pin TEXT NOT NULL,
                balance INTEGER DEFAULT 0 NOT NULL
                );
                ''')
            else:
                cur.execute('''
                INSERT OR IGNORE INTO card (number, pin, balance)
                VALUES (?, ?, ?)
                ''', (card, pin, balance))

    @staticmethod
    def check_credentials(card) -> tuple:
        """"Returns designated values from the table as a tuple, using card(card_number) as the key"""
        with sqlite3.connect('card.s3db') as db:
            cur = db.cursor()
            cur.execute('''
            SELECT number, pin, balance FROM card WHERE number LIKE (?);
            ''', (card,))
            return cur.fetchone()

    @staticmethod
    def generate_account() -> tuple:
        """Generates card-number, pseudo-random, valid(Luhn) and not present in db"""
        while True:
            card_num = ''.join([str(n) for n in str(4000000000000000 + random.randrange(0, 9999999999, 1))])
            pin = ''.join([str(n) for n in random.sample(range(9), 4)])
            if not BankingSystem.check_credentials(card_num):
                if BankingSystem.luhn_validator(card_num):
                    yield card_num, pin
            else:
                continue

    def create_account(self) -> None:
        """Creates an account for user, registers card number and pin-code in db"""
        card, pin = next(self.generate_account())
        self.database(card, pin, 0)
        print("Your card has been created")
        print(f"Your card number:\n{card}")
        print(f"Your card PIN:\n{pin}")

    def log_into_account(self) -> None:
        """Prompts for card number nad pin, validates, if successful opens inner menu"""
        card: str = input("Enter your card number:\n")
        pin: str = input("Enter your PIN:\n")
        try:
            self.card_data = self.check_credentials(card)
            if self.card_data[1] == pin:
                print("You have successfully logged in!\n")
                self.account_menu()
            else:
                print("Wrong card number or PIN!\n")
        except (KeyError, TypeError):
            print("Wrong card number or PIN!\n")

    @staticmethod
    def exists(card: str) -> bool:
        """Checks whether acoount exists in the table, return True if so"""
        with sqlite3.connect('card.s3db') as db:
            cur = db.cursor()
            cur.execute('SELECT number FROM card WHERE number = (?)', (card,))
            return bool(cur.fetchone())

    @staticmethod
    def update_balance(amount: int, card: str) -> None:
        """Updates data about balance for designated (by card number) card"""
        with sqlite3.connect('card.s3db') as db:
            cur = db.cursor()
            cur.execute(f'''
                    UPDATE card 
                    SET balance = balance + {amount}
                    WHERE number = {card}
            ''')
            db.commit()

    @staticmethod
    def delete_account(card: str) -> None:
        """Deletes all the data direectly related to designated card"""
        with sqlite3.connect('card.s3db') as db:
            cur = db.cursor()
            cur.execute(f'''
                    DELETE FROM card 
                    WHERE number = {card}
            ''')
            db.commit()

    def transfer_money(self, card_from: str, card_to: str, amount: int) -> None:
        """Updates balance data for sender and receiver cards on the specified amount""" 
        with sqlite3.connect('card.s3db') as db:
            cur = db.cursor()
            cur.execute(f"""
                        UPDATE card
                        SET balance = balance - {amount}
                        WHERE number = {card_from}
            """)
            db.commit()
            cur.execute(f"""
                        UPDATE card
                        SET balance = balance + {amount}
                        WHERE number = {card_to}
            """)
            db.commit()
            print("Money has been successfully transferred!")

    def transfer_menu(self, card_from: str, card_to: str) -> None:
        """Menu for transferring money, checks whether it is possible to make transfer""""
        if card_to == card_from:
            print("You can't transfer money to the same account!")
            return
        elif not self.luhn_validator(card_to):
            print("Probably you made a mistake in the card number. Please try again!")
            return
        elif not self.exists(card_to):
            print("Such a card does not exist.")
            return
        else:
            amount = int(input("Enter how much money you want to transfer:\n"))
            if amount > self.card_data[2]:
                print("Not enough money!")
                return
            else:
                self.transfer_money(card_from, card_to, amount)

    @staticmethod
    def luhn_validator(card_number: str) -> bool:
        """Validates card number by using Luhn algorithm, returns True if card is valid"""
        number = [int(i) for i in card_number]
        for index, digit in enumerate(number):
            if (index + 1) % 2 == 0:
                continue
            dgt = digit * 2
            number[index] = dgt if dgt < 10 else dgt - 9
        return sum(number) % 10 == 0

    def account_menu(self) -> None:
        """Loop for Inner menu takes user choice(input) if known makes appropriate action"""
        while True:
            self.card_data = self.check_credentials(self.card_data[0])
            print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
            user_choice = input()
            if user_choice == '1':  # Balance
                print(f"\nBalance: {self.card_data[2]}\n")
            elif user_choice == '2':  # Add Income
                income = int(input("\nEnter income:\n"))
                self.update_balance(income, self.card_data[0])
                print("Income was added!")
            elif user_choice == '3':  # Do transfer
                print("Transfer")
                receiver_card = input("Enter card number:\n")
                self.transfer_menu(self.card_data[0], receiver_card)
            elif user_choice == '4':  # Close account
                self.delete_account(self.card_data[0])
                print("The account has been closed!\n")
            elif user_choice == '5':  # Log out
                self.card_data = None
                print("You have successfully logged out!")
                return
            elif user_choice == '0':  # Exit
                print('Bye!')
                exit()
            else:
                print('Unknown command!\n Type 1, 2 or 0.')


if __name__ == "__main__":
    bank = BankingSystem()
    bank.base_menu()

