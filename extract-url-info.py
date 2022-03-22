from operator import attrgetter
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
import json, argparse, sys, re
from hashlib import md5
import urllib.parse

#https://stackoverflow.com/a/41041028/13886183
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    pass


break_titles = [
    (True, 'HP BladeSystem Onboard'),
    (True, 'HP Virtual Connect'),
    (True, 'HP Integrated'),
    (True, 'HPE iLO Login'),
    (True, 'HPE Recovery'),
    (True, 'HP StoreEver'),
    (True, 'HP UCMDB Server'),
    (True, 'Cisco Systems'),
    (False, 'Cisco'),
    (True, 'Hitachi Device Manager'),
    (True, 'rondaweb.celular.intranet'),
    (True, 'Atrium Discovery'),
    (True, 'Supermicro'),
    (True, 'It works'),
    (True, 'OK'),
    (True, 'NOSSOS SISTEMAS'),
    (True, 'Tomcat is'),
    (True, 'Parallel Upgrade')
]

MD5_TABLE = {
    '4ada2be6f16e1623de939acae87ea6e7':{
        'redirect': '/webui/',
        'title': 'Cisco'
    },
    '37c1af0cf3934d2cdf504c63b93b0aa1': {
        'redirect': '/flow/auth/signin',
        'title': 'Senha Segura'
    },
    'ad9c3139081bf8eb46ef9afd2135c43f': {
        'redirect': '/sanproject/',
        'title': 'Hitachi Device Manager - Storage Navigator'
    },
    '9ecc093bbf2fedac8ee3918612446368': {
        'redirect': None,
        'title': 'Atrium Discovery internal tomcat server'
    },
    '06a808538adde87a7e5c74c4dcd4ffaa': {
        'redirect': None,
        'title': 'rondaweb.celular.intranet'
    },
    'f30839cac40540a6d293f296aace505e': {
        'redirect': None,
        'title': 'Supermicro - ATEN International'
    },
    'c7b4690c8c46625ef0f328cd7a24a0a3': {
        'redirect': None,
        'title': 'It works!'
    },
    '5388f60d7695cb57b87c799ee62d20b2': {
        'redirect': None,
        'title': 'It works!'
    },
    'e0aa021e21dddbd6d8cecec71e9cf564': {
        'redirect': None,
        'title': 'OK'
    },
    'ebaa327ac88e86c379b64a9b5769aada': {
        'redirect': None,
        'title': 'NOSSOS SISTEMAS ESTAO OCUPADOS POR FAVOR ACESSE NOVAMENTE EM ALGUNS SEGUNDOS ...'
    },
    'd808943568391c74545c36695b8d7f1c': {
        'redirect': None,
        'title': 'Tomcat is running...'
    },
    'c91122466ca87e8ec6c43c77f72dd9e4': {
        'redirect': None,
        'title': 'Parallel Upgrade Tool - putapp.jnlp'
    },
    '2f650fff5307a9202bbc639bdd20db18': {
        'redirect': None,
        'title': 'Parallel Upgrade Tool - putapp.jnlp'
    },
    '3d315b7b59da8a876619b015659c4d33': {
        'redirect': '/page/login.html',
        'title': 'Symatec Remote Management'
    }
}



def check_leave_server(url, redirect):
    proto = 'https' if url.startswith('https://') else 'http'
    host = re.sub(r'(\/|\?)(.*)','', url.replace(proto + '://', ''))
    if redirect:
        if redirect.startswith('http://') or redirect.startswith('https://'):
            proto = 'https' if redirect.startswith('https://') else 'http'
            if not redirect.startswith(proto + '://' + host):
                return True
    return False

def check_redirect_https(url, redirect):
    proto = 'https' if url.startswith('https://') else 'http'
    host = re.sub(r'(\/|\?)(.*)','', url.replace(proto + '://', ''))
    if proto == 'http' and redirect:
        if redirect.startswith('http://') or redirect.startswith('https://'):
            proto = 'https' if redirect.startswith('https://') else 'http'
            if proto == 'https':
                if redirect.startswith(proto + '://' + host):
                    return True
    return False


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


def getILO(url, timeout=10, proxy=None):
    try:
        if not url.endswith('/'):
            url += '/'
        res = requests.get(f'{url}redfish/v1/', verify=False, timeout=timeout, proxies=proxy)
        if res.status_code == 200 and (res.headers.get('Content-Type', '').startswith('application/json') or res.text.startswith('{"secjmp"')):
            data = res.json()
            if 'Oem' in data:
                if 'Hpe' in data['Oem']:
                    if 'Moniker' in data['Oem']['Hpe'] and 'PRODTAG' in data['Oem']['Hpe']['Moniker']:
                        return 0, data['Oem']['Hpe']['Moniker']['PRODTAG']
                    if 'Manager' in data['Oem']['Hpe'] and len(data['Oem']['Hpe']['Manager']) > 0 and 'ManagerType' in data['Oem']['Hpe']['Manager'][0]:
                        return 0, data['Oem']['Hpe']['Manager'][0]['ManagerType']
                elif 'Hp' in data['Oem']:
                    if 'Moniker' in data['Oem']['Hp'] and 'PRODTAG' in data['Oem']['Hp']['Moniker']:
                        return 0, 'HPE ' + data['Oem']['Hp']['Moniker']['PRODTAG']
                    if 'Manager' in data['Oem']['Hp'] and len(data['Oem']['Hp']['Manager']) > 0 and 'ManagerType' in data['Oem']['Hp']['Manager'][0]:
                        return 0, 'HPE ' + data['Oem']['Hp']['Manager'][0]['ManagerType']
        return 1, 'Not Detected'
    except Exception as e:
        return 2, str(e)


def getiDRAC(url, timeout=10, proxy=None):
    try:

        res = requests.get(urllib.parse.urljoin(url,'data?get=prodServerGen'), verify=False, timeout=timeout, proxies=proxy)
        if res.status_code == 200 and res.headers.get('Content-Type', '').startswith('text/xml'):
            if res.text.find('<prodServerGen>12G</prodServerGen>') > 0:
                return 0,'iDRAC7'
            elif res.text.find('<prodServerGen>13G</prodServerGen>') > 0:
                return 0,'iDRAC8'
        res = requests.get(urllib.parse.urljoin(url,'restgui/locale/strings/locale_str_en.json'), verify=False, timeout=timeout, proxies=proxy)
        if res.status_code == 200 and res.headers.get('Content-Type', '').startswith('application/json'):
            data = res.json()
            if 'app_title' in data:
                return 0, data['app_title']
        res = requests.get(urllib.parse.urljoin(url,'login.html'), verify=False, timeout=timeout, proxies=proxy)
        if res.status_code == 200:
            if res.text.find('var tmpDracName = "iDRAC6";') > 0:
                return 0, 'iDRAC6'
            if res.text.find('/images/Ttl_2_iDRAC7_Base_ML.png') > 0:
                return 0, 'iDRAC7'
        return 1, 'Not Detected'
    except Exception as e:
        return 2, [str(e), type(e).__name__]



def get_redirect_html(text, soup, length=0):
    if length < 12000:
        temp = re.search(r'window.location=[\'|"](.*?)["|\']', text, re.IGNORECASE)
        if temp:
            return temp[1]

        temp = re.search(r'location.href[\s+?]?=[\s+?]?[\'|"](.*?)["|\']', text, re.IGNORECASE)
        if temp:
            return temp[1]

        temp = re.search(r'location[\s+?]?=[\s+?]?[\'|"](.*?)["|\']', text, re.IGNORECASE)
        if temp:
            return temp[1]

        temp = re.search(r'location.replace\(["|\'](.*?)["|\']\)', text, re.IGNORECASE)
        if temp:
            return temp[1]
        if text.find('document.location.href = thisURL + "index_en.html";') > 0:
            return '/index_en.html'

    if soup:
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

def getDellChassis(url, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/cgi-bin/webcgi/login'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        if res.text.find('Chassis Management') > 0:
            return 0, 'Dell Chassis Management Controller'
        
        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]
            
def getDellDDSM(url, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/ddem/login/'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        temp = re.search(r"window.loginInfo = '(.*?)'", res.text)
        if temp and temp[1].startswith('{'):
            data = json.loads(temp[1])
            if 'brand' in data and 'loginTitle' in data['brand']:
                return 0, data['brand']['loginTitle']
        
        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]

def getIBMC(url, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/redfish/v1'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        if res.status_code == 200 and res.headers.get('Content-Type', '').startswith('application/json'):
            data = res.json()
            if 'Oem' in data and 'Huawei' in data['Oem'] and 'ProductName' in data['Oem']['Huawei'] and 'SoftwareName' in data['Oem']['Huawei']:
                return 0, data['Oem']['Huawei']['SoftwareName'] + ' - ' + data['Oem']['Huawei']['ProductName']
        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]

def getHPEStorage(url, v2, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/v2/js/js_overrides.js' if v2 else '/v3/js/brandStrings.js'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        if res.status_code == 200:
            temp = re.search(r'applicationTitle(\s+\=\s+|\:\s+)"(.*)"[;|,]', res.text)
            if temp:
                return 0, temp[2]
        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]

def getCiscoIse(url, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/admin/login.jsp'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        if res.status_code == 200:
            # Check Cisco Product
            if res.text.find('Cisco Systems') > 0:
                temp = re.search('productName="(.*?)"', res.text)
                if temp:
                    return 0, ('Cisco - ' if temp[1] == 'Identity Services Engine' else '') + temp[1]
        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]

def getVMWare(url, s, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/en/welcomeRes.js' if s != 'ID_WelcomePsc' else '/resources/locale/en/welcomeRes.js'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        if res.status_code == 200:
            temp = re.search(s + '[\s+?]?=[\s+?]?[\'|"](.*?)["|\']', res.text)
            if temp:
                return 0, ('VMware - ' if temp[1].find('VMware') < 0 else '') + temp[1]

        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]

def getGenesysPulse(url, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/pulse/api/plugins/pulse'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        if res.status_code == 200 and res.headers.get('Content-Type', '').startswith('application/json'):
            data = res.json()
            if 'name' in data:
                return 0, ('Genesys - ' if 'provider' in data and data['provider'].startswith('Genesys') else '') + data['name']
        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]

def getLenel(url, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/login.shtm'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        if res.status_code == 200:
            temp =  re.search('<CENTER><H1>(.*?)</H1><HR color="#0055fa"></CENTER>', res.text, re.IGNORECASE)
            if temp:
                return 0, 'Lenel - ' + temp[1].replace('&nbsp;', ' ')
        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]

def getEMCUnisphere(url, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/engMessage.js'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        if res.status_code == 200:
            temp = re.search('INDEX_TITLE:[\s+?]?[\'|"](.*?)[\'|"]', res.text, re.IGNORECASE)
            if temp:
                return 0, temp[1]
        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]


def getHuaweiFusionSphere(url, timeout=10, proxy=None):
    try:
        res = requests.get(urllib.parse.urljoin(url, '/SSOSvr/res/login_en_US.js'), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        if res.status_code == 200:
            data = json.loads(res.text.replace('var login_msg = ', '').replace('};', '}'))
            if 'loginTitleOpenStack' in data:
                return 0, 'Huawei - ' + data['loginTitleOpenStack']
        return 1, None
    except Exception as e:
        return 2, [str(e), type(e).__name__]



def get_title_redirect(base, url, timeout, proxy, r=0):
    #print(f'get_title_redirect("{url}", {timeout})')
    try:
        res = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)

        title = None
        redirect = None

        # Check lenovo
        if url.endswith('/designs/imm/index.php'):
            if res.text.find('/designs/imm/images/title-imm.png') > 0:
                return 0, 'Lenovo - Integrated Management Module', redirect

        content_length = int(res.headers.get('Content-Length', '0')) if 'Content-Length' in res.headers else len(res.text)
        md5sum = md5(res.content).hexdigest() if content_length > 0 else None



        soup = BeautifulSoup(res.text, 'html.parser')

        if soup.title:
            title = soup.title.text.strip().replace('\n', '').replace('\u00a0', ' ').replace('\t', ' ')

        if 'Location' in res.headers:
            redirect = res.headers['Location']

        if not title and not redirect:
            redirect = get_redirect_html(res.text, soup, content_length)
    
        if r < 1 and redirect and not check_leave_server(base, redirect):
            return get_title_redirect(
                base,
                urllib.parse.urljoin(base if redirect.startswith('/') else url, redirect) if not (redirect.startswith('http://') or redirect.startswith('https://')) else redirect,
                timeout,
                proxy,
                r+1
            )
            
        if not title and not redirect and md5sum in MD5_TABLE:
            title = MD5_TABLE[md5sum]['title']
            redirect = MD5_TABLE[md5sum]['redirect']
        return 0, title, redirect

    except Exception as e:
        return 1, [str(e), type(e).__name__], None



def check_products(ret, text, md5sum, soup, proxy=None, timeout=10, follow_redirects=False):

    # Check leave from server
    if check_leave_server(ret['url'], ret['redirect']):
        print('Leave')
        return ret

    if not ret['redirect'] and not ret['title']:
        if md5sum in MD5_TABLE:
            ret['title'] = MD5_TABLE[md5sum]['title']
            ret['redirect'] = MD5_TABLE[md5sum]['redirect']

    if ret['status'] != 302 and ret['status'] != 301 and ret['title'] and len(ret['title']) > 0:
        for i in break_titles:
            if i[0]:
                if ret['title'].startswith(i[1]):
                    return ret
            else:
                if ret['title'].find(i[1]) > -1:
                    return ret

    copyright_meta = get_meta_copyright(soup)

    # HPE products
    if (ret['server'] and ret['server'].find('HPE-iLO-Server') > -1) or (copyright_meta and copyright_meta.find('Hewlett Packard Enterprise') > -1):
        if not ret['title'] or len(ret['title']) < 1:
            code, title = getILO(ret['url'], timeout, proxy)
            if code == 0:
                ret['title'] = title
                return ret

    if not ret['redirect']:
        ret['redirect'] = get_redirect_html(text, soup, ret['content-length'])
        if check_leave_server(ret['url'], ret['redirect']):
            return ret
    



    if ret['redirect']:
        
        #print('redirect: "%s"' % ret['redirect'])
        # iDRAC
        if ret['redirect'].endswith('/start.html') or ret['redirect'].endswith('/sclogin.html?console'):
            code, title = getiDRAC(ret['url'].replace('/restgui/start.html','').replace('/start.html',''), timeout, proxy)
            if code == 2:
                ret['error'] = title[0]
                ret['error_type'] = title[1]
            elif code == 0:
                ret['title'] = title
                return ret

        # Chassis
        if ret['redirect'].endswith('/cgi-bin/webcgi/index'):
            code, title = getDellChassis(ret['url'], timeout, proxy)
            if code == 2:
                ret['error'] = title[0]
                ret['error_type'] = title[1]
            elif code == 0:
                ret['title'] = title
                return ret

        
        # Dell Data Domain System Manager
        if ret['redirect'].endswith('/ddem'):
            code, title = getDellDDSM(ret['url'], timeout, proxy)
            if code == 2:
                ret['error'] = title[0]
                ret['error_type'] = title[1]
            elif code == 0:
                ret['title'] = title
                return ret

        # Check HPE Storage Management Utility
        if ret['redirect'].endswith('/v2/index.html') or ret['redirect'].endswith('/v3/index.html'):
            code, title = getHPEStorage(ret['url'],  ret['redirect'].endswith('/v2/index.html'), timeout, proxy)
            if code == 2:
                ret['error'] = title[0]
                ret['error_type'] = title[1]
            elif code == 0:
                ret['title'] = title
                return ret

        # Check Cisco Ise
        if ret['redirect'].endswith('/admin/'):
            code, title = getCiscoIse(ret['url'], timeout, proxy)
            if code == 2:
                ret['error'] = title[0]
                ret['error_type'] = title[1]
            elif code == 0:
                ret['title'] = title
                return ret
        
        # Set VmWare
        if ret['redirect'].endswith('/SAAS/apps/'):
            ret['title'] = 'VMware Workspace ONE'
            return ret

        # Check genesys pulse
        if ret['redirect'].endswith('/pulse'):
            code, title = getGenesysPulse(ret['url'], timeout, proxy)
            if code == 2:
                ret['error'] = title[0]
                ret['error_type'] = title[1]
            elif code == 0:
                ret['title'] = title
                return ret

        # Huawei Openstack
        if ret['redirect'].endswith('/SSOSvr/login'):
            code, title = getHuaweiFusionSphere(ret['url'], timeout, proxy)
            if code == 2:
                ret['error'] = title[0]
                ret['error_type'] = title[1]
            elif code == 0:
                ret['title'] = title
                return ret

        # Follow redirect
        code, title, redirect = get_title_redirect(ret['url'], urllib.parse.urljoin(ret['url'], ret['redirect']) if not (ret['redirect'].startswith('http://') or ret['redirect'].startswith('https://')) else ret['redirect'], timeout, proxy)
        if code != 0:
            ret['error'] = title[0]
            ret['error_type'] = title[1]
        else:
            ret['title'] = title
            ret['redirect'] = redirect if redirect else ret['redirect']
    else:
        # No title
        if not ret['title'] or len(ret['title']) < 1:
            # Angulas app
            if text.find('ng-class') > 0 or text.find('ng-controller') > 0:
                code, title = getIBMC(ret['url'], timeout, proxy)
                if code == 2:
                    ret['error'] = title[0]
                    ret['error_type'] = title[1]
                elif code == 0:
                    ret['title'] = title
                    return ret
            temp = re.search(r'document.write\("<title>(.*?)<\/title>"\)', text, re.IGNORECASE)
            if temp:

                ret['title'] = temp[1].replace('" + ', '').replace(' + "', '')

                # Check VMware
                if ret['title'] in ['ID_EESX_Welcome', 'ID_WelcomePsc', 'ID_VC_Welcome']:
                    code, title = getVMWare(ret['url'], ret['title'], timeout, proxy)
                    if code == 2:
                        ret['error'] = title[0]
                        ret['error_type'] = title[1]
                    elif code == 0:
                        ret['title'] = title
                        return ret

            # Lenel
            if text.find('document.getElementById("home").src = "/whome2.shtm";') > 0:
                code, title = getLenel(ret['url'], timeout, proxy)
                if code == 2:
                    ret['error'] = title[0]
                    ret['error_type'] = title[1]
                elif code == 0:
                    ret['title'] = title
                    return ret
            # Weblogic
            if text.find('Welcome to BEA WebLogic Integration') > 0:
                ret['title'] = 'Welcome to BEA WebLogic Integration'
                return ret
            if text.find("document.title= messageMap['INDEX_TITLE'];"):
                code, title = getEMCUnisphere(ret['url'], timeout, proxy)
                if code == 2:
                    ret['error'] = title[0]
                    ret['error_type'] = title[1]
                elif code == 0:
                    ret['title'] = title
                    return ret


    return ret

def get_url_info(url, timeout=10, proxy=None, https_redirect=False):

    ret = {
        'success': False,
        'error': None,
        'error_type': None,
        'status': 200,
        'redirect': False,
        'title': None,
        'url': url,
        'server': None,
        'content-length': 0
    }

    try:
        
        res = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, verify=False, timeout=timeout, allow_redirects=False, proxies=proxy)


        ret['status'] = res.status_code
        if res.status_code == 404:
            ret['redirect'] = '/console/login/LoginForm.jsp'

        ret['success'] = True
        
        if 'Location' in res.headers:
            ret['redirect'] = res.headers['Location']
        elif 'location' in res.headers:
            ret['redirect'] = res.headers['location']

        if not https_redirect and check_redirect_https(url, ret['redirect']):
            ret['redirect'] = ret['redirect'].replace(':443/', '/').replace(':443?', '?').replace(':443', '')

            return get_url_info(ret['redirect'], timeout, proxy, True)

        soup = BeautifulSoup(res.text, 'html.parser')
        if soup.title:
            ret['title'] = soup.title.text.strip()


        ret['server'] = res.headers.get('Server', None)
 
        ret['content-length'] = int(res.headers.get('Content-Length', '0')) if 'Content-Length' in res.headers else len(res.text)

        md5sum = md5(res.content).hexdigest() if ret['content-length'] > 0 else None
        ret = check_products(ret, res.text, md5sum, soup, proxy, timeout)


    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.Timeout, requests.exceptions.ConnectTimeout) as e:
        ret['error'] = str(e)
        ret['error_type'] = type(e).__name__
    except Exception as e:
        print(e)
    return ret

def run(urls, workers=5, timeout=1, log=False, proxy=None):
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
                    
                    print('URL: %s - Status: %d - Success: %s - Error: %s - Title: %s - Redirect: %s - Server: %s - Content-Length: %d' % (
                        res['url'], res['status'], res['success'], res['error_type'], res['title'], res['redirect'], res['server'], res['content-length']
                    ))

    except KeyboardInterrupt:
        pass

    return data

def main():

    argparser = argparse.ArgumentParser()

    argparser.add_argument('-i','--input', help='File with url list', type=argparse.FileType('r'))
    argparser.add_argument('-o','--output', help='Output file', type=argparse.FileType('w'))
    argparser.add_argument('-l', '--log', help='Print url detail progress', action='store_true')
    argparser.add_argument('-t','--timeout', help='Timeout request', type=int, default=10)
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
