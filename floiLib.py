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
    f.writelines(content)
    f.close()


def logSave():
    global logID, logBusy, logs # Пробрасываем в функцию
    while True:
        time.sleep(60) # С переодичностью в 1 минуту
        logBusy = True # Дополняем файл
        f = open(f"logs/log_{logID}.txt", 'a')
        for i in logs: # Пишем с разделителем строки
            f.writelines(f"{i}\r\n")
        f.close()
        logs = [] # И очищаем список что-бы избежать возможную утечку паямти
        logBusy = False

        if not varsChanged:
            continue

        writeFile("vars", vars)
        varsChanged = False



def init(vers):
    global logID, vars
    while os.path.isfile(f"logs/log_{logID}.txt"): # Если текущее имя лога занято
        logID += 1 # Проверяем следущее имя

    writeFile(f"logs/log_{logID}.txt", [f"ВЕРСИЯ СЕРВЕРА: {vers}", f"{time.time()}", ""])
    vars = readFile("vars")

    threading.Thread(target=logSave, args=()).start()


def log(msg): # Записать в лог
    while logBusy:
        time.sleep(0.01) # Ждём 10 мс что-бы избежать зависания
    logs.append(msg)
    print(msg) # Нe обязательно


def getVar(id):
    global vars
    return vars[id]


def setVar(id, value):
    vars[id] = value
    varsChanged = True
