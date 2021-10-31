import imaplib
import email
from email.header import decode_header
from email.parser import BytesParser, Parser
from email.policy import default
import asyncio
import os
from typing import Generator, BinaryIO


class MailBox():
    """Connect mailbox, get mail and return mail list"""

    HOST: str = ''
    PORT: int = 0
    LOGIN: str = ''
    PASSWORD: str = ''
    COUNT_MAIL: int = 3
    FOLDER: str = 'Inbox'

    def __init__(self, obj=None, **kwargs) -> None:
        self.last_id = 0
        self.mail = None

    def _connect(self) -> None:
        '''
        Connection to the IMAP server
        '''
        try:
            self.mail = imaplib.IMAP4_SSL(host = self.HOST, port=self.PORT)
            self.mail.login(self.LOGIN, self.PASSWORD)
            self.mail.list()
        except:
            raise ConnectionRefusedError('Not connected')

    def _disconnect(self) -> None:
        '''
        Close the connection to the IMAP server
        '''
        self.mail.close()
        self.mail.logout()

    def _connect_server(fn):
        '''
        Decorator conect and desconect to the IMAP server
        '''
        def magic( self, *args, **kwargs) :
            self._connect()
            return fn( self,*args, **kwargs )
            self._disconnect()
        return magic

    def pagination(self, page: int=0, list_ids:list = []) -> list:
        '''
        Return ids mail to slice
        '''
        count_ids = len(list_ids)
        if page == 0:
            return [count_ids-self.COUNT_MAIL, None]
        count = count_ids-self.COUNT_MAIL*page
        if count < 0:
            count = 0
        len_page = self.COUNT_MAIL*(page-1)
        if len_page > count_ids:
            len_page = count_ids - self.COUNT_MAIL
        return [count, -len_page]

    def _selectFolder(self, folder:str = 'inbox') -> None:
        '''
        Selected folder to the IMAP server
        '''
        result, data = self.mail.select(folder)
        
        if result == 'NO':
            self.mail.logout()
            raise ValueError('Folder not find in mailbox.')

    @staticmethod
    def __decoder(string: str) -> str:
        
        string_bytes, encoding = decode_header(string)[0]
        if isinstance(string_bytes, bytes):
            # if it's a bytes, decode to str
            print('-----', string_bytes.decode(encoding))
            return string_bytes.decode(encoding)
    
    @_connect_server
    def getMailList(self, folder: str = 'inbox') -> list:
        '''
        Selected folder to the IMAP server
        '''
        self._selectFolder(folder)
        result, data = self.mail.uid('search', None, "ALL") #(UNSEEN)
        
        if result == 'OK':
            ids = data[0]
            return ids.split()

    @_connect_server
    def getMailSubject(self, folder: str = 'inbox', page: int = 0) -> Generator[int, str, str]:
        '''
        Get subject in mails to the IMAP server
        '''
        
        ids = self.getMailList(folder)
        page, end = self.pagination(page, ids)
        list_id = ids[page:end]
        mail_list = {}

        for i in list_id:
            if self.last_id < int(i):
                result, data = self.mail.uid('fetch', i, "(RFC822)")
                raw_email = data[0][1]

                try:
                    raw_email_string = raw_email.decode('utf-8')
                except UnicodeDecodeError as e:
                    raw_email_string = raw_email.decode('latin-1')

                email_message = email.message_from_string(raw_email_string)
                headers = Parser(policy=default).parsestr(raw_email_string)
                yield {'uid': i, 'subject': headers['Subject'], 'from': headers['From']}
        
        
    @_connect_server
    def getMail(self, ids, folder: str = 'inbox') -> dict:
        '''
        Get body in mail to the IMAP server
        '''        
        self._selectFolder(folder)
        result, data = self.mail.uid('fetch', ids, "(RFC822)")
        if isinstance(data[0], tuple):
            raw_email = data[0][1]

            msg = email.message_from_bytes(raw_email)

            subject = self.__decoder(msg.get("Subject"))

            from_name = self.__decoder(msg.get("From"))

            mail_obj = {'Subject:': subject, 'From:': from_name, 'file_name': []}

            for payload in msg.walk():
                content_type = payload.get_content_type()
                content_disposition = str(payload.get("Content-Disposition"))
                if "attachment" in content_disposition:
                    mail_obj['file_name'].append(payload.get_filename())
                if content_type == 'text/html':
                    mail_obj['text_html'] = payload.get_payload(decode=True).decode()
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    mail_obj['text_plane'] = payload.get_payload(decode=True).decode()
            
            return mail_obj

    @_connect_server
    def uploadFile(self, ids, file_name: str, folder: str = 'inbox') -> None: #BinaryIO
        '''
        Downloads file from the IMAP server.
        '''
        self._selectFolder(folder)
        result, data = self.mail.uid('fetch', ids, "(RFC822)")
        if isinstance(data[0], tuple):
            raw_email = data[0][1]

            msg = email.message_from_bytes(raw_email)

            for payload in msg.walk():
                if payload.get_filename() == file_name:
                    with open(file_name, "wb") as file:
                        file.write(payload.get_payload(decode=True))

class MailBoxBase(MailBox):
    HOST = os.environ.get('MAILBOX_TEST_HOST')
    PORT = os.environ.get('MAILBOX_TEST_PORT')
    LOGIN = os.environ.get('MAILBOX_TEST_LOGIN')
    PASSWORD = os.environ.get('MAILBOX_TEST_PASSWORD')
    COUNT_MAIL = 3
    FOLDER = 'Sent'

class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)

class MailIdsListView(MailBoxBase):
    
    def as_view(self):
        return self.getMailList(self.FOLDER)

    def __call__(self, *args, **kwargs):
        print('ok')
        return self.getMailSubject(self.FOLDER)

class MailSubjectListView(MailBoxBase):

    def as_view(self):
        return self.getMailSubject(self.FOLDER)

class getMailDetailView(MailBoxBase):

    def __init__(self, **kwargs):
        self.ids = kwargs.get('ids')

    def as_view(self):
        return self.getMail(self.ids, self.FOLDER) 

class TestClass(object):
    """docstring for TestClass"""
    def __init__(self, arg):
        self.arg = arg

    def sendJson(self):
        pass
        

p = MailIdsListView().as_view()
print("p", p)
