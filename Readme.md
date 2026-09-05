# AI Employee Assistant

An AI-powered employee assistant that combines **Structured RAG, Graph RAG, and Live RAG** to answer employee-related questions and provide real-time information through a **Streamlit** interface.

---

## 🚀 Project Overview

The AI Employee Assistant uses a routing-based architecture to determine which data source should answer a user's question.

It supports three retrieval approaches:

- **Structured RAG** → retrieves employee information from SQLite
- **Graph RAG** → retrieves relationships between employees using a NetworkX graph
- **Live RAG** → retrieves real-time weather information from an external API

After retrieval, the relevant context is passed to an LLM, which generates the final natural-language answer.

---

## 🏗️ Architecture

```text
                         USER QUERY
                             │
                             ▼
                    ┌────────────────┐
                    │    Streamlit   │
                    │       UI       │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │     Router     │
                    └───────┬────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
      ┌─────────────┐ ┌────────────┐ ┌─────────────┐
      │ Structured  │ │   Graph    │ │    Live     │
      │     RAG     │ │    RAG     │ │     RAG     │
      └──────┬──────┘ └─────┬──────┘ └──────┬──────┘
             │              │               │
             ▼              ▼               ▼
        SQLite DB       NetworkX       Weather API
        employees.db       Graph
             │              │               │
             └──────────────┼───────────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │ LLM Generator  │
                    └───────┬────────┘
                            │
                            ▼
                      FINAL ANSWER
```

---

## 🔹 1. Structured RAG

Structured RAG is used for questions that can be answered using structured employee records.

The employee information is stored in a SQLite database.

### Example questions

```text
Which employees work in Engineering?

Give me the employees in Bengaluru.

Who is on leave in Bengaluru?

Show active employees in Hyderabad.
```

### Flow

```text
User Question
     │
     ▼
   Router
     │
     ▼
Structured RAG
     │
     ▼
 SQLite Database
     │
     ▼
Employee Records
     │
     ▼
LLM Generator
     │
     ▼
Final Answer
```

The database contains employee attributes such as:

- Employee ID
- Name
- Department
- Position
- Email
- Phone
- Hire Date
- Salary
- Location
- Manager
- Status

---

## 🔹 2. Graph RAG

Graph RAG is used when the question requires understanding relationships between entities.

The employee data is converted into a **NetworkX graph**.

Relationships include:

```text
Employee ──WORKS_IN──> Department

Employee ──HAS_POSITION──> Position

Employee ──LOCATED_IN──> Location

Employee ──HAS_STATUS──> Status

Employee ──REPORTS_TO──> Manager
```

### Example question

```text
Who is Kevin Davis's manager?
```

### Flow

```text
User Question
     │
     ▼
   Router
     │
     ▼
 Graph RAG
     │
     ▼
NetworkX Graph
     │
     ▼
REPORTS_TO relationship
     │
     ▼
Manager information
     │
     ▼
LLM Generator
     │
     ▼
Final Answer
```

Graph RAG is useful when the answer depends on relationships rather than simply filtering database rows.

---

## 🔹 3. Live RAG

Live RAG is used when the user needs information that changes over time.

The current implementation uses a weather API.

### Example question

```text
What is the current weather in Vijayawada?
```

### Flow

```text
User Question
     │
     ▼
   Router
     │
     ▼
  Live RAG
     │
     ▼
Weather API
     │
     ▼
Current Weather Data
     │
     ▼
LLM Generator
     │
     ▼
Final Answer
```

The Live RAG module retrieves current weather information such as:

- Temperature
- Feels-like temperature
- Humidity
- Weather condition
- Wind speed
- Location information

---

# 🧠 Router

The router is responsible for deciding which retrieval strategy should handle the user's question.

```text
                    USER QUERY
                        │
                        ▼
                     ROUTER
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      Employee       Manager/      Weather
       Data          Relations     Question
          │             │             │
          ▼             ▼             ▼
    Structured RAG   Graph RAG      Live RAG
```

The router also extracts useful parameters such as:

- Employee name
- Employee ID
- Department
- Location
- Status
- City

---

# 🤖 LLM Answer Generation

The `generator.py` module is responsible for generating the final answer.

The retrieval modules provide the relevant context.

```text
Question
   +
Retrieved Context
   │
   ▼
LLM Generator
   │
   ▼
Natural Language Answer
```

This separates **retrieval** from **answer generation**.

---

# 🖥️ User Interface

The project uses **Streamlit as the UI framework**.

The UI provides:

- Chat interface
- User questions
- Assistant responses
- Retrieval strategy information
- Sidebar/project information
- Chat history

The UI is intentionally kept simple and is implemented entirely using Streamlit.

---

# 📁 Project Structure

```text
AI-Employee-Assistant/
│
├── app.py
├── router.py
├── database.py
├── structured_rag.py
├── graph_rag.py
├── graph_builder.py
├── live_rag.py
├── generator.py
│
├── database/
│   └── employees.db
│
├── data/
│   └── employees.csv
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### File responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI and application orchestration |
| `router.py` | Determines the appropriate RAG strategy |
| `database.py` | SQLite database operations |
| `structured_rag.py` | Structured employee retrieval |
| `graph_builder.py` | Builds the employee graph |
| `graph_rag.py` | Graph relationship retrieval |
| `live_rag.py` | Retrieves live weather information |
| `generator.py` | Generates final LLM answers |
| `employees.db` | Employee database |
| `employees.csv` | Source employee data |

---

# 🛠️ Technologies Used

- Python
- Streamlit
- SQLite
- NetworkX
- OpenAI API
- OpenWeather API
- python-dotenv

---

# ⚙️ Installation

Clone the repository:

```bash
git clone <your-github-repository-url>
cd AI-Employee-Assistant
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

```env
OPENAI_API_KEY=your_openai_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

Never commit your `.env` file to GitHub.

Add it to `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
```

---

# ▶️ Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Streamlit will start the application and provide the local URL in the terminal.

---

# 🧪 Example Queries

### Structured RAG

```text
Which employees work in Engineering?
```

```text
Give me list of names who are on leave in Bengaluru.
```

```text
Show active employees in Hyderabad.
```

### Graph RAG

```text
Who is Kevin Davis's manager?
```

```text
Who does Kevin Davis report to?
```

### Live RAG

```text
What is the current weather in Vijayawada?
```

```text
What is the current temperature in Hyderabad?
```

---

# 🔄 Complete Request Flow

```text
User
 │
 ▼
Streamlit
 │
 ▼
Router
 │
 ├───────────────┐
 │               │
 ▼               ▼
Structured      Graph
RAG             RAG
 │               │
 ▼               ▼
SQLite          NetworkX
 │               │
 └───────┬───────┘
         │
         ├───────────────┐
         │               │
         ▼               ▼
                         Live RAG
                             │
                             ▼
                        Weather API
                             │
                             ▼
                     Retrieved Context
                             │
                             ▼
                       LLM Generator
                             │
                             ▼
                       Final Answer
                             │
                             ▼
                        Streamlit UI
```

---

# 🎯 Key Design Principles

### Separation of responsibilities

Each component has a specific responsibility:

```text
app.py
  → UI

router.py
  → Routing

structured_rag.py
  → Structured retrieval

graph_rag.py
  → Relationship retrieval

live_rag.py
  → Live data retrieval

generator.py
  → Answer generation
```

This makes the project easier to understand, test, maintain, and extend.

---

# ✅ Current Implementation

The current implementation supports:

- Structured employee retrieval
- SQLite database querying
- Employee relationship retrieval
- NetworkX graph traversal
- Live weather retrieval
- Query routing
- LLM-based answer generation
- Streamlit chat interface

---

# 🚧 Future Improvements

Possible future extensions include:

- More live data sources
- More advanced graph relationships
- Better query classification
- Agent-based decision making
- Memory
- Observability
- Guardrails
- Evaluation
- MCP integration

These are **future improvements** and are not required for the current implementation.

---

# 📌 Important Database Values

The current employee database uses the following location/status terminology:

```text
Location:
Bengaluru
Hyderabad
Chennai
Mumbai
Delhi
Pune
Noida
Gurugram
Ahmedabad
Kolkata

Status:
Active
On Leave
```

Therefore, user-friendly terminology should be mapped to the actual database values when necessary.

For example:

```text
Bangalore → Bengaluru
Absent    → On Leave
```

---

# 📄 License

This project is intended for learning and demonstration purposes.
```

This README matches the **actual architecture we built** rather than adding technologies you haven't implemented.

### Git upload

After putting this into `README.md`:

```bash
git status
git add .
git commit -m "Complete AI Employee Assistant"
git push origin main
```

If Git reports that your local and remote branches have diverged again, **don't run random commands**—show me the exact output and we'll resolve it safely.