import telebot, floiLib, os

floiLib.init("v16")

# Сам бот
botToken = floiLib.readFile("../botToken")[0].rstrip()
bot = telebot.TeleBot(botToken)

# Плохие слова
badWords = floiLib.readFile("badWords")
badWords = [i.rstrip() for i in badWords]

# Такие себе слова, не много можно
sosoWords = floiLib.readFile("sosoWords")
sosoWords = [i.rstrip() for i in sosoWords]

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
    lastDelete.append([user, msg])

# Возвращает user в chat админ?
def isAdmin(chat, user): # Посмотрим по возможности отправлять видео
    return True # TODO TODO TODO УДАЛИТЬ
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

    countMessage()

    if msg == "/report":
        if message.reply_to_message != None:
            floiLib.log(f"Пользователь {user} пометил сообщение '{message.reply_to_message.text}' как потенциально недопустимое")
            bot.reply_to(message, "Сообщение отправлено на дальнейщую проверку. Спасибо за обратную связь")
            countReport()
            return

        for i in lastDelete:
            if i[0] != user:
                continue
            bot.reply_to(message, "Сообщение отправлено на дальнейщую проверку. Спасибо за обратную связь")
            floiLib.log(f"Пользователь {user} пометил своё последнее удалёное сообщение '{i[1]}' как ложное")
            lastDelete.remove(i)
            countReport()
            return
        


        bot.reply_to(message, "Ошибка! Не чего сообщать")
    

    if msg == "/ban":
        if not isAdmin(chat, user):
            bot.reply_to(message, "Ошибка! У вас недостаточно прав")
            return

        if not message.quote:
            bot.reply_to(message, "Ошибка! Вы должны цитировать блокируемое слово")
            return
        
        requestWord = message.quote.text
        requestWord = deHydrate(requestWord)
        requestStatus = True
        bot.reply_to(message, f"Слово '{requestWord}' Куда добавить?[B/S/C]")
        return


    if isAdmin(chat, user):
        if requestStatus:
            if msg == "B":
                floiLib.appendFile('badWords', [requestWord])
                floiLib.log(f"@{tag} Добавляет слово {requestWord} в список недопустимых")
                badWords.append(requestWord)
                bot.reply_to(message, "Слово занесено в локальных список недопустимых\r\nИдет синхронизация с репозитроием...")
                requestStatus = False

            elif msg == "S":
                floiLib.appendFile('sosoWords', [requestWord])
                floiLib.log(f"@{tag} Добавляет слово {requestWord} в список нежелательных")
                sosoWords.append(requestWord)
                bot.reply_to(message, "Слово занесено в локальных список нежелательных\r\nИдет синхронизация с репозитроием...")
                requestStatus = False

            elif msg == "C":
                bot.reply_to(message, "Добавление отменено")
                requestStatus = 0
                requestStatus = False
                return
            
            try:
                os.system


        return # Админам можно

    if len(msg) > 250:
        floiLib.log(f"ДЛИННОЕ {user}: {msg}")
        bot.reply_to(message, "Лимит букв (250)! ФЫР!")
        saveLastDelete(user, msg)
        countDelete()
    
    elif isBadMsg(msg):
        floiLib.log(f"НЕНОРМАТИВНОЕ {user}: {msg}")
        bot.reply_to(message, "Не ругайся! ФЫР!")
        saveLastDelete(user, msg)
        countDelete()
        

bot.infinity_polling()

