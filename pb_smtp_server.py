import asyncore
import os
import re
import requests
from datetime import datetime
from smtpd import SMTPServer

class PBReceiver(SMTPServer):
    no = 0

    def retrieved_paste(self, url):
        raw_url = "https://pastebin.com/raw{}".format(url[url.rindex('/'):])
        print("paste retrival for {} in progress..".format(raw_url))
        r = requests.get(raw_url, verify=False)
        if r.ok:
            return r.text
        return None

    def process_message(self, peer, mailfrom, rcpttos, data):
        # yes i know.. will validate spf later.
        if "admin@pastebin.com" not in mailfrom: 
            return 
        print("processing message...")
        dt = datetime.now().strftime('%Y%m%d%H%M%S')
        keyword = re.compile("(?<=')[^']+(?=')")
        pburl = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

        try:
            kw = keyword.findall(data)[0]
            u = pburl.findall(data)[0]
            email_filename = "{}-{}-{}.eml".format(kw, dt, self.no)
            with open(email_filename, 'w') as f:
                f.write(data)
                f.close

                paste_content = self.retrieved_paste(u)
                if paste_content:
                    print("logged keyword {} at {}, pulled from {}, email " \
                            "saved as {}, paste saved as {}!".format(
                                kw, dt, u, email_filename, email_filename+"-paste"))
                    with open(email_filename+'-paste', 'a') as f:
                        f.write(paste_content)
                        f.close()

                    self.no += 1
        except Exception as e:
            print(e)

def run():
    foo = PBReceiver(('127.0.0.1', 2225), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run()
