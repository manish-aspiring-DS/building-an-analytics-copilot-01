# Text-to-SQL Agent

This project is a Streamlit app that converts natural-language business questions into safe SQL queries against a Superstore orders dataset.

The app:
- takes a question from the user
- asks an LLM to generate SQL
- validates the SQL to ensure it is read-only
- runs the query against a DuckDB database
- returns the result as a DataFrame
- shows the generated SQL and validated SQL
- asks the LLM to explain the result in plain English

## Tech Stack

- Python
- Streamlit
- OpenAI API
- DuckDB
- pandas
- Python-dotenv

## Project Structure

```text
text_sql/
├── app.py
├── agent.py
├── database.py
├── requirements.txt
├── .env
├── data/
│   ├── Sample - Superstore.xls
│   └── superstore.duckdb
├── README.md
└── .venv/   (optional local environment)
```

## How it works

### 1. User enters a question
The Streamlit app in `app.py` collects a question from the user.

### 2. SQL is generated
`agent.py` sends a schema-aware prompt to the OpenAI model and asks it to return a SQL query.

The schema includes a single table:

- `orders`

The prompt explicitly restricts the model to:
- only use the `orders` table
- only return read-only queries
- avoid write operations
- use DuckDB-compatible SQL

### 3. SQL is validated
`database.py` validates the generated SQL before executing it.

It blocks unsafe SQL such as:
- `INSERT`
- `UPDATE`
- `DELETE`
- `DROP`
- `ALTER`
- `CREATE`
- other write operations

It also ensures the SQL starts with `SELECT` or `WITH` and adds a default `LIMIT 100` if one is missing.

### 4. Query is executed
The validated query runs against the DuckDB database using the `orders` table.

### 5. Result is returned
The app displays:
- the answer
- the DataFrame result
- the generated SQL
- the validated SQL

## Files

### `app.py`
This is the Streamlit UI.

It contains:
- page configuration
- the question input field
- the Run button
- result display
- expanded sections for generated SQL and validated SQL

### `agent.py`
This file contains the LLM orchestration logic.

It includes:
- `generate_sql(user_question)`
- `generate_answer(user_question, safe_sql, result)`
- `ask_agent(user_question)`

`ask_agent()`:
- generates SQL
- handles LLM connection, rate limit, and API errors
- validates and executes the SQL
- creates a natural-language answer from the result

### `database.py`
This file handles the database layer.

It contains:
- `create_database()`
- `validate_sql(sql)`
- `run_query(sql)`

The database is loaded from:
- `data/Sample - Superstore.xls`

Then it creates or updates:
- `data/superstore.duckdb`

## Setup

### 1. Create a virtual environment

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Set your OpenAI API key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

### 4. Run the app

```powershell
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Requirements

The project expects these Python packages:

```text
streamlit
python-dotenv
openai
pandas
duckdb
openpyxl
```

## Notes

- The app is designed for the Superstore orders dataset.
- SQL generation is based on a fixed schema context and is not a general-purpose database agent yet.
- Validation is strict and only allows read-only queries.
- The app is currently a prototype and uses a restricted schema and query pattern.

## Future Improvements

Possible enhancements:
- support multiple tables
- improve schema awareness
- allow SQL editing before execution
- add query history
- support more database backends
- add safer prompt and query validation layers
