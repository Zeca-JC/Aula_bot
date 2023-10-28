import telebot
import psycopg2
from telebot import types
from io import BytesIO
from Chave import CHAVE_API

bot = telebot.TeleBot(CHAVE_API)


def conectar_bd():
    conn = psycopg2.connect(
        host="localhost",
        database="chatbot",
        user="postgres",
        password="postgres123"
    )
    return conn


@bot.message_handler(func=lambda message: message.text == 'FOTO')
def usuario(message):
    keyboard = types.InlineKeyboardMarkup()
    adicionar_button = types.InlineKeyboardButton(text='Adicionar', callback_data='adicionar')
    exibir_button = types.InlineKeyboardButton(text='Exibir', callback_data='exibir')
    keyboard.add(adicionar_button, exibir_button)
    bot.send_message(message.chat.id, 'Você clicou no Cadastro de Fotos. Escolha uma Opção!', reply_markup=keyboard)


def chatbot_fotos(bot):
    @bot.callback_query_handler(func=lambda call: call.data == 'adicionar')
    def callback_adicionar(call):
        adicionar_usuario(call.message)

    @bot.message_handler(func=lambda message: message.text == 'Adicionar')
    def adicionar_usuario(message):
        bot.send_message(message.chat.id, "Digite o nome do usuário:")
        bot.register_next_step_handler(message, lambda msg: obter_nome(msg, message))

    def obter_nome(message, original_message):
        nome = message.text
        bot.send_message(message.chat.id, "Envie a imagem do usuário:")
        bot.register_next_step_handler(message, lambda msg: obter_imagem(msg, nome, original_message))

    def obter_imagem(message, nome, original_message):
        imagem = message.photo[-1].file_id
        file_info = bot.get_file(imagem)
        downloaded_file = bot.download_file(file_info.file_path)
        imagem_io = BytesIO(downloaded_file)

        try:
            conn = conectar_bd()
            cur = conn.cursor()
            cur.execute("INSERT INTO usuarios (nome, imagem) VALUES (%s, %s) RETURNING id", (nome, imagem_io.getvalue()))
            user_id = cur.fetchone()[0]
            conn.commit()

            bot.send_message(original_message.chat.id, f"Usuário '{nome}' foi adicionado com sucesso! ID: {user_id}")
        except (Exception, psycopg2.DatabaseError) as error:
            bot.send_message(original_message.chat.id, f"Ocorreu um erro ao adicionar o usuário: {str(error)}")
        finally:
            if conn is not None:
                cur.close()
                conn.close()

    @bot.callback_query_handler(func=lambda call: call.data == 'exibir')
    def callback_exibir_usuario(call):
        exibir_usuario(call.message)

    @bot.message_handler(func=lambda message: message.text == 'Exibir')
    def exibir_usuario(message):
        conn = conectar_bd()
        cur = conn.cursor()

        try:
            cur.execute("SELECT id, nome FROM usuarios")
            usuarios = cur.fetchall()
            keyboard = types.InlineKeyboardMarkup()
            for usuario in usuarios:
                user_id = usuario[0]
                nome = usuario[1]
                button = types.InlineKeyboardButton(text=nome, callback_data=f'exibir:{user_id}')
                keyboard.add(button)

            bot.send_message(message.chat.id, "Selecione um usuário para exibir:", reply_markup=keyboard)
        except (Exception, psycopg2.DatabaseError) as error:
            bot.send_message(message.chat.id, f"Ocorreu um erro ao exibir os usuários: {str(error)}")
        finally:
            if conn is not None:
                cur.close()
                conn.close()

    # Método para lidar com os callbacks dos botões de exibição de usuário
    @bot.callback_query_handler(func=lambda call: call.data.startswith('exibir:'))
    def handle_exibir_usuario(call):
        user_id = call.data.split(':')[1]
        conn = conectar_bd()
        cur = conn.cursor()

        try:
            cur.execute("SELECT nome, imagem FROM usuarios WHERE id = %s", (user_id,))
            usuario = cur.fetchone()

            if usuario:
                nome = usuario[0]
                imagem = usuario[1]
                bot.send_photo(call.message.chat.id, imagem, caption=nome)
            else:
                bot.send_message(call.message.chat.id, "Usuário não encontrado.")
        except (Exception, psycopg2.DatabaseError) as error:
            bot.send_message(call.message.chat.id, f"Ocorreu um erro ao exibir o usuário: {str(error)}")
        finally:
            if conn is not None:
                cur.close()
                conn.close()


