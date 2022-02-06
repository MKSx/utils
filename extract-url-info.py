import requests
import concurrent.futures
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
import json, argparse, sys, re

#https://stackoverflow.com/a/41041028/13886183
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    pass

REGEX_OPT = {
    'fortinet': re.compile(r'top.location=[\'|"](.*?)[\'|"]', re.IGNORECASE)
}

def get_redirect_http_meta(soup):
    result = soup.find("meta",attrs={"http-equiv":"refresh"})
    if result:
        key = None
        sl = []
        if 'content' in result:
            key = 'content'
        elif 'CONTENT' in result:
            key = 'CONTENT'
        
        if key != None:
            result[key] = result.lower().replace(' ', '')
            pos = result[key].find("url=")
            if pos > -1:
                return result[key][pos + 4:]
    return None





def get_redirect_http_fortinet(text):
    regex = re.search(REGEX_OPT['fortinet'], text)
    if regex:
        return regex[0].replace('top.location=', '').replace('"', '')
    return None

def get_url_info(url, timeout=10):
    ret = {
        'success': False,
        'error': None,
        'error_type': None,
        'status': 200,
        'redirect': False,
        'title': None,
        'url': url
    }
    try:
        
        res = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False)

        ret['success'] = True
        ret['status'] = res.status_code
        if 'Location' in res.headers:
            ret['redirect'] = res.headers['Location']
        elif 'location' in res.headers:
            ret['redirect'] = res.headers['location']
        
        soup = BeautifulSoup(res.text, 'html.parser')
        if soup.title:
            ret['title'] = soup.title.text.strip()

        
        content_length = int(res.headers.get('Content-Length', '0')) if 'Content-Length' in res.headers else len(res.text)
        
        
        #if ret['title'] == None or len(ret['title']) < 1 and content_length > 0:

        if content_length > 0:
            temp = get_redirect_http_meta(soup)
            if temp != None:
                ret['redirect'] = temp
                return ret
            temp = get_redirect_http_fortinet(res.text)
            if temp != None:
                ret['redirect'] = temp
                return ret
            
            
    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.Timeout, requests.exceptions.ConnectTimeout) as e:
        ret['error'] = str(e)
        ret['error_type'] = type(e).__name__

    return ret


def run(urls, workers=5, timeout=1, log=False):
    #with futures.ThreadPoolExecutor(max_workers=5)
    
    data = []
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for url in urls:
                futures.append(executor.submit(get_url_info, url=url, timeout=timeout))
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                data.append(res)
                if log:
                    print('URL: %s - Status: %d - Success: %s - Error: %s - Title: %s - Redirect: %s' % (
                        res['url'], res['status'], res['success'], res['error_type'], res['title'], res['redirect']
                    ))
    except KeyboardInterrupt:
        pass

    return data

def main():

    argparser = argparse.ArgumentParser()

    argparser.add_argument('-i','--input', help='File with url list', type=argparse.FileType('r'))
    argparser.add_argument('-o','--output', help='Output file', type=argparse.FileType('w'))
    argparser.add_argument('-l', '--log', help='Print url detail progress', action='store_true')
    argparser.add_argument('--timeout', help='Timeout request', type=int, default=10)
    argparser.add_argument('--workers', help='Workers', type=int, default=1)
    argparser.add_argument('--indent', help='Indent json output', type=int, default=0)
    argparser.add_argument('-u','--url', help='Get url info', type=str)

    if len(sys.argv) < 2:
        return argparser.print_help()

    args = argparser.parse_args(sys.argv[1:])

    if args.url:
        if len(args.url) < 10:
            return print('Invalid url')
        
        
        print(json.dumps(get_url_info(args.url), indent=args.indent))
        return
    if not args.input:
        return print('Escolha opção --url ou --input')

    url_list = []
    for url in args.input.readlines():
        url = url.strip()
        if len(url) > 10:
            url_list.append(url)

    if len(url_list) < 1:
        return print('URL list empty')
    
    workers = args.workers

    if workers < 1:
        workers = 1

    if workers > len(url_list):
        workers = len(url_list) if workers < 32 else 32

    timeout = None if args.timeout < 1 else args.timeout

    data = run(url_list, workers, timeout, args.log)
    if len(data) > 0:
        json.dump(data, args.output, indent=args.indent)
        print('Done :D')
    else:
        print("Returned empty")


if __name__ == '__main__':
    main()
