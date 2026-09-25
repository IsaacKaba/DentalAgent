# DentalAgent

AI-powered Telegram dental secretary built with Python and Mistral AI.

DentalAgent handles patient conversations, collects relevant information, forwards medical images to a dental student for human validation, and uses function calling to check appointment availability.

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


## Architecture

```text
Patient
   │
   │ Telegram message
   ▼
┌─────────────────────┐
│     DentalAgent     │
│       Python        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Mistral AI     │
│    LLM + Tools      │
└───────┬─────────────┘
        │
        ├──────────────────────┐
        │                      │
        ▼                      ▼
 Conversation          Function Calling
        │                      │
        │                      ▼
        │             check_availability()
        │                      │
        │                      ▼
        │               Available slots
        │
        ▼
 Medical image
        │
        ▼
┌─────────────────────┐
│   Dental Student    │
│   Human Validation  │
└──────────┬──────────┘
           │
      Accept / Reject
           │
           ▼
        Patient
```



`.env` contains local credentials and must not be committed to the repository.

## Features

* Natural patient conversations powered by Mistral AI
* Patient information and symptom collection
* Medical image forwarding to a dental student
* Human-in-the-loop validation
* Appointment availability through Mistral function calling
* Per-patient conversation history
* Telegram-based administration with Accept/Reject buttons

## Tech Stack

* Python
* Mistral AI
* pyTelegramBotAPI
* python-dotenv
* Telegram Bot API

## Installation

```bash
git clone https://github.com/IsaacKaba/DentalAgent.git
cd DentalAgent
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

### Environment variables

Create a `.env` file:

```env
TELEGRAM_TOKEN=your_telegram_token
MISTRAL_API_KEY=your_mistral_api_key
ADMIN_CHAT_ID=your_admin_chat_id
```

## Usage

Start the bot with:

```bash
python agent.py
```

The bot then handles patient conversations through Telegram.

## Patient Workflow

```text
Patient
   │
   ▼
Conversation with AI
   │
   ▼
Information collection
   │
   ▼
Photo / X-ray requested
   │
   ▼
Patient sends image
   │
   ▼
Case sent to dental student
   │
   ▼
Human validation
   │
   ├── Accept ──► Appointment availability
   │
   └── Reject ──► Alternative recommendation
```

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for the full license text.
