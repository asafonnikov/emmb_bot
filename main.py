import telebot, floiLog

def readFile(path):
    f = open(path, 'r')
    try:
        return f.readlines()
    finally:
        f.close()

# Сам бот
botToken = readFile("../botToken")[0]
bot = telebot.TeleBot(botToken)

# Плохие слова
badWords = readFile("badWords")
badWords = [i.rstrip() for i in badWords]

# Такие себе слова, не много можно
sosoWords = readFile("sosoWords")
sosoWords = [i.rstrip() for i in sosoWords]

# Последнии удаления пользователя
lastDelete = []

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

def isBadMsg(msg):
    msg = msg.rstrip()
    msg = msg.lower()
    msg = replaceTrans(msg)
    msg = unSpace(msg)
    msg = toUniqueSymbols(msg)
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

@bot.message_handler(func=lambda m: True)
def msgHandle(message):
    msg = message.text
    user = message.from_user.id

    if msg.startswith("/report"):
        if message.reply_to_message == None:
            for i in lastDelete:
                if i[0] != user:
                    continue
                bot.reply_to(message, "Последнее удаленое сообщение от вас помечено как ложное. Спасибо за обратную связь")
                floiLog.log(f"Пользователь {user} пометил своё последнее удалёное сообщение '{i[1]}' как ложное")
                return
            
            bot.reply_to(message, "Ошибка! Ни одно ваше сообщение не было удалено")
            return
        
        floiLog.log(f"Пользователь {user} пометил сообщение '{message.reply_to_message.text}' как потенциально недопустимое")
        bot.reply_to(message, "Сообщение отправлено на дальнейщую проверку. Спасибо за обратную связь")
    
    if len(msg) > 100:
        floiLog.log(f"ДЛИННОЕ {user}: {message.text}")
        bot.reply_to(message, "Сообщение сочтено потенциально не допустимым, тк является слишком длинное")
        saveLastDelete(user, msg)
    
    elif isBadMsg(msg):
        floiLog.log(f"НЕНОРМАТИВНОЕ {user}: {message.text}")
        bot.reply_to(message, "Сообщение сочтено потенциально не допустимым, тк содержит ненормативную лексику")
        saveLastDelete(user, msg)
        

bot.infinity_polling()

