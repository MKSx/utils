from subprocess import Popen
from time import sleep
from os import system
import json


def screenshot(filename):
    system('gnome-screenshot -w -f {0}'.format(filename))

def execute_task(command, filename, seconds=2):
    print('Open Terminal')

    # Konsole:
    #x = Popen(['/usr/bin/konsole', '-e', './execute.sh', command])

    # Gnome terminal
    x = Popen(['/usr/bin/gnome-terminal', '--', './execute.sh', command])

    print('Wait {0} seconds'.format(seconds))

    sleep(seconds)

    print('Run screenshot command, output: {0}'.format(filename))

    screenshot(filename)

    print('Close Terminal')
    x.kill()
    return True

def main():
    
    ip = '127.0.0.1'
    user = 'USER'
    passwd = 'PASSWORD'
    hostname = 'HOSTNAME'

    execute_task("sshpass -p '{0}' ssh -oStrictHostKeychecking=no {1}@{2}".format(passwd, user, ip), '{0}-{1}.png'.format(user, hostname), 7)


if __name__ == '__main__':
    main()
