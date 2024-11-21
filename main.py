import telebot, floiLib, os, logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="log.log", level=logging.INFO)

# Сам бот
botToken = floiLib.readFile("../botToken")[0].rstrip()
bot = telebot.TeleBot(botToken)
logger.debug("Бот загружен")

# Комманда для перезапуска
launchCommand = floiLib.readFile("../launchCommand")[0].rstrip()
logger.debug("Комманда загружена")

# Плохие слова
badWords = floiLib.readFile("badWords")
badWords = [i.rstrip() for i in badWords]
logger.info(f"Загружено {len(badWords)} плохих слов")

# Такие себе слова, не много можно
sosoWords = floiLib.readFile("sosoWords")
sosoWords = [i.rstrip() for i in sosoWords]
logger.info(f"Загружено {len(sosoWords)} сомнительных слов")

# Последнии удаления пользователя
lastDelete = []

# Слово запрощеное на удаление
requestWord = ""
requestStatus = False

# Удалет все подряд повторяющие сообщения
def toUniqueSymbols(msg):
    newMsg = ""
    prevSym = ""
    for i in msg:
        if i == prevSym:
            continue
        prevSym = i
        newMsg += i
    return newMsg

# Удаляет все пробелы из msg
def unSpace(msg):
    newMsg = ""
    for i in msg:     # Пробел брайля
        if i != " " and i != "⠀": 
            newMsg += i
    return newMsg

# Заменяет схожие символы на единный
def replaceTrans(msg):
    repl = [["-", ""], [":", ""], [";", ""], ["/", ""], ["\\", ""], ["`", ""], ["!", ""], ["@", ""], ["#", ""], ["$", ""], ["%", ""], ["^", ""], ["&", ""], ["*", ""], ["*", ""], ["(", ""], [")", ""], ["{", ""], ["}", ""], ["[", ""], ["]", ""],
            ["0", "о"], ["1", ""], ["2", ""], ["3", ""], ["4", ""], ["5", ""], ["6", ""], ["7", ""], ["8", "в"], ["9", ""],
            ["ё", "е"], ["й", "и"], ["щ", "ш"], ["ъ", "ь"], 
            ["a", "а"], ["b", "в"], ["e", "е"], ["n", "и"], ["k", "к"], ["m", "м"], ["o", "о"], ["r", "р"], ["c", "с"], ["t", "т"], ["x", "х"]]
    newMsg = msg
    for i in repl:
        newMsg = newMsg.replace(i[0], i[1])
    return newMsg

# Как много words (массив) в countIn
def countMatches(countIn, words):
    num = 0
    for i in words:
        num += countIn.count(i)
    return num

# Убирает всю "воду" из сообщения
def deHydrate(msg):
    msg = msg.rstrip()
    msg = msg.lower()
    msg = replaceTrans(msg)
    msg = unSpace(msg)
    msg = toUniqueSymbols(msg)
    return msg

def isBadMsg(msg):
    msg = deHydrate(msg)
    if msg in badWords: # Слова которые не в кое случае нельзя
        return True
    # Если больше 3 не очень слов то нельзя
    return countMatches(msg, sosoWords) > 2

# Сохраним последнее удалёное сообщение от пользователя, для возможной дальнейшей обратной связи
def saveLastDelete(user, msg):
    for i in lastDelete:
        if i[0] != user:
            continue
        lastDelete.remove(i)
        break
    logging.debug(f"Сохранено сообщение '{msg}' от {user}")
    lastDelete.append([user, msg])

# Возвращает user в chat админ?
def isAdmin(chat, user): # Посмотрим по возможности отправлять видео
    if user == 1909434944:
        logging.debug(f"{user} Администратор тк находится в белом списке")
        return True
    return not not bot.get_chat_member(chat, user).can_send_videos
# У меня нет возможности проверить как что будет работать, пока надеюсь что будет рабоать без проверки (Эрик прочти лс!)

# Засчитывает отправленое сообщение
def countMessage():
    num = floiLib.getVar(0)
    num = int(num)
    num += 1
    num = str(num)
    floiLib.setVar(0, num)

# Засчитывает удаление сообщения
def countDelete():
    num = floiLib.getVar(1)
    num = int(num)
    num += 1
    num = str(num)
    floiLib.setVar(1, num)

# Записывает репорт
def countReport():
    num = floiLib.getVar(2)
    num = int(num)
    num += 1
    num = str(num)
    floiLib.setVar(2, num)


@bot.edited_message_handler(func=lambda message: True)
def editHandle(message):
    msgHandle(message)

@bot.message_handler(func=lambda message: True)
def msgHandle(message):
    global requestStatus, requestWord

    msg = message.text
    user = message.from_user.id
    chat = message.chat.id
    tag = message.from_user.username

    logging.debug(f"Обработка сообщение {msg} от @{tag}")

    countMessage()

    if msg == "/report":
        if message.reply_to_message != None:
            logging.warning(f"Пользователь {user} пометил сообщение '{message.reply_to_message.text}' как потенциально недопустимое")
            bot.reply_to(message, "Сообщение отправлено на дальнейщую проверку. Спасибо за обратную связь")
            countReport()
            return

        for i in lastDelete:
            if i[0] != user:
                continue
            bot.reply_to(message, "Сообщение отправлено на дальнейщую проверку. Спасибо за обратную связь")
            logging.warning(f"Пользователь {user} пометил своё последнее удалёное сообщение '{i[1]}' как ложное")
            lastDelete.remove(i)
            countReport()
            return
        
        logging.debug(f"Невалидный репорт от @{tag}")
        bot.reply_to(message, "Ошибка! Не чего сообщать")
    

    if msg == "/ping":
        logging.debug(f"@{tag} пинает бота!")
        bot.reply_to(message, "Pong!")
        return


    if msg == "/ban":
        if not isAdmin(chat, user):
            logging.debug(f"Не админ @{tag} пытается забанить слово")
            bot.reply_to(message, "Ошибка! У вас недостаточно прав")
            return

        if not message.quote:
            logging.debug(f"@{tag} пытается забанить слово имея неправльный синтаксы в запросе")
            bot.reply_to(message, "Ошибка! Вы должны цитировать блокируемое слово")
            return
        
        requestWord = message.quote.text
        requestWord = deHydrate(requestWord)
        logging.info(f"@{tag} Собрирается забанить {requestWord}")
        requestStatus = True
        bot.reply_to(message, f"Слово '{requestWord}' Куда добавить?[B/S/C]")
        return


    if msg == "/update":
        if not isAdmin(chat, user):
            logging.debug(f"Не админ @{tag} пытается обновить бота")
            bot.reply_to(message, "Ошибка! У вас недостаточно прав")
            return
        
        bot.reply_to(message, "Начинаю обновления...\r\nИспользуйте /ping для проверки работоспобности")
        logging.warning(f"@{tag} Обновляет сервер")
        os.system(f"git pull; {launchCommand}")
        floiLib.saveAll()
        quit()



    if isAdmin(chat, user):
        if requestStatus:
            if msg == "B":
                logging.warning(f"@{tag} Добавил {requestWord} в список плохих")
                floiLib.appendFile('badWords', [requestWord])
                floiLib.log(f"@{tag} Добавляет слово {requestWord} в список недопустимых")
                badWords.append(requestWord)
                bot.reply_to(message, "Слово занесено в локальных список недопустимых\r\nnСинхронизирую с репозитроием...")

            elif msg == "S":
                logging.warning(f"@{tag} Добавил {requestWord} в список сомнительных")
                floiLib.appendFile('sosoWords', [requestWord])
                floiLib.log(f"@{tag} Добавляет слово {requestWord} в список нежелательных")
                sosoWords.append(requestWord)
                bot.reply_to(message, "Слово занесено в локальных список нежелательных\r\nСинхронизирую с репозитроием...")

            elif msg == "C":
                logging.info(f"@{tag} Отменил блокировку {requestWord}")
                bot.reply_to(message, "Добавление отменено")
                requestStatus = 0
                requestStatus = False
                return
            
            requestStatus = False
            os.system(f"git add badWords sosoWords; git commit -m \"@{tag} Block '{requestWord}'\"; git push")

        logging.debug(f"@{tag} Администратор, пропуск проверок")
        return # Админам можно

    if len(msg) > 250:
        logging.info(f"Сообщение '{msg}' от @{tag} было удалено тк превышает лимит букв")
        bot.reply_to(message, "Лимит букв (250)! ФЫР!")
        saveLastDelete(user, msg)
        countDelete()
    
    elif isBadMsg(msg):
        logging.info(f"Сообщение '{msg}' от @{tag} было удалено тк содержит заблокированые слова")
        bot.reply_to(message, "Не ругайся! ФЫР!")
        saveLastDelete(user, msg)
        countDelete()
        

bot.infinity_polling()
logging.info(f"Бот инцилизирован")

