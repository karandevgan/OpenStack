import os

def readFile(path, n):
    lines = os.popen('tail -' + str(n) + ' ' + path).readlines()
    return lines