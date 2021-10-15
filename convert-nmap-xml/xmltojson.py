import xml.etree.ElementTree as ET
import json, argparse, sys

def getInfo(elements):
    flag_addr = False

    ret = {
        'ip': '',
        'hostnames': [],
        'ports': []
    }
    temp = ''
    for element in elements:
        if flag_addr == False and element.tag == 'address':
            attr = element.attrib
            if 'addrtype' in attr and attr['addrtype'] == 'ipv4' and 'addr' in attr:
                ret['ip'] = attr['addr']
                flag_addr = True
        elif element.tag == 'hostnames' and len(element) > 0:
            for hostname in element:
                if hostname.tag == 'hostname':
                    attr = hostname.attrib
                    if 'name' in attr:
                        ret['hostnames'].append(attr['name'])
                        break
        elif element.tag == 'ports':
            for port in element:
                if port.tag == 'port':
                    attr = port.attrib
                    
                    if 'portid' in attr:
                        temp = {
                            'port': attr['portid']
                        }
                        for i in port:
                            if i.tag == 'state':
                                attr = i.attrib
                                if 'state' in attr:
                                    temp['state'] = attr['state']
                            elif i.tag == 'service':
                                attr = i.attrib
                                if 'name' in attr:
                                    temp['service'] = attr['name']
                        
                        ret['ports'].append(temp)
            
    return ret


def main():

    argparser = argparse.ArgumentParser()

    argparser.add_argument('-i','--input', help='Input file', required=True, type=argparse.FileType('r'))
    argparser.add_argument('-o','--output', help='Output file', type=argparse.FileType('w'))

    if len(sys.argv) < 2:
        return argparser.print_help()

    args = argparser.parse_args(sys.argv[1:])


    tree = ET.parse(args.input)
    root = tree.getroot()

    data = []
    for child in root:
        if child.tag == 'host':
            data.append(getInfo(child))

    if not args.output:
        print(json.dumps(data))
    else:
        json.dump(data, args.output)
        print('Finalizado!')
   
    

if __name__ == '__main__':
    main()
