
import xml.etree.ElementTree as ET
import json, argparse, sys

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

def main():

    argparser = argparse.ArgumentParser()

    argparser.add_argument('-i','--input', help='Input file', required=True, type=argparse.FileType('r'))
    argparser.add_argument('-o','--output', help='Output file', type=argparse.FileType('w'))
    argparser.add_argument('--indent', help='Indent json output', type=int, default=0)


    if len(sys.argv) < 2:
        return argparser.print_help()

    args = argparser.parse_args(sys.argv[1:])

    data = parse_file(args.input)


    if not args.output:
        print(json.dumps(data, indent=args.indent))
    else:
        json.dump(data, args.output, indent=args.indent)

    print('Done :D')

    

if __name__ == '__main__':
    main()
