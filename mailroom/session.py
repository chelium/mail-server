CMD_LIST = ["HELO", "MAIL FROM", "RCPT TO", "DATA", "QUIT"]
# States
START = 0
AUTH_START = 1
AUTH_FIRST = 2
AUTH_WAIT = 3
WAITING_FROM = 4
WAITING_RCPT = 5
WAITING_DATA = 6
RECEIVING = 7
SAVING = 8
TERMINATE = 9

class MailSession(object):
    def __init__(self, address):
        self.msg = ""
        self.state = START
        self.addr = address
        self.passkeys = {}
        self.user = ""
        self.target = ""
    
    def parse_passkeys(file_data):
        lines = file_data.split("\n")
        for line in lines:
            pair = line.split(",")
            if len(pair) == 2:
                self.passkeys[pair[0]] = pair[1]
    
    def process_cmd(self, line):
        response = "200 OK\n"
        if MailSession.compare_cmd("HELO", line):
            if self.state == START:
                response = "200 HELO {}(TCP)\n".format(self.addr)
                self.state = WAITING_FROM
            else:
                response = "503 HELO already received\n"
        elif self.state == START:
            response = "503 No HELO\n"
            self.state = TERMINATE
        elif MailSession.compare_cmd("AUTH", line):
            response = "334 dXN1cm5hbWU6\n"
            self.state = AUTH_START
        elif MailSession.compare_cmd("QUIT", line):
            response = "200 BYE {}(TCP)\n".format(self.addr)
            self.state = TERMINATE
        elif MailSession.compare_cmd("MAIL FROM", line):
            data = line[9:].strip()
            if self.state == WAITING_FROM:
                self.msg += "From: <{}>".format(data)
                self.state = WAITING_RCPT
            elif self.state == WAITING_RCPT:
                self.msg += ", <{}>".format(data)
            else:
                response = "503 MAIL FROM after RCPT TO\n"
        elif MailSession.compare_cmd("RCPT TO", line):
            if self.state == WAITING_RCPT:
                data = line[7:].strip()
                self.msg += "\nTo: <{}>\n".format(data)
                self.target = data
                self.state = WAITING_DATA
            elif self.state > WAITING_RCPT:
                response = "503 RCPT TO already received\n"
            else:
                response = "503 RCPT TO before MAIL FROM\n"
        elif MailSession.compare_cmd("DATA", line):
            if self.state == WAITING_DATA:
                self.state = RECEIVING
            else:
                response = "503 DATA before RCPT TO\n"
        else:
            response = "500 command not recognized\n"
        return response

    def process_line(self, line):
        if self.state == AUTH_START:
            email = line.strip()
            if True: # Check if email is valid
                self.user = email
                if email in self.passkeys.keys():
                    self.state = AUTH_WAIT
                    return "334 cGFzc3dvcmQ6"
                else:
                    self.state = AUTH_FIRST
                    new_pass = self.generate_pass()
                    self.passkeys[self.user] = MailSession.encode(new_pass)
                    return "330 {}".format(new_pass)
            else:
                # Invalid email return error
                return "Invalid email"
        elif self.state = AUTH_WAIT:
            passkey = line.strip()
            try:
                if MailSession.encode(int(passkey)) == self.passkeys[self.user]:
                    return "Auth success"
            except ValueError:
                return "Auth failed"
            return "Auth failed"
        elif self.state == RECEIVING:
            self.msg += line
            if line == ".":
                self.state = SAVING
                return "200 OK\n"
            return "200 OK\n"
        else:
            return self.process_cmd(line)
    

    @staticmethod
    def compare_cmd(cmd, line):
        if len(line) < len(cmd):
            return False
        return cmd == line[:len(cmd)]

    @staticmethod
    def is_valid_email(email):
        if email.count('@') != 1:
            return False
        parts = email.split('@')
        if not parts[0] or not parts[1]:
            return False
        
