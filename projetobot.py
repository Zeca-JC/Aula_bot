import telebot
import mysql.connector
from mysql.connector import Error
from telebot import types

# Conexão com o banco de dados MySQL
connection = mysql.connector.connect(
    host='localhost',
    database='seu_banco_de_dados',
    user='seu_usuario',
    password='sua_senha'
)

# Criação da tabela no banco de dados, caso ainda não exista
create_table_query = """
CREATE TABLE IF NOT EXISTS musicas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    banda VARCHAR(255),
    musica VARCHAR(255),
    capa LONGBLOB
);
"""
cursor = connection.cursor()
cursor.execute(create_table_query)
connection.commit()

# Inicialização do bot
bot_token = 'seu_token'
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('/start')
    itembtn2 = types.KeyboardButton('Listar bandas')
    itembtn3 = types.KeyboardButton('Listar Música')
    itembtn4 = types.KeyboardButton('Adicionar Música')
    markup.add(itembtn2, itembtn3, itembtn4)
    bot.reply_to(message, "Bem-vindo ao Chatbot de Músicas!", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'Listar bandas':
        listar_bandas(message)
    elif message.text == 'Listar Música':
        listar_musicas_por_banda(message)
    elif message.text == 'Adicionar Música':
        bot.reply_to(message, "Digite o nome da música:")
        bot.register_next_step_handler(message, solicitar_nome_musica)


def listar_bandas(message):
    try:
        query = "SELECT banda, capa FROM musicas GROUP BY banda"
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            banda, capa = row
            bot.send_photo(message.chat.id, capa, caption=banda)
    except Error as e:
        bot.reply_to(message, "Ocorreu um erro ao listar as bandas.")
        print(e)


def listar_musicas_por_banda(message):
    try:
        query = "SELECT banda FROM musicas GROUP BY banda"
        cursor.execute(query)
        rows = cursor.fetchall()

        markup = types.ReplyKeyboardMarkup(row_width=1)
        for row in rows:
            banda = row[0]
            markup.add(types.KeyboardButton(banda))

        bot.reply_to(message, "Selecione a banda:", reply_markup=markup)
        bot.register_next_step_handler(message, listar_musicas)
    except Error as e:
        bot.reply_to(message, "Ocorreu um erro ao listar as músicas.")
        print(e)

def listar_musicas(message):
    banda_selecionada = message.text
    try:
        query = "SELECT musica FROM musicas WHERE banda = %s"
        cursor.execute(query, (banda_selecionada,))
        rows = cursor.fetchall()

        for row in rows:
            bot.reply_to(message, row[0])
    except Error as e:
        bot.reply_to(message, "Ocorreu um erro ao listar as músicas.")
        print(e)


def solicitar_nome_musica(message):
    chat_id = message.chat.id
    nome_musica = message.text
    bot.reply_to(message, "Digite o nome da banda:")
    bot.register_next_step_handler(message, solicitar_nome_banda, nome_musica)


def solicitar_nome_banda(message, nome_musica):
    chat_id = message.chat.id
    nome_banda = message.text
    bot.reply_to(message, "Envie a imagem da capa:")
    bot.register_next_step_handler(message, salvar_musica, nome_musica, nome_banda)


def salvar_musica(message, nome_musica, nome_banda):
    chat_id = message.chat.id
    capa = message.photo[-1].file_id
    file_info = bot.get_file(capa)
    downloaded_file = bot.download_file(file_info.file_path)

    try:
        insert_query = "INSERT INTO musicas (banda, musica, capa) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (nome_banda, nome_musica, downloaded_file))
        connection.commit()
        bot.reply_to(message, "Música adicionada com sucesso!")
    except Error as e:
        bot.reply_to(message, "Ocorreu um erro ao adicionar a música.")
        print(e)


bot.polling()
