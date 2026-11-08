"""
All your implementation code for the bank system simulation goes here.
"""

from collections import defaultdict
import math


def cashbacks_check(func):
    def wrapper(self, timestamp, *args):
        self.trans_manager.apply_cashbacks(timestamp)
        return func(self, timestamp, *args)
    return wrapper


class CashbackStatment:
    def __init__(self, timestamp, amount, ticket, account):
        self.timestamp = timestamp
        self.amount = amount
        self.status = "IN_PROGRESS"
        self.ticket = ticket
        self.account = account

class AccountTransactionManager():        
    def __init__(self):
        self.outgoing_transactions = defaultdict(int)
        self.cashback_statements = []

    def deposit(self, acc, amount_deposited):
        return acc.deposit(amount_deposited)

    def withdraw(self, acc, amount_withdrawn):
        result = acc.withdraw(amount_withdrawn)

        if result:
            self.outgoing_transactions[acc.account_id] += amount_withdrawn

        return result

    def get_top_x_spenders(self, n):
        spenders_list = list(self.outgoing_transactions.items())
        spenders_list = list((spend, acc_id) for (acc_id, spend) in spenders_list)
        spenders_list.sort(key = lambda x: (-x[0], x[1]))
        print(spenders_list)
        spenders_list = [f"{acc}({amount})" for (amount, acc) in spenders_list]
        return spenders_list[:n]

    def apply_cashbacks(self, timestamp):
        for cbs in self.cashback_statements:
            if cbs.status == "IN_PROGRESS" and timestamp >= cbs.timestamp:
                cbs.status = "CASHBACK_RECEIVED"
                cbs.account.deposit(cbs.amount)

    def add_cashback_statement(self, cs):
        self.cashback_statements.append(cs)



class Account: 
    def __init__(self, account_id):
        self.account_id = account_id
        self.money = 0

    def deposit(self, amount_deposited):
        self.money += amount_deposited
        return self.money

    def withdraw(self, amount_withdrawn):
        if self.money >= amount_withdrawn:
            self.money -= amount_withdrawn
            return self.money
        return None

    def get_money(self):
        return self.money

class AccountRepository:

    def __init__(self):
        self.internal_collection = {}

    def get_account_by_id(self, account_id):
        return self.internal_collection.get(account_id)

    def add_new_account(self, acc):
        self.internal_collection[acc.account_id] = acc


class Simulation:

    def __init__(self):
        self.account_repo = AccountRepository()
        self.trans_manager = AccountTransactionManager()
        

    def create_account(self, timestamp: int, account_id: str) -> bool | None:
        if not self.account_repo.get_account_by_id(account_id):
            new_account = Account(account_id)
            self.account_repo.add_new_account(new_account)
            return True
        return False

    @cashbacks_check
    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        target_account = self.account_repo.get_account_by_id(account_id)

        if target_account:
            self.trans_manager.deposit(target_account,amount)
            return target_account.get_money()
        else:
            return target_account
        
    @cashbacks_check
    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        source_account = self.account_repo.get_account_by_id(source_account_id)
        target_account = self.account_repo.get_account_by_id(target_account_id)

        if not source_account or not target_account:
            return None

        if source_account_id == target_account_id:
            return None

        if not self.trans_manager.withdraw(source_account, amount):
            return None

        self.trans_manager.deposit(target_account, amount)

        return source_account.get_money()

    @cashbacks_check
    def top_spenders(self, timestamp: int, n: int) -> list[str] | None:
        return self.trans_manager.get_top_x_spenders(n)

    @cashbacks_check
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        account = self.account_repo.get_account_by_id(account_id)

        if not account:
            return None
        if not self.trans_manager.withdraw(account, amount):
            return None

        process_time = 86400000
        cashback_amt = math.floor(amount * 0.02)



        ticket = f"payment{len(self.trans_manager.cashback_statements) + 1}"

        new_cashback_statement = CashbackStatment(process_time, cashback_amt, ticket, account)

        self.trans_manager.add_cashback_statement(new_cashback_statement)

        return ticket

    @cashbacks_check
    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        if not self.account_repo.get_account_by_id(account_id):
            return None

        for cbs in self.trans_manager.cashback_statements:
            if cbs.ticket == payment:
                if cbs.account.account_id == account_id:
                    return cbs.status
                else:
                    return None

        return None

    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool | None:
        pass

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        pass
