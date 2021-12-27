import telebot
import math
from telebot import types

import re

list_of_simple_oper = ["+", "-", "*", "/"]
list_of_hard_oper_one = ["n!", "log10(n)", "10ⁿ", "ln(n)", "√n", "sin(n)", "cos(n)", "tg(n)"]
list_of_hard_oper_two = ["xⁿ"]
bot = telebot.TeleBot("")


@bot.message_handler(commands=["start", "help"])
def start_bot(message):
    if message.text == "/start":
        
        start_msg = f"""Я бот - OVi_calc, инженерный калькулятор со множественным функционалом.\nМогу выполнять простые и сложные вычисления, которые ты мне пришлешь.\nВведи /engcalc"""
        
        bot.send_message(message.from_user.id, "Привет, " + message.from_user.first_name + "!")
        bot.send_message(message.from_user.id, start_msg)
        bot.send_message(message.from_user.id, "Введите простое выражение (+ - / *)")
        
    elif message.text == "/help":
        help_msg = ""
        bot.send_message(message.from_user.id, "Cправка не составлена")

@bot.message_handler(regexp=r"\d+[+-/*]{1}\d+")
def simple_oper(message):
    calculator_operations(message)  
    
    
@bot.message_handler(commands=["engcalc"])
def engineer_oper(message):
    
    choose_msg = f"""Сначала выбери выражение из предложенного списка. Либо напиши отмена"""
    
    markup_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup_choose.add(types.KeyboardButton("xⁿ"))
    for val in list_of_hard_oper_one:
        markup_choose.add(val)
        
    msg = bot.send_message(message.chat.id, choose_msg, reply_markup=markup_choose)
    bot.register_next_step_handler(msg, choose_oper) 



def choose_oper(message):
    global user_oper
    user_oper = message.text.lower()
    markup_choose = types.ReplyKeyboardRemove(selective=True)
    if user_oper == "отмена":
        bot.send_message(message.from_user.id, "Возвращаюсь")
        return
    elif user_oper in list_of_hard_oper_two:
        msg = bot.send_message(message.chat.id, "Введи два числа (x n) через пробел.\n(либо \"отмена\")", reply_markup=markup_choose)
        bot.register_next_step_handler(msg, hard_oper)
    elif user_oper in list_of_hard_oper_one:
        msg = bot.send_message(message.chat.id, "Введи одно число (n).\n(либо \"отмена\")", reply_markup=markup_choose)
        bot.register_next_step_handler(msg, hard_oper)
        
        
     
def hard_oper(message):
    result = list(map(int, message.text.split()))
    if user_oper == "отмена":
        bot.send_message(message.from_user.id, "Возвращаюсь")
        return 
    elif user_oper == list_of_hard_oper_two[0]:
        bot.send_message(message.chat.id, "Результат возведения в степень: " + str(result[0] ** result[1]))    
    elif user_oper == list_of_hard_oper_one[0]:
        bot.send_message(message.chat.id, "Результат факториала: " + str(math.factorial(result[0])))
    elif user_oper == list_of_hard_oper_one[1]:
        bot.send_message(message.chat.id, "Результат логарифма с основанием 10: " + str(math.log10(result[0])))
    elif user_oper == list_of_hard_oper_one[2]:
        bot.send_message(message.chat.id, "Результат 10 в степени: " + str(10 ** result[0]))
    elif user_oper == list_of_hard_oper_one[3]:
        bot.send_message(message.chat.id, "Результат натурального логарифма: " + str(math.log(result[0])))
    elif user_oper == list_of_hard_oper_one[4]:
        bot.send_message(message.chat.id, "Результат извлечения корня: " + str(math.sqrt(result[0])))
    elif user_oper == list_of_hard_oper_one[5]:
        bot.send_message(message.chat.id, "Результат синуса: " + str(math.sin(result[0])))
    elif user_oper == list_of_hard_oper_one[6]:
        bot.send_message(message.chat.id, "Результат косинуса: " + str(math.cos(result[0])))
    elif user_oper == list_of_hard_oper_one[7]:
        bot.send_message(message.chat.id, "Результат тангенса: " + str(math.tan(result[0])))

        
def calculator_operations(message):
    user_oper = message.text
    if user_oper.lower() == "отмена":
        bot.send_message(message.from_user.id, "Возвращаюсь")
        return

    else:
        expression = user_oper.split()
        symbol = define_simple_symbol(expression)
        numberA, numberB = re.findall(r'\d+', ''.join(expression))
        numberA = int(numberA)
        numberB = int(numberB)
        result = 0
        if symbol == '+':
            result = numberA + numberB
        elif symbol == '-':
            result = numberA - numberB
        elif symbol == '/':
            if numberB != 0:
                result = numberA / numberB
            else:
                bot.send_message(message.from_user.id, "На ноль делить нельзя!") 
        elif symbol == '*':
            result = numberA * numberB
        else:
            bot.send_message(message.from_user.id, "Ошибка")
        bot.send_message(message.from_user.id, "Результат вычисления:")
        bot.send_message(message.from_user.id, result)

        
def define_simple_symbol(phrase):
    symbol_oper = re.findall(r'\D', ''.join(phrase))
    return symbol_oper[0]            
        
bot.polling(none_stop=True, interval=0)