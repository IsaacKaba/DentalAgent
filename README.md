# DentalAgent

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,gcp&theme=light" alt="Python and Google Cloud">
  <img src="https://cdn.simpleicons.org/mistralai" height="48" alt="Mistral AI">
  <img src="https://cdn.simpleicons.org/telegram" height="48" alt="Telegram">
</p>

<p align="center">
  <strong>AIAgent Telegram dental pre-consultation assistant</strong>
</p>

<p align="center">
  DentalAgent helps a dental student collect patient information,<br>
  prepare a patient dossier and receive medical images through Telegram.
</p>

---

## Overview

DentalAgent is a Telegram-based AI assistant designed to handle the **pre-consultation stage** of a dental interaction.

The bot uses Mistral AI to:

* communicate naturally with patients;
* automatically adapt to the patient's language either Romanian or French;
* collect identity and consultation information;
* ask for a photo or X-ray when necessary;
* generate a concise patient summary;
* forward the patient's dossier and image to the dental student.

After the pre-consultation, the patient is redirected to the dental student's personal Facebook Messenger for the final discussion and appointment.

> DentalAgent does not provide medical diagnoses. The final assessment and appointment are handled by the dental student.

## Project Structure

```text
DentalAgent/
├── agent.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── .env
```

`.env` contains local credentials and configuration and must not be committed to the repository.

## Architecture

```text
                         Patient
                            │
                            │ Telegram
                            ▼
                 ┌─────────────────────┐
                 │     DentalAgent     │
                 │       Python        │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │      Mistral AI     │
                 │   Conversation AI   │
                 └──────────┬──────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
     Patient information           Photo / X-ray
     & symptoms collection               │
              │                           │
              └─────────────┬─────────────┘
                            ▼
                 ┌─────────────────────┐
                 │   Dental Student    │
                 │                     │
                 │  Patient dossier   │
                 │  + attached image  │
                 └──────────┬──────────┘
                            │
                            ▼
                 Facebook Messenger
                            │
                            ▼
                 Final discussion
                  & appointment
```

## Features

* AI-powered patient conversations
* Automatic language adaptation
* Patient identity collection
* Consultation reason and symptom collection
* Photo / X-ray collection
* Automatic patient case summary
* Patient dossier sent to the dental student
* Medical image forwarded with the dossier
* Telegram-based administration
* Per-patient conversation history
* Redirection to Facebook Messenger

## Patient Workflow

```text
┌──────────────────────┐
│  1. Initial contact  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 2. Consultation      │
│    reason & symptoms  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 3. Identity          │
│    collection        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 4. Photo / X-ray     │
│    requested         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 5. Patient dossier   │
│    generated         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 6. Dossier sent to   │
│    dental student    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 7. Facebook          │
│    Messenger         │
└──────────────────────┘
```

## Patient Experience

The patient interacts entirely through Telegram during the pre-consultation.

The assistant adapts its language automatically depending on the language used by the patient.

### Example — Patient Conversation

![Patient conversation](images/patient-conversation.png)

### Example — Patient Sends a Photo

![Patient photo](images/patient-photo.png)

## Dental Student Experience

When the patient sends a photo or X-ray, DentalAgent:

1. retrieves the patient's conversation history;
2. generates a structured summary;
3. sends the summary to the dental student's Telegram;
4. sends the original image separately.

### Example — Patient Dossier

![Dental student dossier](images/dental-student-dossier.png)

### Example — Attached Image

![Attached medical image](images/dental-student-image.png)

The generated summary follows this structure:

```text
🚨 NOUVEAU DOSSIER PATIENT

- Identité : Nom, Prénom, Âge.
- Motif de la consultation : ...
- Symptômes et durée : ...

📸 Photo jointe au dossier.
```

The patient-facing conversation can take place in any language supported by the model, while the dossier sent to the dental student is always generated in French.

## Technology Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,gcp&theme=light" alt="Python and Google Cloud">
  <img src="https://cdn.simpleicons.org/mistralai" height="48" alt="Mistral AI">
  <img src="https://cdn.simpleicons.org/telegram" height="48" alt="Telegram">
</p>

| Technology       | Usage                                          |
| ---------------- | ---------------------------------------------- |
| Python           | Main programming language                      |
| Mistral AI       | Patient conversation and dossier summarization |
| Telegram Bot API | Patient and dental student communication       |
| pyTelegramBotAPI | Telegram integration                           |
| python-dotenv    | Environment variable management                |
| Google Cloud     | Deployment / infrastructure                    |

## Installation

Clone the repository:

```bash
git clone https://github.com/IsaacKaba/DentalAgent.git
cd DentalAgent
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_TOKEN=your_telegram_token
MISTRAL_API_KEY=your_mistral_api_key
ADMIN_CHAT_ID=your_admin_chat_id
DENTIST_NAME=your_dentist_name
DENTIST_LINK=your_facebook_profile_link
```

Never commit `.env` to Git.

## Usage

Start the bot:

```bash
python agent.py
```

The terminal should display:

```text
Telegram bot is online.
```

The bot is then ready to receive Telegram messages.

## Human-in-the-Loop

DentalAgent is designed as a **pre-consultation assistant**, not as an autonomous medical system.

```text
Patient
   │
   ▼
AI pre-consultation
   │
   ▼
Information + symptoms
   │
   ▼
Photo / X-ray
   │
   ▼
Patient dossier
   │
   ▼
Dental student
   │
   ▼
Final discussion
   │
   ▼
Appointment
```

The AI does not diagnose the patient. The dental student receives the collected information and image and handles the final assessment directly with the patient.

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for the full license text.
