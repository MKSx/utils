import requests, argparse, sys
from hashlib import md5
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'DES-CBC3-SHA'

#https://stackoverflow.com/a/41041028/13886183
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    pass




def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-u','--url', help='Get url hash', type=str, required=True)
    argparser.add_argument('--timeout', help='Timeout request', type=int, default=10)
    argparser.add_argument('--proxy', help='Using proxy', type=str)

    if len(sys.argv) < 2:
        return argparser.print_help()

    args = argparser.parse_args(sys.argv[1:])

    proxy = {
        'http': f'http://{args.proxy}',
        'https': f'https://{args.proxy}'
    } if args.proxy else None
    try:
        res = requests.get(args.url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, timeout=args.timeout, verify=False, allow_redirects=False, proxies=proxy)

        print('Hash: %s' % md5(res.content).hexdigest())
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
