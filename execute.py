import telebot
from telebot import types
import string
import random
from deep_translator import GoogleTranslator
import requests

bot = telebot.TeleBot("TUA_API_KEY")

# Lista dei servizi offerti dal bot
servizi = ["Genera Password", "Traduci Testo", "Calcolatore", "Citazione Casuale", "Ricerca GIF"]

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
        # Descrizione del servizio
        bot.send_message(chat_id=call.message.chat.id,
                         text="Questo servizio genererà una password casuale di 12 caratteri (lettere maiuscole, minuscole, numeri e simboli).")

        # Genera una password casuale
        lunghezza_password = 12  # Lunghezza della password desiderata
        password = ''.join(random.choice(caratteri) for _ in range(lunghezza_password))
        bot.send_message(chat_id=call.message.chat.id, text=f"La tua password generata casualmente è: {password}")

    elif servizio_scelto == "Traduci Testo":
        # Descrizione del servizio
        bot.send_message(chat_id=call.message.chat.id,
                         text="Questo servizio ti permetterà di tradurre un testo in un'altra lingua. Inserisci il testo da tradurre e successivamente specifica la lingua di destinazione (es: it, en, es, fr).")

        # Richiedi il testo da tradurre e la lingua di destinazione
        msg = bot.send_message(call.message.chat.id, "Inserisci il testo da tradurre:")
        bot.register_next_step_handler(msg, get_text_to_translate)

    elif servizio_scelto == "Calcolatore":
        # Descrizione del servizio
        bot.send_message(chat_id=call.message.chat.id,
                         text="Questo servizio fungerà da calcolatrice. Inserisci un'espressione matematica (ad esempio: 2+3*5, 10/2, ecc.) e il bot la valuterà e mostrerà il risultato.")

        # Richiedi l'espressione matematica
        msg = bot.send_message(call.message.chat.id, "Inserisci l'espressione matematica:")
        bot.register_next_step_handler(msg, calculate_expression)

    elif servizio_scelto == "Citazione Casuale":
        # Descrizione del servizio
        bot.send_message(chat_id=call.message.chat.id,
                         text="Questo servizio ti invierà una citazione casuale presa da una lista di citazioni famose.")

        # Invia una citazione casuale
        quote = random.choice(quotes)
        bot.send_message(call.message.chat.id, quote)
        show_services_menu(call.message)

    elif servizio_scelto == "Ricerca GIF":
        # Descrizione del servizio
        bot.send_message(chat_id=call.message.chat.id,
                         text="Questo servizio ti permetterà di cercare e ricevere GIF animate correlate a una parola chiave o frase di tuo interesse. Inserisci la parola chiave o frase e il bot cercherà e ti invierà la prima GIF rilevante trovata su Giphy.")

        # Richiedi la parola chiave per la ricerca GIF
        msg = bot.send_message(call.message.chat.id, "Inserisci una parola chiave per cercare GIF:")
        bot.register_next_step_handler(msg, search_gif)

    else:
        # Gestisci altri servizi qui
        bot.answer_callback_query(call.id, text=f"Hai selezionato il servizio: {servizio_scelto}")


# Le altre funzioni rimangono invariate

bot.infinity_polling()