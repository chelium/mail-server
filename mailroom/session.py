CMD_LIST = ["HELO", "MAIL FROM", "RCPT TO", "DATA", "QUIT"]
# States
START = 0
WAITING_FROM = 1
WAITING_RCPT = 2
WAITING_DATA = 3
RECEIVING = 4
TERMINATE = 5
SAVING = 6

class MailSession(object):
    def __init__(self, address):
        self.msg = ""
        self.state = START
        self.addr = address
        self.target = ""
    
    def process_cmd(self, line):
        if MailSession.compare_cmd("HELO", line):
            if self.state == START:
                response = "200 HELO {}(TCP)\n".format(self.addr)
                self.state = WAITING_FROM
            else:
                response = "503 HELO already received\n"
        elif self.state == START:
            response = "503 No HELO\n"
            self.state = TERMINATE
        elif MailSession.compare_cmd("QUIT", line):
            response = "200 BYE {}(TCP)\n".format(self.addr)
            self.state = TERMINATE
        elif MailSession.compare_cmd("MAIL FROM", line):
            response = "200 OK"
            data = line[9:].strip()
            if self.state == WAITING_FROM:
                self.msg += "From: <{}>".format(data)
                self.state = WAITING_RCPT
            elif self.state == WAITING_RCPT:
                self.msg += ", <{}>".format(data)
            else:
                response = "503 MAIL FROM after RCPT TO\n"
        elif MailSession.compare_cmd("RCPT TO", line):
            response = "200 OK"
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
                response = "200 OK"
                self.state = RECEIVING
            else:
                response = "503 DATA before RCPT TO\n"
        else:
            response = "500 command not recognized\n"
        return response

    def process_line(self, line):
        if self.state == RECEIVING:
            self.msg += line
            print(line)
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


if __name__ == "__main__":
    session = MailSession("195.0.2.1")
    res = session.process_line("HELO")
    print(res)
    res = session.process_line("MAIL FROM john@john.com")
    print(res)
    res = session.process_line("MAIL FROM jake@jake.com")
    print(res)
    res = session.process_line("RCPT TO josh@josh.com")
    print(res)
    res = session.process_line("DATA")
    print(res)
    res = session.process_line(raw_input())
    print(res)
    res = session.process_line(raw_input())
    print(res)
    print(session.msg)
