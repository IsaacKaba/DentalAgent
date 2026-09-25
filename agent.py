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

bot = telebot.TeleBot(TELEGRAM_TOKEN)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

chat_history = {}

SCHEDULE = {
    "vendredi": ["17:00", "18:00"],
    "samedi": ["14:00", "15:00", "16:30"]
}


@bot.message_handler(content_types=["photo"])
def handle_patient_photo(message):
    patient_id = message.chat.id

    bot.reply_to(
        message,
        "Merci pour la photo ! Je prépare votre dossier et je le transmets à "
        "l'étudiant-dentiste. Je reviens vers vous dès qu'il l'a examiné. ⏳"
    )

    summary_prompt = """
Fais un résumé structuré de cette conversation pour le dentiste.

Inclus obligatoirement sous forme de tirets :

- Identité : Nom, Prénom, Âge.
- Motif de la consultation.
- Symptômes et durée.

Ne t'adresse pas au patient, rédige-le comme une fiche médicale très concise.

RÈGLE ABSOLUE : N'utilise AUCUN formatage en gras (pas d'astérisques **).
Rédige uniquement en texte brut.
"""

    temporary_history = chat_history.get(patient_id, []).copy()
    temporary_history.append(UserMessage(content=summary_prompt))

    print("⏳ Génération du résumé par l'IA...")

    try:
        response = mistral_client.chat.complete(
            model="open-mistral-nemo",
            messages=temporary_history
        )
        patient_summary = response.choices[0].message.content
    except Exception as error:
        patient_summary = "Erreur lors de la génération du résumé."
        print(f"Erreur IA : {error}")

    keyboard = InlineKeyboardMarkup()

    accept_button = InlineKeyboardButton(
        "✅ Accepter le soin",
        callback_data=f"accept_{patient_id}"
    )

    reject_button = InlineKeyboardButton(
        "❌ Refuser",
        callback_data=f"reject_{patient_id}"
    )

    keyboard.add(accept_button, reject_button)

    dossier = (
        f"🚨 NOUVEAU DOSSIER PATIENT (ID: {patient_id})\n\n"
        f"Résumé généré par l'IA :\n{patient_summary}"
    )

    bot.send_message(ADMIN_CHAT_ID, dossier)

    bot.send_photo(
        ADMIN_CHAT_ID,
        message.photo[-1].file_id,
        caption="📸 Photo jointe au dossier. Que décidez-vous ?",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_admin_decision(call):
    action, patient_id_str = call.data.split("_")
    patient_id = int(patient_id_str)

    bot.answer_callback_query(call.id, "Décision enregistrée !")

    bot.edit_message_caption(
        caption="Décision transmise au patient ✅",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

    if action == "accept":
        decision_prompt = (
            "L'étudiant-dentiste a validé la photo et accepte de réaliser le soin. "
            "Annonce-le au patient et passe à l'ÉTAPE 6 (Prise de rendez-vous)."
        )
    else:
        decision_prompt = (
            "L'étudiant-dentiste a regardé la photo mais ne peut pas réaliser ce soin. "
            "Annonce-le au patient avec tact et propose-lui de consulter un autre "
            "praticien. Fin de la prise de rendez-vous."
        )

    if patient_id in chat_history:
        chat_history[patient_id].append(
            SystemMessage(content=decision_prompt)
        )

        response = mistral_client.chat.complete(
            model="open-mistral-nemo",
            messages=chat_history[patient_id],
            tools=tools
        )

        ai_message = response.choices[0].message
        chat_history[patient_id].append(ai_message)

        bot.send_message(patient_id, ai_message.content)


def check_availability(day: str) -> str:
    """Return available appointment slots for a given weekday."""
    day = day.lower()

    if day in SCHEDULE and SCHEDULE[day]:
        return f"Dispos le {day} : {', '.join(SCHEDULE[day])}"

    return f"Aucune disponibilité le {day}."


tools = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Vérifie les créneaux disponibles dans l'agenda pour un jour précis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "Le jour de la semaine (ex: lundi, mardi, vendredi, samedi)."
                    }
                },
                "required": ["day"]
            }
        }
    }
]


SYSTEM_PROMPT = """
Tu es l'assistant secrétaire d'un étudiant en chirurgie dentaire.

Tu échanges avec les patients par message privé sur Messenger.

TON RÔLE :

Tu es chaleureux, naturel, professionnel et rassurant, comme un véritable secrétaire de cabinet dentaire.

Tu aides le patient à expliquer son besoin, tu recueilles les informations utiles et tu facilites l'échange avec l'étudiant-dentiste.

RÈGLES DE CONVERSATION :

- Commence toujours par saluer le patient.
- Ne sois ni froid, ni excessivement enthousiaste.
- Utilise un ton naturel, simple et humain.
- Fais des messages courts : généralement 1 à 3 phrases maximum.
- Pose UNE SEULE question à la fois.
- Ne bombarde jamais le patient de questions.
- Ne passe pas directement à la prise de rendez-vous.
- Commence par comprendre pourquoi le patient contacte le cabinet.
- Adapte tes questions aux réponses du patient au lieu de suivre un questionnaire rigide.
- Si le patient donne déjà une information, ne la redemande pas.
- Ne donne jamais de diagnostic médical.
- Ne décide jamais seul du traitement nécessaire.
- En cas d'urgence ou de symptôme potentiellement sérieux, reste prudent et recommande au patient de consulter rapidement un professionnel de santé si nécessaire.

ÉTAPE 1 — COMPRENDRE LA DEMANDE :

1. Salue le patient.
2. Demande naturellement ce qui l'amène.
3. Pose les questions nécessaires pour comprendre sa douleur ou son besoin.

Ne transforme pas immédiatement la conversation en prise de rendez-vous.

ÉTAPE 2 — RECUEILLIR L'IDENTITÉ :

Une fois le besoin compris, demande au patient son nom, son prénom et son âge.

Rappel : Pose une seule question à la fois. N'enchaîne pas les questions dans un seul message.

ÉTAPE 3 — PHOTO OU RADIO :

Une fois l'identité connue, demande au patient s'il possède une photo ou une radio qui pourrait aider l'étudiant-dentiste.

Exemple :

"Si vous avez une photo ou une radio de la zone concernée, vous pouvez également nous l'envoyer. Cela permettra à l'étudiant-dentiste de mieux regarder votre situation."

Si le patient n'en possède pas :

- Ne force pas le patient à en fournir une.
- Continue normalement la conversation.

Si le patient possède une photo ou une radio :

- Demande-lui simplement de l'envoyer dans la conversation.
- Lorsqu'un fichier ou une image est effectivement reçu, confirme brièvement sa réception.
- NE DONNE AUCUNE interprétation médicale de la photo ou de la radio.
- NE DIS PAS quel soin est nécessaire.
- NE PROPOSE PAS de rendez-vous à ce stade.

ÉTAPE 4 — VALIDATION PAR L'ÉTUDIANT-DENTISTE :

Lorsqu'une photo ou une radio est reçue, la conversation doit être considérée comme EN ATTENTE DE VALIDATION DU DENTISTE.

À ce moment :

- Une notification doit être envoyée à l'étudiant-dentiste pour lui signaler qu'une photo ou une radio du patient doit être vérifiée.
- L'étudiant-dentiste doit examiner lui-même le document.
- Le bot ne doit prendre AUCUNE décision à sa place.
- Le bot ne doit jamais déterminer seul le soin à réaliser.
- Le bot ne doit jamais promettre que l'étudiant-dentiste peut réaliser le soin.

L'étudiant-dentiste doit pouvoir indiquer :

- ce qu'il pense être nécessaire ;
- s'il est en mesure de réaliser le soin ;
- s'il souhaite réaliser le soin ;
- s'il souhaite recevoir davantage d'informations ;
- ou s'il préfère que le patient consulte un autre professionnel.

Le bot doit attendre cette validation avant de reprendre la conversation avec le patient.

ÉTAPE 5 — RETOUR VERS LE PATIENT :

Une fois que l'étudiant-dentiste a donné sa décision, reprends la conversation avec le patient.

Si l'étudiant-dentiste accepte de réaliser le soin :

- Informe simplement le patient que l'étudiant-dentiste peut prendre en charge la demande.
- Ne donne pas de diagnostic supplémentaire.
- Propose ensuite de passer à la recherche d'un rendez-vous.

Exemple :

"Merci pour votre patience ! L'étudiant-dentiste a pu regarder votre photo et peut prendre en charge votre demande. On peut maintenant regarder ensemble pour un rendez-vous 😊"

Si l'étudiant-dentiste ne souhaite pas réaliser le soin :

- Informe le patient avec tact.
- Ne donne pas de fausse justification.
- Suis exactement les indications données par l'étudiant-dentiste.

ÉTAPE 6 — PRISE DE RENDEZ-VOUS :

La prise de rendez-vous ne commence QUE lorsque :

1. Le besoin du patient est suffisamment compris.
2. La photo/radio a été vérifiée lorsqu'elle était disponible et pertinente.
3. L'étudiant-dentiste a confirmé qu'il peut et souhaite réaliser le soin.

À partir de là :

1. Demande au patient quel jour lui conviendrait.
2. Une fois le jour connu, utilise l'outil 'check_availability' pour vérifier les disponibilités de ce jour précis.
3. Ne propose JAMAIS de créneau qui n'a pas été renvoyé par l'outil.
4. Ne suppose JAMAIS qu'un créneau est disponible.
5. Si aucune disponibilité n'est trouvée, indique-le simplement et demande au patient quel autre jour lui conviendrait.
6. Ne propose pas spontanément plusieurs jours au hasard.
7. Lorsque l'outil renvoie des horaires disponibles, présente uniquement ces horaires au patient.

RÈGLES ABSOLUES :

- Ne jamais inventer une disponibilité.
- Ne jamais inventer un diagnostic.
- Ne jamais décider du soin à la place de l'étudiant-dentiste.
- Ne jamais confirmer qu'un soin sera réalisé avant validation de l'étudiant-dentiste.
- Ne jamais prendre de rendez-vous avant cette validation.
- Ne jamais interpréter médicalement une photo ou une radio à la place de l'étudiant-dentiste.
- Ne jamais faire semblant qu'un document a été examiné par l'étudiant-dentiste s'il ne l'a pas encore été.
- Ne jamais dire au patient qu'une photo/radio est "bonne", "mauvaise", "normale" ou qu'elle montre une pathologie.
- Si une information nécessaire manque, demande-la simplement au patient.
- Une seule question à la fois.
- Messages courts, naturels et conversationnels.
"""


@bot.message_handler(func=lambda message: True)
def handle_patient_message(message):
    try:
        chat_id = message.chat.id
        patient_message = message.text

        print(
            f"\nReceived from {message.from_user.first_name}: "
            f"{patient_message}"
        )

        if chat_id not in chat_history:
            chat_history[chat_id] = [
                SystemMessage(content=SYSTEM_PROMPT)
            ]

        chat_history[chat_id].append(
            UserMessage(content=patient_message)
        )

        response = mistral_client.chat.complete(
            model="open-mistral-nemo",
            messages=chat_history[chat_id],
            tools=tools
        )

        ai_message = response.choices[0].message
        chat_history[chat_id].append(ai_message)

        if ai_message.tool_calls:
            for tool_call in ai_message.tool_calls:
                if tool_call.function.name == "check_availability":
                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                    requested_day = arguments.get("day")
                    availability_result = check_availability(requested_day)

                    print(
                        f"Tool executed: check_availability("
                        f"'{requested_day}') -> {availability_result}"
                    )

                    chat_history[chat_id].append(
                        ToolMessage(
                            name="check_availability",
                            content=availability_result,
                            tool_call_id=tool_call.id
                        )
                    )

            response = mistral_client.chat.complete(
                model="open-mistral-nemo",
                messages=chat_history[chat_id],
                tools=tools
            )

            ai_message = response.choices[0].message
            chat_history[chat_id].append(ai_message)

        bot.reply_to(message, ai_message.content)

        print(f"Bot replied: {ai_message.content}")

    except Exception as error:
        print(f"\nERROR: {error}")

        bot.reply_to(
            message,
            "Oups, un petit souci technique est survenu avec l'agenda."
        )


if __name__ == "__main__":
    print("Telegram bot is online.")
    bot.infinity_polling()

