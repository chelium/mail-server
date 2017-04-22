import unittest
from mailroom.session import *

TEST_IP = "127.0.0.1"

class TestMailSession(unittest.TestCase):

    def test_hello(self):
        s = MailSession(TEST_IP)
        self.assertEqual(s.process_line("HELO"), "200 HELO {}(TCP)\n".format(TEST_IP))
        
    def test_mail_from(self):
        s = MailSession(TEST_IP)
        s.process_line("HELO")
        self.assertEqual(s.process_line("MAIL FROM john@john.com"), "200 OK")

    def test_mail_to(self):
        s = MailSession(TEST_IP)
        s.process_line("HELO")
        s.process_line("MAIL FROM john@doe.com")
        self.assertEqual(s.process_line("RCPT TO joan@joan.com"), "200 OK")

if __name__ == "__main__":
    unittest.main()
