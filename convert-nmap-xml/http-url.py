import json, argparse, sys, glob, os
from datetime import datetime

class PathInput:
    path = None
    is_file = False
    name = None

    def __init__(self, p, i, n):
        self.path = p
        self.is_file = i
        self.name = n


# FileType copy
class ArgParsePathType(object):
    def __init__(self, mode='r', bufsize=-1, encoding=None, errors=None):
        self._mode = mode
        self._bufsize = bufsize
        self._encoding = encoding
        self._errors = errors

    def __call__(self, string):

        if os.path.isdir(string):
            return PathInput(string, False, string)

        if string == '-':
            if 'r' in self._mode:
                return sys.stdin.buffer if 'b' in self._mode else sys.stdin
            elif any(c in self._mode for c in 'wax'):
                return sys.stdout.buffer if 'b' in self._mode else sys.stdout
            else:
                msg = _('argument "-" with mode %r') % self._mode
                raise ValueError(msg)
        try:
            return PathInput(open(string, self._mode, self._bufsize, self._encoding, self._errors), True, string)
        except OSError as e:
            args = {'filename': string, 'error': e}
            message = ("can't open '%(filename)s': %(error)s")
            raise argparse.ArgumentTypeError(message % args)

    def __repr__(self):
        args = self._mode, self._bufsize
        kwargs = [('encoding', self._encoding), ('errors', self._errors)]
        args_str = ', '.join([repr(arg) for arg in args if arg != -1] + ['%s=%r' % (kw, arg) for kw, arg in kwargs if arg is not None])
        return '%s(%s)' % (type(self).__name__, args_str)


whitelist_ports = {
    '80': 'https',
    '443': 'http',
    '3000': 'http',
    '3001': 'http',
    '7000': 'http',
    '7001': 'http',
    '8000': 'http',
    '8080': 'http',
    '8081': 'http',
    '8443': 'https',
    '4700': 'http',
    '41101': 'http',
    '41102': 'http',
    '42091': 'http'
}

def run(file):
    global whitelist_ports
    data = None
    try:
        data = json.load(file)
    except Exception as e:
        return False, e

    urls = {}
    for ip in data['data']:
        for port in data['data'][ip]['ports']:
            if port in whitelist_ports:
                if port not in urls:
                    urls[port] = []
                urls[port].append('%s://%s%s' % (whitelist_ports[port], ip, '' if port == '80' or port == '443' else (':'+port)))
            
    return True, urls

def save_files(data, output_dir, basename):
    for port in data:
        if len(data[port]) > 0:
            with open(os.path.join(output_dir, f'{basename}-{port}.txt'), 'w') as file:
                for url in data[port]:
                    file.write(url + '\n')
                print('Done:',os.path.join(output_dir, f'{basename}-{port}.txt'))

def main():
    argparser = argparse.ArgumentParser()

    argparser.add_argument('-i','--input', help='Input file', type=ArgParsePathType('r'))
    argparser.add_argument('-o','--output', help='Output file', type=ArgParsePathType('w'))
    argparser.add_argument('--indent', help='Indent json output', type=int, default=0)
    argparser.add_argument('--ports', help='Separate by ports', action='store_true')
    argparser.add_argument('--name', help='Base file names', type=str)
    argparser.add_argument('--all', help='Output multiple files in one file', action='store_true')


    if len(sys.argv) < 2:
        return argparser.print_help()

    args = argparser.parse_args(sys.argv[1:])

    if args.input.is_file:
        success, data = run(args.input.path)
        if not success:
            return print(data)

        
        if not args.output:
            for port in data:
                for url in data[port]:
                    print(url)
        else:
            if args.ports:
                out = './'
                if args.output:
                    if args.output.is_file:
                        out = os.path.dirname(args.output.name)
                    else:
                        out = args.output.path

                filename = args.name if args.name else datetime.now().strftime('%d-%m-%Y-%H-%M-%S')

                save_files(data, out, filename)

            else:

                filename = os.path.basename(args.output.name) if args.output.is_file else ''
                handler = args.output.path if args.output.is_file else None

                if not handler:
                    try:
                        filename = os.path.join(args.output.path, datetime.now().strftime('%d-%m-%Y-%H-%M-%S') + '.url')
                        handler = open(filename, 'w')

                        filename = os.path.basename(filename)
                    except Exception as e:
                        return print(e)

                for port in data:
                    for url in data[port]:
                        handler.write(url + '\n')
                
                print('Done:', filename)
                handler.close()
    else:
        files = [i.replace('.\\', '').replace('.json', '') for i in glob.glob(os.path.join(args.input.path, '*.json'))]

        data = {}
        for filename in files:
            with open(filename + '.json', 'r') as file:
                name = os.path.basename(filename)
                success, temp = run(file)
                if not success:
                    print('%s: %s' % (name + '.json', temp))
                    continue
                
                data[name] = temp
        
        if not args.output:
            for i in data:
                for port in data[i]:
                    for url in data[i][port]:
                        print(url)
        else:



            if args.ports:
                out = './'
                if args.output:
                    out = os.path.dirname(args.output.name) if args.output.is_file else args.output.path

                if args.all:
                    basename = args.name if args.name else datetime.now().strftime('%d-%m-%Y-%H-%M-%S')

                    temp = {}
                    for i in data:
                        for port in data[i]:
                            if port not in temp:
                                temp[port] = []
                            temp[port].extend(data[i][port])

                    save_files(temp, out, basename)
                else:
                    for i in data:
                        save_files(data[i], out, i)
            else:
                filename = args.output.name if args.output and args.output.is_file else ''
                handler = args.output.path if args.output and args.output.is_file else None

                if not handler:
                    try:
                        out = './'
                        if args.output:
                            out = os.path.dirname(args.output.name) if args.output.is_file else args.output.path

                        filename = os.path.join(out, datetime.now().strftime('%d-%m-%Y-%H-%M-%S') + '.url')
                        handler = open(filename, 'w')
                    except Exception as e:
                        return print(e)
                
                for i in data:
                    for port in data[i]:
                        for url in data[i][port]:
                            handler.write(url + '\n')

                handler.close()
                print('Done:', filename)

if __name__ == '__main__':
    main()
