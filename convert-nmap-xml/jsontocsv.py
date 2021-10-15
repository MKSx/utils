import json, argparse, sys


def main():

    argparser = argparse.ArgumentParser()

    argparser.add_argument('-i','--input', help='Json input file', required=True, type=argparse.FileType('r'))
    argparser.add_argument('-o','--output', help='CSV output file ', type=argparse.FileType('w'))

    if len(sys.argv) < 2:
        return argparser.print_help()

    args = argparser.parse_args(sys.argv[1:])

    data = []
    try:
        data = json.load(args.input)
    except Exception as e:
        return print(e)

    args.output.write('ip,hostname,port,service,state\n')

    for i in data:
        hostname = i['hostnames'][0] if len(i['hostnames']) > 0 else ''

        for port in i['ports']:
            args.output.write('"%s","%s",%s,"%s",%s\n' % (i['ip'], hostname, port['port'], port['service'], port['state']))

    print('Arquivo salvo!')

if __name__ == '__main__':
    main()
