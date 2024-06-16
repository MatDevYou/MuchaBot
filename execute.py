import telebot
from telebot import types
import string
import random
from deep_translator import GoogleTranslator

bot = telebot.TeleBot("7249708469:AAHEqhkdG3w026nsD5rZR6oPEf7aWrkPcvw")

# Lista dei servizi offerti dal bot
servizi = ["Genera Password", "Traduci Testo", "Calcolatore","Meteo"]

# Caratteri utilizzati per generare la password
caratteri = string.ascii_letters + string.digits + string.punctuation

# Inizializza il traduttore
translator = GoogleTranslator()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Crea i tasti di risposta inline per i servizi
    keyboard = types.InlineKeyboardMarkup()
    for servizio in servizi:
        button = types.InlineKeyboardButton(text=servizio, callback_data=servizio)
        keyboard.add(button)

    # Invia il messaggio di benvenuto con i tasti di risposta inline
    bot.reply_to(message, "Ciao, seleziona uno dei seguenti servizi:", reply_markup=keyboard)

# Gestore per il comando /stop
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    bot.reply_to(message, "Arrivederci! Il bot è stato fermato.")
    bot.stop_polling()  # Ferma il polling del bot

def show_services_menu(message):
    # Crea i tasti di risposta inline per i servizi
    keyboard = types.InlineKeyboardMarkup()
    for servizio in servizi:
        button = types.InlineKeyboardButton(text=servizio, callback_data=servizio)
        keyboard.add(button)

    # Invia il messaggio con i tasti di risposta inline
    bot.send_message(message.chat.id, "Seleziona uno dei seguenti servizi:", reply_markup=keyboard)

# Gestore per le risposte inline
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    servizio_scelto = call.data
    if servizio_scelto == "Genera Password":
        # Genera una password casuale
        lunghezza_password = 12  # Lunghezza della password desiderata
        password = ''.join(random.choice(caratteri) for _ in range(lunghezza_password))
        bot.send_message(chat_id=call.message.chat.id, text=f"La tua password generata casualmente è: ")
        bot.send_message(chat_id=call.message.chat.id, text={password})
    elif servizio_scelto == "Traduci Testo":
        # Richiedi il testo da tradurre e la lingua di destinazione
        msg = bot.send_message(call.message.chat.id, "Inserisci il testo da tradurre:")
        bot.register_next_step_handler(msg, get_text_to_translate)
    elif servizio_scelto == "Calcolatore":
        # Richiedi l'espressione matematica
        msg = bot.send_message(call.message.chat.id, "Inserisci l'espressione matematica:")
        bot.register_next_step_handler(msg, calculate_expression)
    else:
        # Gestisci altri servizi qui
        bot.answer_callback_query(call.id, text=f"Hai selezionato il servizio: {servizio_scelto}")

def calculate_expression(message):
    expression = message.text
    try:
        result = str(eval(expression))
        bot.send_message(message.chat.id, f"Risultato: {result}")
        show_services_menu(message)  # Mostra il menu dei servizi
    except Exception as e:
        bot.send_message(message.chat.id, f"Errore durante il calcolo: {e}")
        show_services_menu(message)  # Mostra il menu dei servizi

def get_text_to_translate(message):
    text_to_translate = message.text
    msg = bot.send_message(message.chat.id, "Seleziona la lingua di destinazione (es: it, en, es, fr):")
    bot.register_next_step_handler(msg, translate_text, text_to_translate)

def translate_text(message, text_to_translate):
    target_language = message.text.lower().strip()
    try:
        if target_language == "es":
            translated_text = translator.translate(text_to_translate, target="es")
        elif target_language == "fr":
            translated_text = translator.translate(text_to_translate, target="fr")
        else:
            translated_text = translator.translate(text_to_translate, target="en")
        bot.send_message(message.chat.id, f"Testo tradotto: {translated_text}")
        show_services_menu(message)  # Mostra il menu dei servizi
    except Exception as e:
        bot.send_message(message.chat.id, f"Errore durante la traduzione: {e}")
        show_services_menu(message)  # Mostra il menu dei servizi

import requests

def get_weather(city):
    api_key = "YOUR_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        weather = data["weather"][0]
        temperature = main["temp"]
        description = weather["description"]
        return f"La temperatura a {city} è {temperature}°C con {description}."
    else:
        return "Città non trovata."

# Nella funzione handle_callback aggiungi:
elif servizio_scelto == "Meteo":
    msg = bot.send_message(call.message.chat.id, "Inserisci il nome della città:")
    bot.register_next_step_handler(msg, send_weather)

def send_weather(message):
    city = message.text
    weather_info = get_weather(city)
    bot.send_message(message.chat.id, weather_info)
    show_services_menu(message)


bot.infinity_polling()
