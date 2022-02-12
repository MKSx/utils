from operator import attrgetter
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'DES-CBC3-SHA'
import json, argparse, sys, re
from hashlib import md5

#https://stackoverflow.com/a/41041028/13886183
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    pass

REGEX_OPT = {
    'fortinet': re.compile(r'top.location=[\'|"](.*?)[\'|"]', re.IGNORECASE)
}

MD5_TABLE = {
    'ff21d4a95b17cc5b4433e58769970c35': {
        'redirect': '/ui/',
        'title': 'VMware ESXi'
    },
    '37c1af0cf3934d2cdf504c63b93b0aa1': {
        'redirect': '/flow/auth/signin',
        'title': 'Senha Segura'
    },
    'ad9c3139081bf8eb46ef9afd2135c43f': {
        'redirect': '/sanproject/',
        'title': 'Hitachi Device Manager - Storage Navigator'
    },
    '89147f12959645f37a6037a05f04caab': {
        'redirect': None,
        'title': 'VCenter - VMware vSphere 6'
    },
    '50a06705d03b18b41ae7eb8d7665a622': {
        'redirect': '/appliance',
        'title': 'Login- Symantec NetBackup Web Management Console',
    },
    '9118bbfeffeb607067f073b264173e83': {
        'redirect': None,
        'title': 'Welcome to VMware ESXi'
    },
    '6228ca7a50fcac3ecaafd21ddbae90bb': {
        'redirect': None,
        'title': 'Welcome to VMware ESXi - 5.5.0'
    },
    'fd969a4e519ec459445f7bf9885a3739': {
        'redirect': None,
        'title': 'Welcome to VMware ESXi - 5.5.0'
    },
    'd41d8cd98f00b204e9800998ecf8427e': {
        'redirect': '/dashboard',
        'title': 'Welcome to XAMPP'
    },
    'c07f661dad49ba32c8f5c9605148fb5f': {
        'redirect': '/restgui/start.html',
        'title': 'Login to iDRAC'
    },
    '4ada2be6f16e1623de939acae87ea6e7':{
        'redirect': '/webui',
        'title': 'Cisco'
    },
    '9934ed6eedb0d78ae2a873831013f8c7': {
        'redirect': None,
        'title': 'HP DesignJet'
    },
    '2d8c71ed8cbc5c464056ea4b95ce689d': {
        'redirect': None,
        'title': 'Welcome to VMware vSphere'
    },
    '14bacec89f8b6abeae1d9a0cebde763c': {
        'redirect': None,
        'title': 'iLO4 - HP ProLiant'
    },
    '138bd383afafea5b45aa59575a066d33': {
        'redirect': None,
        'title': 'HP - Storage Management Utility'
    },
    'f8ec0af2ad1d0debeb5f2554abcea124': {
        'redirect': None,
        'title': 'Welcome to VMware vSphere'
    },
    'b8e23f9f0f904b3d81ef2e13069bf2b3': {
        'redirect': None,
        'title': 'iLO4 - HP ProLiant'
    },
    'f9bb30bc910afb31ad5437b658131ad5': {
        'redirect': None,
        'title': 'OceanStor ISM'
    },
    '97022257c0e41813fc17b661c6f77e18': {
        'redirect': None,
        'title': 'Start EMC Unisphere'
    },
    'a1552483d401e40acda711025422a12d': {
        'redirect': None,
        'title': 'Start EMC Unisphere'
    },
    'e08598c479ca5f37d547b85bcace9435': {
        'redirect': '/index_en.cgi',
        'title': 'OceanStor ISM'
    },
    '35e978c461242f9c4807f13230ab403e': {
        'redirect': '/index_en.cgi',
        'title': 'OceanStor ISM'
    },
    'b815d4c0b7f9ee5966e3ac4d2f7823a3': {
        'redirect': None,
        'title': 'HP - Storage Management Utility'
    },
    '4bdea16a4f874b0e45965ed2f382aa84': {
        'redirect': None,
        'title': 'Welcome to VMware ESXi - 5.5.0'
    },
    '00322a3c86c11c9a6b7d47303c90ba4f': {
        'redirect': None,
        'title': 'HP Virtual Connect Manager'
    },
    '588ade7ae9e5ad8494daa6757955837d': {
        'redirect': None,
        'title': 'HP Virtual Connect Manager'
    },
    'f30839cac40540a6d293f296aace505e': {
        'redirect': None,
        'title': 'Supermicro - ATEN International'
    },
    'c7b4690c8c46625ef0f328cd7a24a0a3': {
        'redirect': None,
        'title': 'It works!'
    },
    '50431cd86161e83439439db658db492a': {
        'redirect': None,
        'title': 'Welcome to VMware ESXi - 6.0.0'
    },
    'b452f0a743b5b99f23a23fafc9f61d8b': {
        'redirect': None,
        'title': 'Welcome to VMware ESXi - 5.5.0'
    },
    '0bfcaf0405a62ce415306ad8172ce6be': {
        'redirect': '/rsm/',
        'title': 'RSM Login'
    },
    'bd395f9f00f07a196d27df38af7759b1': {
        'redirect': '/webacs/welcomeAction.do',
        'title': 'Cisco NCS'
    },
    '713a34a43bf27539050453c6a848c653': {
        'redirect': None,
        'title': 'Check flash:/http.zip , please'
    },
    '7162869e0efa332d103aea840cee19c1': {
        'redirect': None,
        'title': 'Management Controller'
    },
    '6a1da869b30c46118278450187274b41': {
        'redirect': None,
        'title': 'Jenkins'
    },
    'f67f7c219b0107103dfbbc219b691337': {
        'redirect': '/+CSCOE+/logon.html',
        'title': 'CISCO - SSL VPN Service'
    },
    'a9275c024d4df2fb042910f741506933': {
        'redirect': None,
        'title': 'iBMC'
    },
    'b4dbef2b5d64400882800c06bbba6748': {
        'redirect': '/dell_login.html',
        'title': 'Dell OpenManage Switch Administrator'
    }
}

def get_redirect_html1(text, length=0):
    if length < 500:
        text = text.lower().strip().replace(' ', '')
        temp = re.search(r'window.location=[\'|"](.*?)["|\']', text, re.IGNORECASE)
        if temp:
            return temp[1]
    
    return None

def get_redirect_http_meta(soup):
    result = soup.select('meta[http-equiv="refresh" i]')
    if result and len(result) > 0:
        result = result[0]
        key = None
        sl = []
        if 'content' in result.attrs:
            key = 'content'
        elif 'CONTENT' in result.attrs:
            key = 'CONTENT'
        
        if key != None:
            result[key] = result[key].lower().replace(' ', '')
            pos = result[key].find("url=")
            if pos > -1:
                return result[key][pos + 4:]
    return None

def check_md5(hs):
    if hash in MD5_TABLE:
        return MD5_TABLE[hs]

def get_meta_copyright(soup):
    
    result = soup.select('meta[name="copyright" i]')
    
    if result and len(result) > 0:
        result = result[0]
        key = None
        
        if 'content' in result.attrs:
            key = 'content'
        elif 'CONTENT' in result.attrs:
            key = 'CONTENT'

        if key != None:
            return result.get(key)

    return None


def check_rcats(text):
    if text.find('<rcats  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="rcats.xsd">') > 0:
        return 'RCATS Status'
    return None

def get_redirect_http_fortinet(text):
    regex = re.search(REGEX_OPT['fortinet'], text)
    if regex:
        return regex[0].replace('top.location=', '').replace('"', '')
    return None

def check_radcom(text):
    if text.find('/monserver/AjaxClient/JSP/Login/Login.jsp') > 0:
        return ['RADCOM', '/monserver/AjaxClient/JSP/Login/Login.jsp']
    
    return None

def get_url_info(url, timeout=10, proxy=None):
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
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)


        

        ret['success'] = True
        ret['status'] = res.status_code
        if 'Location' in res.headers:
            ret['redirect'] = res.headers['Location']
        elif 'location' in res.headers:
            ret['redirect'] = res.headers['location']
        
        soup = BeautifulSoup(res.text, 'html.parser')
        if soup.title:
            ret['title'] = soup.title.text.strip()

        if ret['title'] == 'Burp Suite Professional':
            ret['title'] = None
            ret['success'] = False
            ret['error'] = 'Burp failed to connect'
            ret['error_type'] = 'ConnectionError'
            return ret

        content_length = int(res.headers.get('Content-Length', '0')) if 'Content-Length' in res.headers else len(res.text)

        md5sum = md5(res.content).hexdigest() if content_length > 0 else None
        
        if md5sum in MD5_TABLE:
                ret['redirect'] = MD5_TABLE[md5sum]['redirect']
                ret['title'] = MD5_TABLE[md5sum]['title']
                return ret
        
        #if ret['title'] == None or len(ret['title']) < 1 and content_length > 0:

        if content_length > 0 and (ret['title'] == None or len(ret['title']) < 1):
            temp = get_redirect_html1(res.text, content_length)
            if temp != None:
                ret['redirect'] = temp
                return ret

            temp = get_redirect_http_meta(soup)
            if temp != None:
                ret['redirect'] = temp
                return ret
            temp = get_redirect_http_fortinet(res.text)
            if temp != None:
                ret['redirect'] = temp
                return ret

            temp = get_meta_copyright(soup)
            if temp != None:
                ret['title'] = temp
                return ret
            
            temp = check_rcats(res.text)
            if temp != None:
                ret['title'] = temp
                return ret
            temp  = check_radcom(res.text)
            if temp != None:
                ret['title'] = temp[0]
                ret['redirect'] = temp[1]
                return ret
            
            
    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.Timeout, requests.exceptions.ConnectTimeout) as e:
        ret['error'] = str(e)
        ret['error_type'] = type(e).__name__

    return ret


def run(urls, workers=5, timeout=1, log=False, proxy=None):
    #with futures.ThreadPoolExecutor(max_workers=5)
    
    data = []
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for url in urls:
                futures.append(executor.submit(get_url_info, url=url, timeout=timeout, proxy=proxy))
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
    argparser.add_argument('--proxy', help='Set proxy', type=str)

    if len(sys.argv) < 2:
        return argparser.print_help()

    args = argparser.parse_args(sys.argv[1:])

    proxy = {
        'http': f'http://{args.proxy}',
        'https': f'https://{args.proxy}'
    } if args.proxy else None

    if args.url:
        if len(args.url) < 10:
            return print('Invalid url')
        
        print(json.dumps(get_url_info(args.url, args.timeout, proxy), indent=args.indent))
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

    data = run(url_list, workers, timeout, args.log, proxy)
    if len(data) > 0:
        json.dump(data, args.output, indent=args.indent)
        print('Done :D')
    else:
        print("Returned empty")


if __name__ == '__main__':
    main()
