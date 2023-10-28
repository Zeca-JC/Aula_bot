import telebot
from telebot import types
from Chave import CHAVE_API

bot = telebot.TeleBot(CHAVE_API)


@bot.message_handler(func=lambda message: message.text == 'MENU')
def menu_aluno(message):
    keyboard = types.InlineKeyboardMarkup()
    arquivo_button = types.InlineKeyboardButton(text='Arquivo', callback_data='arquivo')
    ler_arquivo_button = types.InlineKeyboardButton(text='Listar Arquivo', callback_data='ler_arquivo')
    keyboard.add(arquivo_button, ler_arquivo_button)
    bot.send_message(message.chat.id, 'Você clicou no MENU', reply_markup=keyboard)


def chatbot_arquivo(bot):
    @bot.callback_query_handler(func=lambda call: call.data == 'arquivo')
    def callback_arquivo(call):
        arquivo(call.message)
        # arquivo(call.message, bot)

    @bot.message_handler(func=lambda message: message.text == 'Arquivo')
    def arquivo(message):
        bot.send_message(message.chat.id, 'Digite o nome do aluno:')
        bot.register_next_step_handler(message, obter_nome)

    def obter_nome(message):
        nome_aluno = message.text
        bot.send_message(message.chat.id, 'Digite o curso do aluno:')
        bot.register_next_step_handler(message, lambda msg: obter_curso(msg, nome_aluno))

    def obter_curso(message, nome_aluno):
        curso_aluno = message.text
        with open("alunos.txt", "a") as arquivo:
            arquivo.write(f"Nome: {nome_aluno} - Curso: {curso_aluno}\n")
        bot.send_message(message.chat.id, "Aluno registrado com sucesso!")

    @bot.callback_query_handler(func=lambda call: call.data == 'ler_arquivo')
    def callback_ler_arquivo(call):
        ler_arquivo(call.message)

    def ler_arquivo(message):
        try:
            with open("alunos.txt", "r") as arquivo:
                conteudo = arquivo.read()
            if conteudo:
                bot.send_message(message.chat.id, conteudo)
            else:
                bot.send_message(message.chat.id, "O arquivo está vazio.")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "O arquivo não existe.")


