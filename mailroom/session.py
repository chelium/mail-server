class MailSession(object):
    def __init__(self, address):
        self.msg = ""
        self.state = START
        self.addr = address

    def process_cmd(self, cmd, data):
        if cmd == "HELO":
            if self.state == START:
                response = "200 HELO {}(TCP)\n".format(self.addr)
                self.state = WAITING_FROM
            else:
                response = "503 {} already received".format(cmd)
        elif self.state == START:
            response = "503 No HELO\n".format(cmd)
            self.state = TERMINATE
        elif cmd == "QUIT":
            response = "200 BYE {}(TCP)\n".format(self.addr)
            self.state = TERMINATE
        elif cmd == "MAIL FROM":
            response = "200 OK"
            if self.state == WAITING_FROM:
                self.msg += "From: <{}>".format(data)
                self.state = WAITING_TO
            elif self.state == WAITING_TO:
                self.msg += ", <{}>".format(data)
            else:
                response = "503 {} after RCPT TO\n".format(cmd)
        elif cmd == "RCPT TO":
            if self.state == WAITING_TO:
                self.msg += "To: <{}>".format(data)
                self.state = READY
            elif self.state > WAITING_TO:
                response = "503 {} already received\n".format(cmd)
            else:
                response = "503 {} before MAIL FROM\n".format(cmd)
        elif cmd == "DATA":
            if self.state == WAITING_DATA:
                response = "200 OK"
                self.state = RECEIVING
        else:
            response = "500 {} not recognized\n".format(cmd)
        return self.state, response
