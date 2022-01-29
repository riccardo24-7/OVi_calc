import telebot
import math
from telebot import types
import re
import numpy as np
from config.config import TOKEN_BOT


bot = telebot.TeleBot(TOKEN_BOT)


@bot.message_handler(commands=["start", "help"])
def start_bot(message):
    user = message.from_user
    cid = message.chat.id
    if message.text == "/start":
        
        start_msg = f"""Я бот - OVi_calc, инженерный калькулятор со множественным функционалом.\nМогу выполнять простые и сложные вычисления, которые ты мне пришлешь.\nВведи /calc или /keycalc"""
        
        bot.send_message(cid, "Привет, " + user.first_name + "!")
        bot.send_message(cid, start_msg)
        
    elif message.text == "/help":
        help_msg = f"""Этот калькулятор способен производить рассчеты разной сложности"""
        bot.send_message(cid, "Cправка не составлена")



@bot.message_handler(commands="calc")
def command_calc(message):
    cid = message.chat.id
    markup_close = types.ReplyKeyboardRemove(selective=True)
    msg = bot.send_message(cid, "Введите выражение. \n(либо \"==\" для отмены)", reply_markup = markup_close)
    bot.register_next_step_handler(msg, calc_expression) 

def calc_expression(message):
    cid = message.chat.id
    calc_oper = message.text.lower()

    if calc_oper == "==":
        bot.send_message(cid, "Возвращаюсь")
        return
    else:
        result_calc = eval_expression(calc_oper, message, cid, command_calc)
        
        calc_inline_keyboard = types.InlineKeyboardMarkup()

        if isinstance(result_calc, float):           
            key_one = types.InlineKeyboardButton(text='Округлить до 2-x знаков', callback_data='round_two')
            key_two = types.InlineKeyboardButton(text='Округлить до 3-х знаков', callback_data='round_three')
            calc_inline_keyboard.add(key_one, key_two) 
        
        bot.send_message(cid, "Результат вычисления " + calc_oper + " = " + "<code>" + str(result_calc) + "</code>", parse_mode="HTML", reply_markup=calc_inline_keyboard)
        command_calc(message)


def eval_expression(input_string, message, cid, oper_calc):
    global result
    allowed_names = {
        "ln":    math.log,
        "sqrt":  math.sqrt,
        "log10": math.log10,
        "factorial":  math.factorial,
        "sin":   math.sin,
        "cos":   math.cos,
        "tg":    math.tan
        }
    try:   
        code = compile(input_string, "<string>", "eval")  
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError("Not allowed")
        result = eval(code, {"__builtins__": {}}, allowed_names)
    except SyntaxError as synerr:
        bot.send_message(cid, "У Вас синтаксическая ошибка, либо такой функции я не знаю, попробуйте ещё раз")
        oper_calc(message)
    except TypeError as typeerr:
        bot.send_message(cid, "Нецелочисленные значения лучше указывать через точку, попробуйте ещё раз")
        oper_calc(message)        
        
        
    return result
    
    
    
@bot.message_handler(commands=["keycalc"])
def command_keycalc(message):
    cid = message.chat.id
    choose_msg = f"""Сначала выбери выражение из предложенного списка. \n(либо \"==\" для отмены)"""
    markup_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup_choose.add(types.KeyboardButton("xⁿ"), types.KeyboardButton("factorial(n)"),types.KeyboardButton("log10(n)"),
                    types.KeyboardButton("ln(n)"),types.KeyboardButton("sqrt(n)"), types.KeyboardButton("sin(n)"), 
                    types.KeyboardButton("cos(n)"),types.KeyboardButton("tg(n)"))
    msg = bot.send_message(cid, choose_msg, reply_markup=markup_choose)
    bot.register_next_step_handler(msg, keycalc_enter) 
    
    
def keycalc_enter(message):
    cid = message.chat.id
    keycalc_oper = message.text.lower()
    markup_close = types.ReplyKeyboardRemove(selective=True)
    
    if keycalc_oper == "==":
        bot.send_message(cid, "Возвращаюсь", reply_markup= markup_close)
        return

    text_msg = f"Введи одно число (n).\n(либо \"==\" для отмены)"
    if keycalc_oper == "xⁿ":
        keycalc_oper = "x**n"
        text_msg = f"Введи два числа (x n) через пробел.\n(либо \"==\" для отмены)"
        
    msg = bot.send_message(cid, text_msg, reply_markup=markup_close)     
    bot.register_next_step_handler(msg, keycalc_pattern, keycalc_oper)
        
        
     
def keycalc_pattern(message, keycalc_oper):
    cid = message.chat.id
    text = message.text
    markup_close = types.ReplyKeyboardRemove(selective=True)
    angle = ""
        
    if text == "==":
        bot.send_message(cid, "Возвращаюсь", reply_markup= markup_close)
        return
    

    text = re.sub(r"\([n]\)", "(" + text + ")", keycalc_oper)
    if keycalc_oper == "x**n":
        list_text = text.split(" ")
        text = re.sub(r"[x]", list_text[0], keycalc_oper)
        text = re.sub(r"[n]+", list_text[1], text)
    
    result_keycalc = eval_expression(text, message, cid, command_keycalc)
    
    if keycalc_oper in ["sin(n)", "cos(n)", "tg(n)"]:
        angle = "rad" 
        
    keycalc_inline_keyboard = types.InlineKeyboardMarkup()

    if isinstance(result_keycalc, float):           
        key_one = types.InlineKeyboardButton(text='Округлить до 2-x знаков', callback_data='round_two')
        key_two = types.InlineKeyboardButton(text='Округлить до 3-х знаков', callback_data='round_three')
        keycalc_inline_keyboard.add(key_one, key_two) 
        
       
          

    str_keycalc = "Результат вычисления " + keycalc_oper + " = " + "<code>" + str(result_keycalc) + "</code> " + angle
    
    bot.send_message(cid, str_keycalc, parse_mode = "HTML", reply_markup = keycalc_inline_keyboard)
    command_keycalc(message)       
 


@bot.message_handler(commands=["onematrix"])
def command_onematrix(message):
    cid = message.chat.id
    choose_msg = f"""Введите матрицу первую матрицу. \n(либо \"==\" для отмены)"""
    msg = bot.send_message(cid, choose_msg)
    bot.register_next_step_handler(msg, onematrix_input)
    

def onematrix_input(message):
    cid = message.chat.id
    text = message.text
    if text == "==":
        bot.send_message(cid, "Возвращаюсь")
        return

    tes = [val.split(",") for val in text.split("\n")]
    new_tes = [list(map(int, tes[idx])) for idx in range(0, len(tes))]
    arr_one = np.array(new_tes, int)
    markup_one_matrix = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup_one_matrix.add(types.KeyboardButton("Транспонировать"), types.KeyboardButton("Найти определитель"),
                            types.KeyboardButton("Обратная матрица"),types.KeyboardButton("Среднее арифметическое"),
                            types.KeyboardButton("Собственный вектор"), types.KeyboardButton("Отмена"))

    msg = f"""Матрица размером {arr_one.shape}:\n{arr_one}\n Какие операции выполнить над ней?"""
    bot_msg = bot.send_message(cid, msg, reply_markup=markup_one_matrix)
    bot.register_next_step_handler(bot_msg, onematrix_oper, arr_one)

def onematrix_oper(message, arr_one):
    cid = message.chat.id
    text = message.text
    oper_arr = arr_one.copy()
    
    if text == "Отмена": 
        bot.send_message(cid, "Возвращаюсь", reply_markup=types.ReplyKeyboardRemove(selective=True))
        return
        
    elif text == "Транспонировать":      
        result_arr = oper_arr.transpose()
        msg = f"""Транспонированная матрица размером {result_arr.shape}:\n{result_arr}"""
        bot.send_message(cid, msg, reply_markup=types.ReplyKeyboardRemove(selective=True))
        
    elif text == "Найти определитель":
        result_arr = np.linalg.det(oper_arr)
        msg = f"""Определитель матрицы:\n{oper_arr}\nРавняется - {result_arr}"""
        bot.send_message(cid, msg, reply_markup=types.ReplyKeyboardRemove(selective=True))
        
    elif text == "Обратная матрица":
        result_arr = np.linalg.inv(oper_arr)
        msg = f"""Обратная матрица размером {result_arr.shape}:\n{result_arr}"""
        bot.send_message(cid, msg, reply_markup=types.ReplyKeyboardRemove(selective=True))
        
    elif text == "Среднее арифметическое":
        result_arr = oper_arr.mean()
        msg = f"""Среднее арифметическое матрицы:\n{oper_arr}\nРавняется - {result_arr}"""
        bot.send_message(cid, msg, reply_markup=types.ReplyKeyboardRemove(selective=True))
        
    elif text == "Собственный вектор":
        result_arr, vecs = np.linalg.eig(oper_arr)
        msg = f"""Собственный вектор матрицы:\n{oper_arr}\nРавняется - {result_arr}"""
        bot.send_message(cid, msg, reply_markup=types.ReplyKeyboardRemove(selective=True))

    

@bot.callback_query_handler(func=lambda call: True)
def callbackFunction(call):
    
    user = call.from_user.id
    message_id =  call.message.message_id
    markup = call.message.reply_markup
    text = call.message.text
    split_call = re.split(r" = ", text)
    call_oper = re.findall(r"[^А-я ]+\w+\W+\w*\b",split_call[0])[0]
    call_angle = "rad"
    
    if call.data == "round_two":
        
        result_calculation = "Результат округления выражения " + call_oper + " = " + "<code>" + str(round(result,2)) + "</code>" + " <b>" + call_angle + "</b>"
        bot.edit_message_text(result_calculation,user,message_id, parse_mode="HTML", reply_markup=markup)
    
    elif call.data == "round_three":

        result_calculation = "Результат округления выражения " + call_oper + " = " + "<code>" + str(round(result,3)) + "</code>" + " <b>" + call_angle + "</b>"  
        bot.edit_message_text(result_calculation,user, message_id, parse_mode="HTML", reply_markup=markup)


           
bot.polling(none_stop=True, interval=0)