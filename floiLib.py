import time, os, threading

logs = [] # Логи
logBusy = False # True когда логи сбрасываются на диск и писать нельзя
logID = 0 # ID текущего файла лога
vars = []
varsChanged = False

def readFile(path):
    f = open(path, 'r')
    try:
        return f.readlines()
    finally:
        f.close()


def writeFile(path, content):
    f = open(path, 'w')
    content = [i + "\r\n" for i in content]
    f.writelines(content)
    f.close()


def appendFile(path, content):
    f = open(path, 'a')
    content = [i + "\r\n" for i in content]
    f.writelines(content)
    f.close()


def saveAll():
    global logID, logBusy, logs, vars, varsChanged
    logBusy = True # Дополняем файл
    appendFile(f"logs/log_{logID}.txt", logs)
    logs = [] # И очищаем список что-бы избежать возможную утечку паямти
    logBusy = False

    if not varsChanged:
        return

    writeFile("vars", vars)
    varsChanged = False


def autoSave():
    while True:
        time.sleep(60) # С переодичностью в 1 минуту
        saveAll()



def init(vers):
    global logID, vars
    while os.path.isfile(f"logs/log_{logID}.txt"): # Если текущее имя лога занято
        logID += 1 # Проверяем следущее имя

    writeFile(f"logs/log_{logID}.txt", [f"ВЕРСИЯ СЕРВЕРА: {vers}", f"{time.time()}", ""])
    vars = readFile("vars")

    threading.Thread(target=autoSave, args=()).start()


def log(msg): # Записать в лог
    while logBusy:
        time.sleep(0.01) # Ждём 10 мс что-бы избежать зависания
    logs.append(msg)
    print(msg) # Нe обязательно


def getVar(id):
    global vars
    return vars[id]


def setVar(id, value):
    global vars, varsChanged
    vars[id] = value
    varsChanged = True
