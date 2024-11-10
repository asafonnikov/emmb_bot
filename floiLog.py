import time, os, threading

logs = [] # Логи
logBusy = False # True когда логи сбрасываются на диск и писать нельзя
logID = 0 # ID текущего файла лога

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


def init(vers):
    global logID
    while os.path.isfile(f"logs/log_{logID}.txt"): # Если текущее имя лога занято
        logID += 1 # Проверяем следущее имя

    f = open(f"logs/log_{logID}.txt", 'w')
    f.write(f"ВЕРСИЯ СЕРВЕРА: {vers}\r\nUNIX ВРЕМЯ: {time.time()}\r\n\r\n")
    f.close() # Пишем главную информацию о сервере

    threading.Thread(target=logSave, args=()).start()


def log(msg): # Записать в лог
    while logBusy:
        time.sleep(0.01) # Ждём 10 мс что-бы избежать зависания
    logs.append(msg)
    print(msg) # Нe обязательно
