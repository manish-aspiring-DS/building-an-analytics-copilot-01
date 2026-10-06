import duckdb
import pandas as pd

EXCEL_PATH = "data/Sample - Superstore.xls"
DATABASE_PATH = "data/superstore.duckdb"

# Create a DuckDB database from the Excel file
def create_database():
    orders_df = pd.read_excel(EXCEL_PATH, sheet_name="Orders")

    orders_df.columns = [
        column.strip().lower().replace(" ", "_").replace("-", "_")
        for column in orders_df.columns
    ]

    connection = duckdb.connect(DATABASE_PATH)

    connection.execute("DROP TABLE IF EXISTS orders")

    connection.register("orders_df", orders_df)

    connection.execute("""
        CREATE TABLE orders AS
        SELECT * FROM orders_df
    """)

    row_count = connection.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    print(f"Database created successfully with {row_count} rows.")

    connection.close()


# Validate SQL queries to ensure they are safe and read-only

def validate_sql(sql: str) -> str:
    cleaned_sql = sql.strip().lower()

    blocked_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "replace",
        "copy",
        "attach",
        "detach",
        "install",
        "load",
        "pragma",
    ]

    if not cleaned_sql.startswith(("select", "with")):
        raise ValueError("Only read-only SELECT queries are allowed.")

    for keyword in blocked_keywords:
        if keyword in cleaned_sql:
            raise ValueError(
                f"Unsafe SQL blocked because it contains: {keyword}"
            )

    if ";" in cleaned_sql[:-1]:
        raise ValueError("Multiple SQL statements are not allowed.")

    if "limit" not in cleaned_sql:
        cleaned_sql = cleaned_sql.rstrip(";") + " LIMIT 100"

    return cleaned_sql

# Run a validated SQL query against the DuckDB database
def run_query(sql: str):
    safe_sql = validate_sql(sql)

    connection = duckdb.connect(DATABASE_PATH)

    try:
        result = connection.execute(safe_sql).fetchdf()
        return result, safe_sql
    finally:
        connection.close()


# main function to create the database when the script is run directly
if __name__ == "__main__":
    create_database()