import telebot
import math
from telebot import types
import re
import numpy as np

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
    user = message.from_user
    cid = message.chat.id
    if message.text == "/start":
        
        start_msg = f"""Я бот - OVi_calc, инженерный калькулятор со множественным функционалом.\nМогу выполнять простые и сложные вычисления, которые ты мне пришлешь.\nВведи /calc или /keycalc"""
        
        bot.send_message(cid, "Привет, " + user.first_name + "!")
        bot.send_message(cid, start_msg)
        
    elif message.text == "/help":
        help_msg = ""
        bot.send_message(cid, "Cправка не составлена")



@bot.message_handler(commands="calc")
def calc(message):
    cid = message.chat.id
    markup_close = types.ReplyKeyboardRemove(selective=True)
    msg = bot.send_message(cid, "Введите выражение. \n(либо \"==\" для отмены)", reply_markup = markup_close)
    bot.register_next_step_handler(msg, result_calc) 

def result_calc(message):
    cid = message.chat.id
    user_oper = message.text.lower()

    if user_oper == "==":
        bot.send_message(cid, "Возвращаюсь")
        return
    else:
        bot.send_message(cid, "Результат вычисления " + user_oper + " = " + "<code>" + str(eval_expression(user_oper)) + "</code>")
        calc(message)


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
    cid = message.chat.id
    choose_msg = f"""Сначала выбери выражение из предложенного списка. \n(либо \"==\" для отмены)"""
    markup_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup_choose.add(types.KeyboardButton("xⁿ"), types.KeyboardButton("n!"),types.KeyboardButton("log10(n)"),
                    types.KeyboardButton("ln(n)"),types.KeyboardButton("√n"), types.KeyboardButton("sin(n)"), 
                    types.KeyboardButton("cos(n)"),types.KeyboardButton("tg(n)"))
    msg = bot.send_message(cid, choose_msg, reply_markup=markup_choose)
    bot.register_next_step_handler(msg, choose_oper) 
    
    
def choose_oper(message):
    cid = message.chat.id
    global user_oper
    user_oper = message.text.lower()
    markup_close = types.ReplyKeyboardRemove(selective=True)
    if user_oper == "==":
        bot.send_message(cid, "Возвращаюсь", reply_markup= markup_close)
        return
    elif user_oper in operations_two_num:
        
        msg = bot.send_message(cid, "Введи два числа (x n) через пробел.\n(либо \"==\" для отмены)", reply_markup=markup_close)
        bot.register_next_step_handler(msg, hard_oper)
    elif user_oper in operations_one_num:
        msg = bot.send_message(cid, "Введи одно число (n).\n(либо \"==\" для отмены)", reply_markup=markup_close)       
        bot.register_next_step_handler(msg, hard_oper)
        
        
     
def hard_oper(message):
    cid = message.chat.id
    markup_close = types.ReplyKeyboardRemove(selective=True)
    angle = ""
    
    if message.text == "==":
        bot.send_message(cid, "Возвращаюсь", reply_markup= markup_close)
        return
    else:
        result = list(map(int, message.text.split()))
        calculation = ""
        if user_oper in operations_two_num:
            calculation = str(result[0] ** result[1])
        
        elif user_oper in operations_one_num:
            global operation
            operation = operations_one_num.get(user_oper)
            global result_calc
            global perem
            perem = result[0]
            result_calc = operation(result[0])
            if operation.__name__ in ["sin", "cos", "tan"]:
                angle = "rad"
                calculation = "<code>" + str(result_calc) + "</code>" + " <b>" + angle + "</b>"
            else:
                calculation = "<code>" + str(result_calc) + "</code>"
    
    keyboard_result = types.InlineKeyboardMarkup()

    if isinstance(result_calc, float):           
        key_one = types.InlineKeyboardButton(text='Округлить до 1 знака', callback_data='round_one')
        key_two = types.InlineKeyboardButton(text='Округлить до 2 знаков', callback_data='round_two')
        keyboard_result.add(key_one, key_two)
    
    if angle == "rad":
        key_angle = types.InlineKeyboardButton(text='Перевести в градусы', callback_data='degree_change')
        keyboard_result.add(key_angle)
     
    result_calculation = "Результат вычисления " + user_oper + " = " + calculation 
    bot.send_message(cid, result_calculation, parse_mode="HTML", reply_markup=keyboard_result)
    engineer_oper(message)       
 


@bot.message_handler(commands=["onematrix"])
def engineer_oper(message):
    cid = message.chat.id
    text = message.text
    choose_msg = f"""Введите матрицу первую матрицу. \n(либо \"==\" для отмены)"""
    msg = bot.send_message(cid, choose_msg)
    bot.register_next_step_handler(msg, matrix_oper)
    

def matrix_oper(message):
    cid = message.chat.id
    text = message.text
    if message.text == "==":
        bot.send_message(cid, "Возвращаюсь")
        return
    else:
        tes = [val.split(",") for val in text.split("\n")]
        new_tes = [list(map(int, tes[idx])) for idx in range(0, len(tes))]

        arr_test = np.array(new_tes, int)
    
        bot.send_message(cid, f"""Матрица размером {arr_test.shape}:\n{arr_test}\n Какие операции выполнить над ней?""")

    

@bot.callback_query_handler(func=lambda call: True)
def callbackFunction(call):
    
    user = call.from_user.id
    message_id =  call.message.message_id
    markup = call.message.reply_markup
    calc = result_calc
    call_angle = "rad"
    
    if call.data == "round_one":
        
        result_calculation = "Результат вычисления " + user_oper + " = " + "<code>" + str(round(calc,1)) + "</code>" + " <b>" + call_angle + "</b>"
        bot.edit_message_text(result_calculation,user,message_id, parse_mode="HTML", reply_markup=markup)
    
    elif call.data == "round_two":
        
        result_calculation = "Результат вычисления " + user_oper + " = " + "<code>" + str(round(calc,2)) + "</code>" + " <b>" + call_angle + "</b>"  
        bot.edit_message_text(result_calculation,user, message_id, parse_mode="HTML", reply_markup=markup)
    
    
    elif call.data == "degree_change":
        
        call_angle = "deg"
        calc = operation(perem*math.pi/180)
        result_calculation = "Результат вычисления " + user_oper + " = " + "<code>" + str(calc) + "</code>" + " <b>" + call_angle + "</b>"
        markup.keyboard[1][0].callback_data = 'radians_change'
        markup.keyboard[1][0].text = 'Перевести в радианы'
        bot.edit_message_text(result_calculation,user, message_id, parse_mode="HTML",  reply_markup=markup)
        
    elif call.data == "radians_change":
        
        call_angle = "rad"
        calc = operation(perem)
        result_calculation = "Результат вычисления " + user_oper + " = " + "<code>" + str(calc) + "</code>" + " <b>" + call_angle + "</b>"
        markup.keyboard[1][0].callback_data = 'degree_change'
        markup.keyboard[1][0].text = 'Перевести в градусы'
        bot.edit_message_text(result_calculation,user, message_id, parse_mode="HTML", reply_markup=markup) 


           
bot.polling(none_stop=True, interval=0)