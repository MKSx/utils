#!/bin/python3

from colorama import Style, Fore
from colorama import init as colorama_init


colorama_init()

import argparse, sys, os

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir: {path} is not a valid path")
def dir_output(path):
    output = './' if not path or len(path.replace(' ', '')) < 1 else path


    if not (output.startswith('./') or output.startswith('../') or output.startswith('/')):
        path = './' + path

    if not os.path.isdir(output):
        basepath = os.path.dirname(output)

        if not basepath or len(basepath) < 1:
            basepath = './'

        if not os.path.isdir(basepath):
            raise argparse.ArgumentTypeError(f"output_dir: {basepath} is not a valid path")

        if not os.access(basepath, os.W_OK):
            raise argparse.ArgumentTypeError(f"output_dir: {basepath} is not writable")

        try:
            os.mkdir(output)
        except Exception as e:
            raise argparse.ArgumentTypeError(f"output_dir: Unable create a new dir: {path}")

        if path.endswith("/"):
            path = path[:len(path) - 1]

    else:
        if not os.access(output, os.W_OK):
            raise argparse.ArgumentTypeError(f"output_dir: {path} is not writable")

            if not path.endswith('/'):
                path = parth + '/'

    return path

def build(repository, output):

    
    if output.endswith('/'):
        if repository == './':
            output += 'output'
        else:
            if repository.lower().endswith('.git'):
                basename = os.path.basename(repository)
                output += basename[:len(basename) - 4]
            else:
                output += os.path.basename(repository) + '-output'

        if os.path.isdir(output) and not os.access(output, os.W_OK):
            for i in range(1, 10000):
                if not os.path.isdir(f'{output}-{i}'):
                    output = f'{output}-{i}'
                    break
        if not os.path.isdir(output):
            try:
                os.mkdir(output)
            except Exception as e:
                print(f"Unable create a new dir: {output}")
                return 2


    repo_name = os.path.basename(repository)

    if repo_name == '.':
        repo_name = repository
    
    print(f'{Style.BRIGHT}{Fore.YELLOW}[Building] {Style.RESET_ALL}{Style.BRIGHT}{repo_name}{Style.RESET_ALL}')
    ret = os.system(f'PH123243=$(pwd) && cd {repository} && git archive master | (cd $PH123243 && cd {output} && tar x)')
    if ret != 0:
        print(f'{Style.BRIGHT}{Fore.RED}[Build Fail] {Style.RESET_ALL}{Style.BRIGHT}{repo_name}{Style.RESET_ALL}')
        return 1
    else:
        print(f'{Style.BRIGHT}{Fore.BLUE}[Build Success] {Style.RESET_ALL}{Style.BRIGHT}{repo_name}{Style.RESET_ALL}')
        return 0

def main():
    argparser = argparse.ArgumentParser()

    argparser.add_argument('-r', '--repository', help='Repository to build', type=dir_path)
    argparser.add_argument('-o', '--output', help='Output repository build', type=dir_output, default='./')
    argparser.add_argument('--all', help='Build all repositories folders with .git', action='store_true', default=False)

    if len(sys.argv) < 2:
        return argparser.print_help()

    args = argparser.parse_args(sys.argv[1:])

    

    if not args.all:
        if not args.repository:
            return argparser.print_help()
            
        build(args.repository, args.output)
    else:
        repository = './' if not args.repository else args.repository
        repositories = [f for f in os.listdir(repository) if os.path.isdir(os.path.join(repository, f)) and f.lower().endswith('.git')]
        
        output = args.output if args.output.endswith('/') else (args.output + '/')

        for repo in repositories:
            try:
                if build(os.path.join(repository, repo), output) == 1:
                    try:
                        os.rmdir(output + repo[:len(repo) - 4])
                    except Exception as e:
                        pass
            except Exception as e:
                print(e)

        


if __name__ == '__main__':
    main()
