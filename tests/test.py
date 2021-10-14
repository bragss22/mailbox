import unittest
import os

from mailbox import MailBox, getMailBox

class TestMailBox(unittest.TestCase):
    def setUp(self):
        class testGetMailBox(MailBox):
            HOST = os.environ.get('MAILBOX_TEST_HOST')
            PORT = os.environ.get('MAILBOX_TEST_PORT')
            LOGIN = os.environ.get('MAILBOX_TEST_LOGIN')
            PASSWORD = os.environ.get('MAILBOX_TEST_PASSWORD')
            COUNT_MAIL: int = 3

        self.mailbox = testGetMailBox()

    def test_getMailList(self):
        self.assertIsInstance(self.mailbox.getMailList(), list, 'is list')
        self.assertIsNone(self.mailbox.getMailList(folder='NoFolder'))

        
        

    def test_getMailSubject(self):
        self.assertIsInstance(self.mailbox.getMailSubject(), dict, 'is dict')
  

if __name__ == '__main__':
    unittest.main()