import telebot
from telebot import types
import string
import random
from deep_translator import GoogleTranslator
import requests
import io

promemoria = {}

bot = telebot.TeleBot("7249708469:AAHEqhkdG3w026nsD5rZR6oPEf7aWrkPcvw")

# Lista dei servizi offerti dal bot
servizi = ["Genera Password", "Traduci Testo", "Calcolatore", "Citazione Casuale", "Ricerca GIF","Promemoria","Conversione Unità di misura"]

# Caratteri utilizzati per generare la password
caratteri = string.ascii_letters + string.digits + string.punctuation

# Inizializza il traduttore
translator = GoogleTranslator()

# Lista di citazioni
quotes = [
    "L'unico modo per fare un lavoro straordinario è amare quello che fai. - Steve Jobs",
    "Il successo non è definitivo, il fallimento non è fatale: ciò che conta è il coraggio di continuare. - Winston Churchill",
    "Credi in te stesso e tutto sarà possibile. - Christopher Reeve",
    "L'immaginazione è più importante della conoscenza. - Albert Einstein",
    "Solo chi osa andare troppo lontano scoprirà quanto si può arrivare lontano. - Thomas Arthur Eliot"
]

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
        bot.send_message(chat_id=call.message.chat.id, text=password)
    elif servizio_scelto == "Traduci Testo":
        # Richiedi il testo da tradurre e la lingua di destinazione
        msg = bot.send_message(call.message.chat.id, "Inserisci il testo da tradurre:")
        bot.register_next_step_handler(msg, get_text_to_translate)
    elif servizio_scelto == "Calcolatore":
        # Richiedi l'espressione matematica
        msg = bot.send_message(call.message.chat.id, "Inserisci l'espressione matematica:")
        bot.register_next_step_handler(msg, calculate_expression)
    elif servizio_scelto == "Citazione Casuale":
        # Invia una citazione casuale
        quote = random.choice(quotes)
        bot.send_message(call.message.chat.id, quote)
        show_services_menu(call.message)
    elif servizio_scelto == "Ricerca GIF":
        # Richiedi la parola chiave per la ricerca GIF
        msg = bot.send_message(call.message.chat.id, "Inserisci una parola chiave per cercare GIF:")
        bot.register_next_step_handler(msg, search_gif)


    elif servizio_scelto == "Promemoria":

        keyboard = types.InlineKeyboardMarkup()

        button_add = types.InlineKeyboardButton(text="Aggiungi promemoria", callback_data="add_reminder")

        button_view = types.InlineKeyboardButton(text="Visualizza promemoria", callback_data="view_reminders")

        keyboard.add(button_add, button_view)

        bot.send_message(chat_id=call.message.chat.id, text="Seleziona un'opzione:", reply_markup=keyboard)

    elif servizio_scelto == "add_reminder":

        msg = bot.send_message(call.message.chat.id, "Inserisci il tuo promemoria:")

        bot.register_next_step_handler(msg, set_reminder)

    elif servizio_scelto == "view_reminders":

        chat_id = call.message.chat.id

        if chat_id in promemoria:

            reminders_text = "\n".join(promemoria[chat_id])

            keyboard = types.InlineKeyboardMarkup()

            button_download = types.InlineKeyboardButton(text="Scarica promemoria", callback_data="download_reminder")

            keyboard.add(button_download)

            bot.send_message(chat_id, f"I tuoi promemoria:\n{reminders_text}", reply_markup=keyboard)

        else:

            bot.send_message(chat_id, "Non hai impostato ancora nessun promemoria.")

            show_services_menu(call.message)

    elif servizio_scelto == "download_reminder":

        chat_id = call.message.chat.id

        if chat_id in promemoria:

            reminder_file = create_reminder_file(promemoria[chat_id], chat_id)

            bot.send_document(chat_id=chat_id, document=reminder_file)

        else:

            bot.send_message(chat_id, "Non hai impostato ancora nessun promemoria.")

        show_services_menu(call.message)

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

def search_gif(message):
    query = message.text
    api_key = "uCuxJoI5B1vFuU7szoKugQsscHchSxXb"  # Sostituisci con la tua chiave API di GIPHY
    url = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit=1"
    response = requests.get(url)
    data = response.json()

    if data["data"]:
        gif_url = data["data"][0]["images"]["original"]["url"]
        bot.send_animation(chat_id=message.chat.id, animation=gif_url)
    else:
        bot.send_message(chat_id=message.chat.id, text="Nessuna GIF trovata per la ricerca specificata.")

    show_services_menu(message)

def set_reminder(message):
    chat_id = message.chat.id
    reminder = message.text
    if chat_id in promemoria:
        promemoria[chat_id].append(reminder)
    else:
        promemoria[chat_id] = [reminder]
    bot.send_message(chat_id, "Promemoria impostato correttamente.")
    show_services_menu(message)

def create_reminder_file(reminders, chat_id):
    reminder_text = "\n".join(reminders)
    file_data = io.BytesIO(reminder_text.encode('utf-8'))
    file_data.name = f"promemoria_{chat_id}.txt"
    return file_data

bot.infinity_polling()