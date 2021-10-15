import unittest
import os
import types

from mailbox import MailBox


class TestMailBox(unittest.TestCase):
    def setUp(self):
        class testGetMailBox(MailBox):
            HOST = os.environ.get('MAILBOX_TEST_HOST')
            PORT = os.environ.get('MAILBOX_TEST_PORT')
            LOGIN = os.environ.get('MAILBOX_TEST_LOGIN')
            PASSWORD = os.environ.get('MAILBOX_TEST_PASSWORD')
            COUNT_MAIL: int = 3

        self.mail = testGetMailBox()


    def test_getMailList(self):
        self.mail._connect()
        self.mail._selectFolder('inbox')
        self.assertIsInstance(self.mail.getMailList(), list, 'is list')
        self.assertRaises(ValueError, self.mail._selectFolder, 'NoFolder')

    def test_getMail(self):
        self.mail._connect()
        self.mail._selectFolder('inbox')
        ids = self.mail.getMailList()[0]
        self.assertIsInstance(self.mail.getMail(ids), dict, 'is dict')
        ids = b'565'
        self.assertIsInstance(self.mail.getMail(ids), dict, 'is dict')


    def test_getMailSubject(self):
        self.assertIsInstance(self.mail.getMailSubject(), types.GeneratorType, 'is generator')
  

if __name__ == '__main__':
    unittest.main()