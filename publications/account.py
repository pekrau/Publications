"Publications: Account and login pages."

from __future__ import print_function

import logging

import tornado.web

from . import constants
from . import settings
from . import utils
from .saver import Saver
from .requesthandler import RequestHandler

ADD_TEXT = """A new account %(email)s in the website %(site)s has been created.

To set the password, go to %(link)s and provide it.

Or, go to %(url)s and fill in the one-time code %(code)s manually and provide your password.

/The %(site)s administrator.
"""

RESET_TEXT = """The password for your account %(email)s in the website %(site)s has been reset.

To set a new password, go to %(link)s and provide your new password.

Or, go to %(url)s and fill in the one-time code %(code)s manually and provide your new password.

/The %(site)s administrator.
"""

class AccountSaver(Saver):
    doctype = constants.ACCOUNT

    def set_email(self, email):
        assert self.get('email') is None # Email must not have been set.
        email = email.strip().lower()
        if not email: raise ValueError('No email given.')
        if not constants.EMAIL_RX.match(email):
            raise ValueError('Malformed email value.')
        if len(list(self.db.view('account/email', key=email))) > 0:
            raise ValueError('Email is already in use.')
        self['email'] = email

    def erase_password(self):
        self['password'] = None

    def set_password(self, new):
        utils.check_password(new)
        self['code'] = None
        # Bypass ordinary 'set'; avoid logging password.
        self.doc['password'] = utils.hashed_password(new)
        self.changed['password'] = '******'

    def reset_password(self):
        "Invalidate any previous password and set activation code."
        self.erase_password()
        self['code'] = utils.get_iuid()


class AccountMixin(object):
    "Mixin with access check methods."

    def is_readable(self, account):
        "Is the account readable by the current user?"
        if self.is_owner(account): return True
        if self.is_admin(): return True
        return False

    def check_readable(self, account):
        "Check that the account is readable by the current user."
        if self.is_readable(account): return
        raise ValueError('You may not read the account.')

    def is_editable(self, account):
        "Is the account editable by the current user?"
        if self.is_owner(account): return True
        if self.is_admin(): return True
        return False

    def check_editable(self, account):
        "Check that the account is editable by the current user."
        if self.is_editable(account): return
        raise ValueError('You may not edit the account.')


class Account(AccountMixin, RequestHandler):
    "Account page."

    @tornado.web.authenticated
    def get(self, email):
        logging.debug(">>> Account")
        try:
            account = self.get_account(email)
            self.check_readable(account)
        except (KeyError, ValueError), msg:
            self.see_other('home', error=str(msg))
            return
        self.render('account.html', account=account)


class Accounts(RequestHandler):
    "List of accounts."

    @tornado.web.authenticated
    def get(self):
        self.check_admin()
        accounts = self.get_docs('account/email', key=None)
        self.render('accounts.html', accounts=accounts)


class AccountAdd(RequestHandler):
    "Account addition page."

    @tornado.web.authenticated
    def get(self):
        self.check_admin()
        self.render('account_add.html')

    @tornado.web.authenticated
    def post(self):
        self.check_admin()
        try:
            email = self.get_argument('account')
        except tornado.web.MissingArgumentError:
            self.see_other('account_add', error='No account email provided.')
            return
        try:
            account = self.get_account(email)
        except KeyError:
            pass
        else:
            self.see_other('account', account['email'],
                           error='Account already exists.')
            return
        role = self.get_argument('role', constants.CURATOR)
        if role not in constants.ROLES:
            role = constants.CURATOR
        try:
            with AccountSaver(rqh=self) as saver:
                saver.set_email(email)
                saver['owner'] = email
                saver['role'] = role
                saver.reset_password()
            account = saver.doc
        except ValueError, msg:
            self.see_other('account_add', error=str(msg))
            return
        data = dict(site=settings['SITE_NAME'],
                    email=account['email'],
                    code=account['code'],
                    url=self.absolute_reverse_url('account_password'),
                    link=self.absolute_reverse_url('account_password',
                                                   account=account['email'],
                                                   code=account['code']))
        server = utils.EmailServer()
        server.send(account['email'],
                    "A new account in the website %s" % settings['SITE_NAME'],
                    ADD_TEXT % data)
        self.see_other('account', email)


class AccountEdit(AccountMixin, RequestHandler):
    "Account edit page."

    @tornado.web.authenticated
    def get(self, email):
        try:
            account = self.get_account(email)
        except KeyError, msg:
            self.see_other('home', error=str(msg))
            return
        try:
            self.check_editable(account)
        except ValueError, msg:
            self.see_other('account', account['email'], error=str(msg))
            return
        self.render('account_edit.html', account=account)

    @tornado.web.authenticated
    def post(self, email):
        try:
            account = self.get_account(email)
        except KeyError, msg:
            self.see_other('home', error=str(msg))
            return
        try:
            self.check_editable(account)
        except ValueError, msg:
            self.see_other('account', account['email'], error=str(msg))
            return
        with AccountSaver(account, rqh=self) as saver:
            if self.is_admin():
                saver['role'] = self.get_argument('role', account['role'])
        self.see_other('account', account['email'])
        

class AccountReset(RequestHandler):
    "Reset the password of the account; send an email with the one-time code."

    def get(self):
        if self.current_user:
            email = self.current_user['email']
        else:
            email = None
        self.render('account_reset.html', email=email)

    def post(self):
        try:
            email = self.get_argument('account')
        except tornado.web.MissingArgumentError:
            self.see_other('home')
            return
        try:
            account = self.get_account(email)
        except KeyError:
            self.see_other('home')
            return
        with AccountSaver(account, rqh=self) as saver:
            saver.reset_password()
        data = dict(site=settings['SITE_NAME'],
                    email=account['email'],
                    code=account['code'],
                    url=self.absolute_reverse_url('account_password'),
                    link=self.absolute_reverse_url('account_password',
                                                   account=account['email'],
                                                   code=account['code']))
        server = utils.EmailServer()
        server.send(account['email'],
                    "Reset your password in website %s" % settings['SITE_NAME'],
                    RESET_TEXT % data)
        self.see_other('home')
        

class AccountPassword(RequestHandler):
    "Set the password of the account; requires a one-time code."

    def get(self):
        self.render('account_password.html',
                    email=self.get_argument('account', ''),
                    code=self.get_argument('code', ''))

    def post(self):
        try:
            email = self.get_argument('account')
            password = self.get_argument('password')
            code = self.get_argument('code')
            account = self.get_account(email)
            if code != account.get('code'): raise ValueError
            with AccountSaver(account, rqh=self) as saver:
                saver.set_password(password)
                # Login directly
                self.set_secure_cookie(constants.USER_COOKIE,
                                       account['email'],
                                       expires_days=settings['LOGIN_MAX_AGE_DAYS'])
                saver['login'] = utils.timestamp() # Set last login timestamp.
        except (tornado.web.MissingArgumentError, KeyError, ValueError):
            self.see_other('account_password',
                           error='Missing or wrong data in one or more fields.')
        else:
            self.see_other('account', account['email'])
