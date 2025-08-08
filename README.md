# 🎙️ VoiceDB Assistant

**VoiceDB Assistant** is a voice-controlled chatbot application that lets users interact with a structured database using natural language voice commands. It transcribes audio input, extracts the user’s intent using a language model, and performs corresponding database operations — such as creating, reading, updating, deleting, filtering, and sorting entries.

## 🚀 Features

- 🎤 **Voice input via microphone** (real-time recording)
- 🧠 **Speech recognition** using [OpenAI Whisper](https://github.com/openai/whisper)
- 📋 **Natural language parsing** via `LangChain` and language models (e.g., Google Gemini or others)
- 🔧 **Structured database operations** (CRUD, filter, sort, replicate)
- 🗂️ **Local SQLite database** for storing and managing entries
- 🖥️ **Interactive web UI** built with Flask, JS, CSS & HTML
- 🌍 **Multilingual support** via Whisper (auto language detection)

## 📦 Project Structure

```bash
.
├── app.py                   # Flask app 
├── main.py                  # CLI interface
├── db/
│   ├── create_db.py         # Script to initialize the database
│   └── inventory.db         # SQLite database file
├── utils/
│   ├── tools.py             # Core logic for executing parsed commands
│   ├── models.py            # Pydantic models for command schema
│   └── utils.py             # Helper functions
├── test/                    # Voice command test files
├── templates/               # Optional front-end template
├── README.md                # You are here
```

## 🗣️ Sample Voice Commands
Here are some examples of what you can say to the assistant:
| Intent                  | Sample Voice Command                                                 |
| ----------------------- | -------------------------------------------------------------------- |
| **Create**              | "Add a new row with ID 10, name 'Notebook', color blue, quantity 25" |
| **Read**                | "Show all products in the database"                                  |
| **Update**              | "Change the color of row 4 to red"                                   |
| **Delete**              | "Remove row 6 from the table"                                        |
| **Filter**              | "Show all books with quantity less than 10"                          |
| **Sort**                | "Sort products by quantity in descending order"                      |
| **Replicate**           | "Replicate row 3 three times"                                        |

## 🛠️ Technologies Used
  - Python
  - Whisper (speech-to-text)
  - LangChain (intent parsing)
  - Pydantic (validation)
  - SQLite (database)
  - Flask, JS, CSS & HTML
    

---

## 💻 Installing and Running the Project

Follow these steps to get **VoiceDB Assistant** up and running on your local machine.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/voicedb-assistant.git
cd voicedb-assistant
```

### 2️⃣ Create and Activate a Virtual Environment (Optional)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Prepare the Database

Run the script to generate the sample dataset.

```bash
python3 db/create_db.py
```

### 5️⃣ Run the Application

#### ▶️ Option 1 — Run with Web Interface

```bash
python3 app.py
```

### 6️⃣ Access in Your Browser

Open your browser and go to:

```
http://127.0.0.1:5000
```

You can now chat with the assistant, use voice commands, and explore your database.

#### ▶️ Option 2 — Run with Command-Line Interface
```bash
python3 main.py test/1.mp3
```

