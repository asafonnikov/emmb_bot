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

def isBadMsg(msg):
    msg = msg.rstrip()
    msg = msg.lower()
    msg = replaceTrans(msg)
    msg = unSpace(msg)
    msg = toUniqueSymbols(msg)
    return msg in badWords

@bot.message_handler(func=lambda m: True)
def msgHandle(message):
    msg = message.text
    user = message.from_user.id

    if msg.startswith("/report"):
        floiLog.log(f"Пользователь {user} оставил сообщение {msg}")
        bot.reply_to(message, "Обратная связь отправлена. Спасибо за обратную связь")
    
    if len(msg) > 100:
        floiLog.log(f"ДЛИННОЕ {user}: {message.text}")
        bot.reply_to(message, "Сообщение сочтено потенциально не допустимым, тк является слишком длинное")
    elif isBadMsg(msg):
        floiLog.log(f"НЕНОРМАТИВНОЕ {user}: {message.text}")
        bot.reply_to(message, "Сообщение сочтено потенциально не допустимым, тк содержит ненормативную лексику")


bot.infinity_polling()

