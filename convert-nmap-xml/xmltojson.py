
import xml.etree.ElementTree as ET
import json, argparse, sys, glob, os

def parse_hostnames(hosts, debug=False):
    ret = []
    for name in hosts:
        
        if name.tag == 'hostname':
            ret.append(name.attrib['name'])

    if debug:
        print(ret)
        
    return ret if len(ret) > 0 else None

def parse_ports(ports):
    ret = {}
    for port in ports:
        if port.tag != 'port':
            continue
        
        portid = ''
        temp = {
            'protocol': '',
            'state': None,
            'service': None,
            'banner': None
        }
        portid = port.attrib['portid']
        temp['protocol'] = port.attrib['protocol']
        for info in port:
            if info.tag == 'state':
                temp['state'] = info.attrib['state']
            elif info.tag == 'service':
                temp['service'] = info.attrib['name']
            elif info.tag == 'script':
                if info.attrib['id'] == 'banner':
                    temp['banner'] = info.attrib['output']
        ret[portid] = temp

    return ret if len(ret) > 0 else None

def parse_host(host):
    ret = {
        'hostname': [],
        'ports': None
    }
    ip = None
    for child in host:
        if child.tag == 'address':
            if ip == None and child.attrib['addrtype'] == 'ipv4':
                ip = child.attrib['addr']
        if child.tag == 'hostnames':
            ret['hostname'] = parse_hostnames(child)
        if child.tag == 'ports':
            ret['ports'] = parse_ports(child)
    
    return ip,ret
    

def parse_file(file):
    tree = ET.parse(file)
    root = tree.getroot()


    scan = {
        'nmaprun': {},
        'scaninfo': {},
        'data': {}
    }

    if root.tag == 'nmaprun':
        for attr in root.attrib:
            if attr != 'xmloutputversion':
                scan['nmaprun'][attr] = root.attrib[attr]

    
    for child in root:
        if child.tag == 'scaninfo':
            for info in child.attrib:
                scan['scaninfo'][info] = child.attrib[info]
        elif child.tag == 'host':

            ip, temp = parse_host(child)
            scan['data'][ip] = temp
    return scan


class PathInput:
    path = None
    is_file = False

    def __init__(self, p, i):
        self.path = p
        self.is_file = i


# FileType copy
class ArgParsePathType(object):
    def __init__(self, mode='r', bufsize=-1, encoding=None, errors=None):
        self._mode = mode
        self._bufsize = bufsize
        self._encoding = encoding
        self._errors = errors

    def __call__(self, string):

        if os.path.isdir(string):
            return PathInput(string, False)

        if string == '-':
            if 'r' in self._mode:
                return sys.stdin.buffer if 'b' in self._mode else sys.stdin
            elif any(c in self._mode for c in 'wax'):
                return sys.stdout.buffer if 'b' in self._mode else sys.stdout
            else:
                msg = _('argument "-" with mode %r') % self._mode
                raise ValueError(msg)
        try:
            return PathInput(open(string, self._mode, self._bufsize, self._encoding, self._errors), True)
        except OSError as e:
            args = {'filename': string, 'error': e}
            message = ("can't open '%(filename)s': %(error)s")
            raise argparse.ArgumentTypeError(message % args)

    def __repr__(self):
        args = self._mode, self._bufsize
        kwargs = [('encoding', self._encoding), ('errors', self._errors)]
        args_str = ', '.join([repr(arg) for arg in args if arg != -1] + ['%s=%r' % (kw, arg) for kw, arg in kwargs if arg is not None])
        return '%s(%s)' % (type(self).__name__, args_str)


def main():

    argparser = argparse.ArgumentParser()

    argparser.add_argument('-i','--input', help='Input file', type=ArgParsePathType('r'))
    argparser.add_argument('-o','--output', help='Output file', type=ArgParsePathType('w'))
    argparser.add_argument('--indent', help='Indent json output', type=int, default=0)


    if len(sys.argv) < 2:
        return argparser.print_help()

    args = argparser.parse_args(sys.argv[1:])

    if args.input.is_file:
        if args.output and not args.output.is_file:
            return print('Output precisa ser um arquivo!')

        data = parse_file(args.input)
        if not args.output:
            print(json.dumps(data, indent=args.indent))
        else:
            json.dump(data, args.output.path, indent=args.indent)    
    else:
        if args.output and args.output.is_file:
            return print('Output precisa ser um diretório!')

        out = args.output.path if args.output else './'

        files = [i.replace('.\\', '').replace('.xml', '')  for i in glob.glob(os.path.join(args.input.path, '*.xml'))]
        for filename in files:
            with open(filename + '.xml', 'r') as finput, open(os.path.join(out, os.path.basename(filename) + '.json'), 'w') as foutput:
                json.dump(parse_file(finput), foutput, indent=4)

    print('Done :D')

if __name__ == '__main__':
    main()
