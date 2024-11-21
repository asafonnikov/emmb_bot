def readFile(path):
    with open(path, 'r') as f:
        return f.readlines()

vars = readFile("vars")

def writeFile(path, content):
    content = [i + "\r\n" for i in content]
    with open(path, 'w') as f:
        f.writelines(content)

def appendFile(path, content):
    f = open(path, 'a')
    content = [i + "\r\n" for i in content]
    f.writelines(content)
    f.close()


def getVar(id):
    global vars
    return vars[id].rstrip()


def setVar(id, value):
    global vars, varsChanged
    vars[id] = value
    writeFile("vars", vars)
