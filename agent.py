import os
from dotenv import load_dotenv
from openai import OpenAI
import openai

from database import run_query

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SCHEMA_CONTEXT = """
You are working with one DuckDB table named orders.

Table: orders

Important columns:
- order_id
- order_date
- ship_date
- ship_mode
- customer_id
- customer_name
- segment
- country
- city
- state
- postal_code
- region
- product_id
- category
- sub_category
- product_name
- sales
- quantity
- discount
- profit

Rules:
- Only use the orders table.
- Generate only a single read-only SQL query.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or other write operations.
- Prefer simple DuckDB-compatible SQL.
- Always make a most optiimized query that returns only the necessary columns.
- Use GROUP BY when combining dimensions with aggregates.
- Do not add explanations, markdown, or code fences.
- Return only the SQL query text.
"""


def generate_sql(user_question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a text-to-SQL assistant. "
                    "Convert business questions into safe SQL queries. "
                    + SCHEMA_CONTEXT
                ),
            },
            {
                "role": "user",
                "content": user_question,
            },
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()
    return sql

def generate_answer(user_question: str, safe_sql: str, result) -> str:
    result_text = result.to_string(index=False)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a data analyst assistant. "
                    "Answer the user's question using  the SQL result provided. "
                    "Be concise and factual. "
                    "Do not invent values. "
                    "If the result is empty, say no matching data was found."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"User question:\n{user_question}\n\n"
                    f"Executed SQL:\n{safe_sql}\n\n"
                    f"SQL result:\n{result_text}"
                ),
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()



def ask_agent(user_question: str):
    try:
        sql = generate_sql(user_question)
    except openai.APIConnectionError:
        return {
            "question": user_question,
            "generated_sql": None,
            "safe_sql": None,
            "result": None,
            "answer": "Could not connect to the LLM service. Please check your internet connection and try again.",
            "error": "llm_connection_error",
        }
    except openai.RateLimitError:
        return {
            "question": user_question,
            "generated_sql": None,
            "safe_sql": None,
            "result": None,
            "answer": "The LLM service rate limit was reached. Please try again shortly.",
            "error": "llm_rate_limit_error",
        }
    except openai.APIStatusError as e:
        return {
            "question": user_question,
            "generated_sql": None,
            "safe_sql": None,
            "result": None,
            "answer": f"LLM request failed with status code {e.status_code}.",
            "error": "llm_api_status_error",
        }
    except Exception as e:
        return {
            "question": user_question,
            "generated_sql": None,
            "safe_sql": None,
            "result": None,
            "answer": f"Unexpected error while generating SQL: {str(e)}",
            "error": "sql_generation_error",
        }

    try:
        result, safe_sql = run_query(sql)
    except ValueError as e:
        return {
            "question": user_question,
            "generated_sql": sql,
            "safe_sql": None,
            "result": None,
            "answer": f"The generated SQL was blocked by validation: {str(e)}",
            "error": "sql_validation_error",
        }
    except Exception as e:
        return {
            "question": user_question,
            "generated_sql": sql,
            "safe_sql": None,
            "result": None,
            "answer": f"Database query failed: {str(e)}",
            "error": "sql_execution_error",
        }

    try:
        answer = generate_answer(user_question, safe_sql, result)
    except openai.APIConnectionError:
        answer = "The SQL ran successfully, but the explanation step could not connect to the LLM service."
    except openai.RateLimitError:
        answer = "The SQL ran successfully, but the explanation step hit a rate limit."
    except Exception as e:
        answer = f"The SQL ran successfully, but answer generation failed: {str(e)}"

    return {
        "question": user_question,
        "generated_sql": sql,
        "safe_sql": safe_sql,
        "result": result,
        "answer": answer,
        "error": None,
    }


if __name__ == "__main__":
    test_question = "Which region has the highest total sales?"
    response = ask_agent(test_question)
    print("Generated SQL:")
    print(response["generated_sql"])

    print("\nSafe SQL:")
    print(response["safe_sql"])

    print("\nResult:")
    print(response["result"])

    print("\nAnswer:")
    print(response["answer"])