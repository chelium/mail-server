import os


class MailRoom(object):
    def __init__(self, path):
        self.path = path
        MailRoom.check_dir(path)
    
    def read_pass(self):
        passkey_file = "{}.user_pass".format(self.path)
        if not os.path.exists(passkey_file):
            open(passkey_file, 'w')
        with open(passkey_file, 'r') as f:
            return f.read()

    def save_pass(self, username, passkey):
        passkey_file = "{}.user_pass".format(self.path)
        with open(passkey_file, 'a') as f:
            f.write("{},{}\n".format(username, passkey))

    def check_email(self, username):
        MailRoom.check_dir("{}{}/".format(self.path, username))
        i = 1
        while True:
            unused = self.get_email_path(username, i)
            if os.path.exists(unused):
                i += 1
            else:
                return unused

    def read_email(self, username, i):
        fname = get_email_path(username, i)
        with open(fname, 'r') as f:
            return f.read()
        
    def get_email_path(self, username, i):
        return "{}{}/{:0=3d}.email".format(self.path, username, i)

    def save_email(self, to_email, content):
        fname = self.check_email(MailRoom.get_username(to_email))
        with open(fname, 'w') as f:
            f.write(content)
    
    @staticmethod
    def check_dir(path):
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def get_username(email):
        return email.split("@")[0]

    @staticmethod
    def create_email(date_str, mail_from, mail_to, data):
        email_str = """Date: {}
From: <{}>
To: <{}>
{}""".format(date_str, mail_from, mail_to, data)
        
    @staticmethod
    def mail_from_list_to_str(mail_from):
        result = "<{}>".format(">, <".join(mail_from))
        print(result)


if __name__ == "__main__":
    mr = MailRoom("db/")
    mr.read_pass()
