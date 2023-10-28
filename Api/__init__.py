import telebot
import requests
from telebot import types
from Chave import CHAVE_API

bot = telebot.TeleBot(CHAVE_API)

URL_API_WIKIPEDIA = "https://pt.wikipedia.org/api/rest_v1/page/summary"
URL_API_CLIMA = "https://api.hgbrasil.com/weather"


@bot.message_handler(func=lambda message: message.text == 'API')
def iniciar_api(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    wikip_button = types.KeyboardButton('Wikipédia')
    clima_button = types.KeyboardButton('Clima')
    markup.add(wikip_button, clima_button)
    bot.send_message(message.chat.id, "Escolha uma opção:", reply_markup=markup)


def chatbot_apis(bot):
    @bot.message_handler(func=lambda message: message.text == 'Wikipédia')
    def buscar_wikipedia(message):
        bot.send_message(message.chat.id, "Informe o tema da sua busca:")
        bot.register_next_step_handler(message, resposta_wikipedia)

    @bot.message_handler(func=lambda message: message.text == 'Clima')
    def buscar_clima(message):
        bot.send_message(message.chat.id, "Informe sua cidade:")
        bot.register_next_step_handler(message, resposta_clima)

    @bot.message_handler(func=lambda message: True)
    def obter_informacoes(message):
        bot.send_message(message.chat.id, "Opção inválida. Por favor, escolha uma opção válida.")

    def resposta_wikipedia(message):
        tema = message.text
        response = requests.get(f"{URL_API_WIKIPEDIA}/{tema}")

        if response.status_code == 200:
            data = response.json()
            titulo = data.get("title")
            imagem_url = data.get("thumbnail", {}).get("source")
            resumo = data.get("extract")

            bot.send_photo(message.chat.id, imagem_url, caption=resumo)
        else:
            bot.send_message(message.chat.id, "Desculpe, não foi possível encontrar informações sobre o tema.")

    def resposta_clima(message):
        cidade = message.text
        params = {
            "key": "SUA_CHAVE_API_HG",
            "city_name": cidade
        }
        response = requests.get(URL_API_CLIMA, params=params)

        if response.status_code == 200:
            data = response.json()
            clima = data.get("results", {}).get("temp")
            descricao = data.get("results", {}).get("description")

            bot.send_message(message.chat.id, f"Clima em {cidade}: {clima}°C - {descricao}")
        else:
            bot.send_message(message.chat.id, "Desculpe, não foi possível obter o clima da cidade.")





