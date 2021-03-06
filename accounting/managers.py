from django.conf import settings
from django.core import exceptions
import re
from swingtix.bookkeeper import models


class BookManager():

    def __init__(self):
        self.book_names = settings.ACCOUNTING_BOOKS

    def get_book(self, currency='USD'):
        if currency not in self.book_names:
            raise Exception(u"no book for currency '{0}'".format(currency))
        try:
            self.book = models.BookSet.objects.get(
                description=self.book_names[currency])
        except exceptions.ObjectDoesNotExist:
            self.book = models.BookSet(description=self.book_names[currency])
            self.book.save()
        return self.book


class AccountManager():

    def name_is_valid(self, account_name):
        if re.match(
                "(" + ")|(".join(settings.ACCOUNTING_VALID_ACCOUNTS) + ")",
                account_name):
            return True
        return False

    def format_user_account(self, user):
        return settings.ACCOUNTING_USER_ACCOUNT_FORMAT["format"].format(user)

    def is_credit_positive(self, account_name):
        if account_name in settings.ACCOUNTING_CREDIT_NEGATIVE_ACCOUNTS:
            return False
        return True

    def create_account(self, account_name):
        account = models.Account(
            bookset=BookManager().get_book(),
            name=account_name,
            positive_credit=self.is_credit_positive(account_name))
        account.save()
        return account

    def has_sufficient_balance(self, account):
        if self.get_user_account(
                account).balance() < settings.MINIMUM_BALANCE:
            return False
        return True

    def is_asset_source(self, account):
        if account in settings.ACCOUNTING_ASSET_SOURCES:
            return True
        return False

    def get_account(self, account_name):
        if not self.name_is_valid(account_name):
            raise Exception(u"account name '{0}' is not valid"
                            .format(account_name))
        try:
            return BookManager().get_book().get_account(account_name)
        except exceptions.ObjectDoesNotExist:
            return self.create_account(account_name)

    def get_user_account(self, user):
        return self.get_account(self.format_user_account(user))

    def get_revenue_account(self):
        return self.get_account(settings.ACCOUNTING_REVENUE_ACCOUNT)

    def get_promotions_account(self):
        return self.get_account(settings.ACCOUNTING_PROMOTIONS_ACCOUNT)
