import os
import json

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from mistralai import Mistral
from mistralai.models import SystemMessage, UserMessage, AssistantMessage, ToolMessage
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
DENTIST_NAME = os.getenv("DENTIST_NAME")
DENTIST_LINK = os.getenv("DENTIST_LINK")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

chat_history = {}





@bot.message_handler(content_types=["photo"])
def handle_patient_photo(message):
    patient_id = message.chat.id


    summary_prompt = """
    Fais un résumé structuré de cette conversation pour le dentiste.
    Inclus obligatoirement sous forme de tirets :
    - Identité : Nom, Prénom, Âge.
    - Motif de la consultation.
    - Symptômes et durée.
    Ne t'adresse pas au patient, rédige-le comme une fiche médicale très concise.
    RÈGLE ABSOLUE 1 : Ce résumé doit OBLIGATOIREMENT être rédigé en FRANÇAIS, quelle que soit la langue parlée par le patient. Traduis les symptômes si nécessaire.
    RÈGLE ABSOLUE 2 : N'utilise AUCUN formatage en gras (pas d'astérisques **).
    """

    summary_history = chat_history.get(patient_id, []).copy()
    summary_history.append(UserMessage(content=summary_prompt))

    print("⏳ Génération du résumé par l'IA...")

    try:
        response = mistral_client.chat.complete(
            model="open-mistral-nemo",
            messages=summary_history
        )
        patient_summary = response.choices[0].message.content
    except Exception as error:
        patient_summary = "Erreur lors de la génération du résumé."
        print(f"Erreur IA : {error}")

    dossier = f"🚨 NOUVEAU DOSSIER PATIENT (ID: {patient_id})\n\n{patient_summary}"
    bot.send_message(ADMIN_CHAT_ID, dossier)

    bot.send_photo(
        ADMIN_CHAT_ID,
        message.photo[-1].file_id,
        caption="📸 Photo jointe au dossier ci-dessus."
    )
    
    if patient_id not in chat_history:
        chat_history[patient_id] = [SystemMessage(content=SYSTEM_PROMPT)]

    chat_history[patient_id].append(
        SystemMessage(
            content=f"Le patient vient d'envoyer la photo avec succès. Passe directement à l'ÉTAPE 4 : Remercie-le, dis-lui que le dossier a été transmis, et donne-lui le lien Facebook. Rédige ce dernier message DANS LA LANGUE DU PATIENT (ex: en roumain s'il parlait roumain). RÈGLE ABSOLUE : N'utilise AUCUN formatage Markdown. Donne le lien exactement comme ça : {DENTIST_LINK}"
        )
    )
    
    response = mistral_client.chat.complete(
        model="open-mistral-nemo",
        messages=chat_history[patient_id]
    )
    
    ai_message = response.choices[0].message
    
    chat_history[patient_id].append(ai_message)
    
    bot.send_message(patient_id, ai_message.content)






SYSTEM_PROMPT = f"""
Tu es l'assistant de pré-consultation de {DENTIST_NAME}, étudiant en chirurgie dentaire.
Tu échanges avec les patients par message privé sur Telegram.

TON RÔLE :
Accueillir le patient, comprendre son besoin, recueillir son identité, lui demander une radio/photo si nécessaire, puis le rediriger vers le Messenger personnel de {DENTIST_NAME} pour la décision finale et la prise de rendez-vous.

RÈGLES DE CONVERSATION :
- Utilise un ton naturel, simple et humain (1 à 3 phrases maximum).
- Pose UNE SEULE question à la fois.
- Ne donne jamais de diagnostic médical.
- Adapte tes questions aux réponses du patient.
- ADAPTATION DE LA LANGUE : Réponds TOUJOURS au patient dans la langue qu'il utilise (ex: s'il te parle en roumain, parle-lui en roumain. S'il te parle en français, réponds en français).
- RÈGLE ABSOLUE : N'utilise JAMAIS de formatage Markdown (pas de **gras**, pas de *italique*, pas de crochets [texte](lien)). Écris uniquement en texte brut.

ÉTAPE 1 — COMPRENDRE LA DEMANDE :
Salue le patient et demande naturellement ce qui l'amène (symptômes, douleur).

ÉTAPE 2 — RECUEILLIR L'IDENTITÉ :
Une fois le besoin compris, demande au patient son nom, son prénom et son âge.

ÉTAPE 3 — RADIO OU PHOTO :
Une fois l'identité connue, demande au patient s'il possède une radio ou une photo de la zone concernée.
- S'il n'en a pas, passe à l'étape 4.
- S'il en a une, demande-lui de l'envoyer. Une fois reçue, passe à l'étape 4.

ÉTAPE 4 — REDIRECTION VERS LE DENTISTE (FIN) :
Une fois le dossier complet (infos + éventuelle photo), remercie le patient et explique-lui que ton rôle s'arrête ici.
Demande-lui de contacter directement l'étudiant-dentiste ({DENTIST_NAME}) sur Facebook pour qu'il examine le dossier et lui propose un rendez-vous.
Donne-lui OBLIGATOIREMENT ce lien vers son profil en texte brut :
{DENTIST_LINK}
Précise-lui bien de cliquer sur le bouton "Message" une fois sur le profil.
Clôture la conversation chaleureusement.
"""

@bot.message_handler(func=lambda message: True)
def handle_patient_message(message):
    try:
        chat_id = message.chat.id
        patient_message = message.text

        print(f"\nReceived from {message.from_user.first_name}: {patient_message}")

        if chat_id not in chat_history:
            chat_history[chat_id] = [SystemMessage(content=SYSTEM_PROMPT)]

        chat_history[chat_id].append(UserMessage(content=patient_message))

        response = mistral_client.chat.complete(
            model="open-mistral-nemo",
            messages=chat_history[chat_id]
        )

        ai_message = response.choices[0].message
        chat_history[chat_id].append(ai_message)

        bot.reply_to(message, ai_message.content)
        print(f"Bot replied: {ai_message.content}")

    except Exception as error:
        print(f"\nERROR: {error}")
        bot.reply_to(message, "Oups, un petit souci technique est survenu.")


if __name__ == "__main__":
    print("Telegram bot is online.")
    bot.infinity_polling()

