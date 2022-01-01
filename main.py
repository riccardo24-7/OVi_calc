import telebot
import math
from telebot import types


list_of_simple_oper = ["+", "-", "*", "/"]

operations_one_num = {
    "n!": math.factorial,
    "log10(n)": math.log10,
    "ln(n)": math.log,
    "√n": math.sqrt,
    "sin(n)": math.sin, 
    "cos(n)": math.cos, 
    "tg(n)": math.tan   
}

operations_two_num = {
    "xⁿ"
}


bot = telebot.TeleBot("")


@bot.message_handler(commands=["start", "help"])
def start_bot(message):
    if message.text == "/start":
        
        start_msg = f"""Я бот - OVi_calc, инженерный калькулятор со множественным функционалом.\nМогу выполнять простые и сложные вычисления, которые ты мне пришлешь.\nВведи /engcalc"""
        
        bot.send_message(message.from_user.id, "Привет, " + message.from_user.first_name + "!")
        bot.send_message(message.from_user.id, start_msg)
        
    elif message.text == "/help":
        help_msg = ""
        bot.send_message(message.from_user.id, "Cправка не составлена")



@bot.message_handler(commands="calc")
def calc(message):
    markup_choose = types.ReplyKeyboardRemove(selective=True)
    msg = bot.send_message(message.chat.id, "Введите выражение", reply_markup = markup_choose)
    bot.register_next_step_handler(msg, result_calc) 

def result_calc(message):
    user_oper = message.text.lower()

    if user_oper == "==":
        bot.send_message(message.from_user.id, "Возвращаюсь")
        return
    else:
        bot.send_message(message.chat.id, eval_expression(user_oper))

def eval_expression(input_string):
    
    allowed_names = {
        "ln":    math.log,
        "sqrt":  math.sqrt,
        "log10": math.log10,
        "fact":  math.factorial,
        "sin":   math.sin,
        "cos":   math.cos,
        "tg":    math.tan
        }   
    code = compile(input_string, "<string>", "eval")  
    for name in code.co_names:
        if name not in allowed_names:
            raise NameError("Not allowed")
    return eval(code, {"__builtins__": {}}, allowed_names) 
    
    
    
@bot.message_handler(commands=["keycalc"])
def engineer_oper(message):
    
    choose_msg = f"""Сначала выбери выражение из предложенного списка. Либо напиши "==" для отмены"""
    
    markup_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup_choose.add(types.KeyboardButton("xⁿ"), types.KeyboardButton("n!"),types.KeyboardButton("log10(n)"),
                      types.KeyboardButton("ln(n)"),types.KeyboardButton("√n"), types.KeyboardButton("sin(n)"), 
                      types.KeyboardButton("cos(n)"),types.KeyboardButton("tg(n)"))
    
    msg = bot.send_message(message.chat.id, choose_msg, reply_markup=markup_choose)
    bot.register_next_step_handler(msg, choose_oper) 
    
    
def choose_oper(message):
    
    global user_oper
    user_oper = message.text.lower()
    markup_choose = types.ReplyKeyboardRemove(selective=True)
    if user_oper == "==":
        bot.send_message(message.from_user.id, "Возвращаюсь", reply_markup= markup_choose)
        return
    elif user_oper in operations_two_num:
        msg = bot.send_message(message.chat.id, "Введи два числа (x n) через пробел.\n(либо \"==\" для отмены)", reply_markup=markup_choose)
        bot.register_next_step_handler(msg, hard_oper)
    elif user_oper in operations_one_num:
        msg = bot.send_message(message.chat.id, "Введи одно число (n).\n(либо \"==\" для отмены)", reply_markup=markup_choose)
        bot.register_next_step_handler(msg, hard_oper)
        
        
     
def hard_oper(message):
    result = list(map(int, message.text.split()))
    calculation = ""
    if user_oper == "==":
        bot.send_message(message.from_user.id, "Возвращаюсь")
        return
    elif user_oper in operations_two_num:
        calculation = str(result[0] ** result[1])
        
    elif user_oper in operations_one_num:
        operation = operations_one_num.get(user_oper)
        calculation = str(operation(result[0]))


    bot.send_message(message.chat.id, "Результат вычисления " + user_oper + " = " + calculation)
    bot.send_message(message.chat.id, "/keycalc")        
 
               
bot.polling(none_stop=True, interval=0)