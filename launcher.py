"""Лаунчер"""

import subprocess
import os
import sys

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, '
                   'x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        if os.name == 'posix':
            PROCESS.append(subprocess.Popen(
                ['gnome-terminal', '-e', 'python3 server.py'],
                stdout=subprocess.PIPE))
            PROCESS.append(subprocess.Popen(
                ['gnome-terminal', '-e', 'python3 client.py -n test1'],
                stdout=subprocess.PIPE))
            PROCESS.append(subprocess.Popen(
                ['gnome-terminal', '-e', 'python3 client.py -n test2'],
                stdout=subprocess.PIPE))
            PROCESS.append(subprocess.Popen(
                ['gnome-terminal', '-e', 'python3 client.py -n test3'],
                stdout=subprocess.PIPE))
        elif os.name == 'nt':
            PROCESS.append(subprocess.Popen(
                'python server.py',
                creationflags=subprocess.CREATE_NEW_CONSOLE))
            PROCESS.append(subprocess.Popen(
                'python client.py -n test1',
                creationflags=subprocess.CREATE_NEW_CONSOLE))
            PROCESS.append(subprocess.Popen(
                'python client.py -n test2',
                creationflags=subprocess.CREATE_NEW_CONSOLE))
            PROCESS.append(subprocess.Popen(
                'python client.py -n test3',
                creationflags=subprocess.CREATE_NEW_CONSOLE))
        else:
            print(f'Платформа {os.name} не поддерживается')
            sys.exit(1)

    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
