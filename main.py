import telebot
from telebot import types
from Chave import CHAVE_API
import Palavras
import Arquivo
import Api
import Database

bot = telebot.TeleBot(CHAVE_API)


@bot.message_handler(commands=['start'])
def principal(msg):
    bot.send_message(msg.chat.id, "Olá, aqui é o ZECABOT! Chique e bacanizado?")
    keyboard = types.ReplyKeyboardMarkup(row_width=3)
    api_button = types.KeyboardButton('API')
    menu_button = types.KeyboardButton('MENU')
    foto_button = types.KeyboardButton('FOTO')
    keyboard.add(api_button, menu_button, foto_button)
    bot.send_message(msg.chat.id, 'Selecione uma opção', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'API')
def redirecionar_api(message):
    Api.iniciar_api(message)


@bot.message_handler(func=lambda message: message.text == 'MENU')
def redirecionar_menu(message):
    Arquivo.menu_aluno(message)


@bot.message_handler(func=lambda message: message.text == 'FOTO')
def redirecionar_foto(message):
    Database.usuario(message)


@bot.message_handler(func=lambda message: message.text.lower() in Palavras.lista)
def verificar(msg):
    bot.send_message(msg.chat.id, "Olá, você não pode falar estas coisas aqui.")


# Chamar as funções dos três pacotes para fazer com que o loop (bot.polling()) seja controlado pelo arquivo main.
Api.chatbot_apis(bot)
Arquivo.chatbot_arquivo(bot)
Database.chatbot_fotos(bot)

bot.polling()

