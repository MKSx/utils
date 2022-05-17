import smtplib, argparse, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-u','--username', help='SMTP username', type=str, required=True)
    argparser.add_argument('-p','--password', help='SMTP passsword', type=str, required=True)
    argparser.add_argument('-H','--host', help='SMTP hostname', type=str, required=True)
    argparser.add_argument('-P','--port', help='SMTP port', type=str, default=587)
    argparser.add_argument('--subject', help='Email subject', type=str, default='Test smtp')
    argparser.add_argument('--sender', help='Email sender', type=str, required=True)
    argparser.add_argument('--to', help='Email to', type=str, required=True)
    argparser.add_argument('--body', help='Email body', type=str, default='Hello world!')

    if len(sys.argv) < 2:
        return argparser.print_help()

    try:
        args = argparser.parse_args(sys.argv[1:])


        msg = MIMEMultipart()

        msg['From'] = args.sender
        msg['To'] = args.to
        msg['Subject'] = args.subject
        msg.attach(MIMEText(args.body, 'plain'))

        server = smtplib.SMTP(args.host, args.port)

        server.set_debuglevel(0)

        server.starttls()
        server.login(args.username, args.password)

        server.sendmail(args.sender, args.to, msg.as_string())

        server.quit()
        print('Email enviado!')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
