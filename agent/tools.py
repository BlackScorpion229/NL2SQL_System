"""LangChain tool wrappers for MCP tools."""
from mcp_tools.summarize_results import summarize_results as mcp_summarize_results
from mcp_tools.execute_sql import execute_sql as mcp_execute_sql
from mcp_tools.generate_sql import generate_sql as mcp_generate_sql
from mcp_tools.get_schema import get_schema as mcp_get_schema
from typing import Dict, Any
from langchain.tools import tool
from loguru import logger

# Import MCP tools
import sys
sys.path.append('.')


@tool
def get_schema_tool(role: str = "admin") -> Dict[str, Any]:
    """
    Retrieve the database schema filtered by user role.

    Args:
        role: User role ('admin' or 'viewer') for schema filtering

    Returns:
        Dict containing tables and their column information.
    """
    return mcp_get_schema(role)


@tool
def generate_sql_tool(question: str, db_schema: str) -> str:
    """
    Convert a natural language question into a SQL query.

    This tool uses the database schema and LLM to generate safe, optimized SQL SELECT statements.
    It prevents generation of harmful SQL operations (UPDATE, DELETE, INSERT, etc.).

    Args:
        question: Natural language question to convert to SQL
        db_schema: Database schema information as JSON string from get_schema_tool

    Returns:
        Generated SQL query string
    """
    logger.info("LangChain tool: generate_sql_tool invoked")
    import json

    # Parse schema if it's a string
    if isinstance(db_schema, str):
        schema_dict = json.loads(db_schema)
    else:
        schema_dict = db_schema

    result = mcp_generate_sql(question, schema_dict)
    return result["sql"]


@tool
def execute_sql_tool(sql: str, role: str = "admin") -> str:
    """
    Safely execute a SQL query with automatic safety checks, LIMIT enforcement, and RBAC validation.

    This tool validates and executes SQL queries with safety features:
    - Rejects UPDATE, DELETE, INSERT, ALTER, DROP, and TRUNCATE operations
    - Automatically applies LIMIT 200 if not present
    - Validates table and column access based on user role
    - Returns structured results with column names and row data

    Args:
        sql: SQL query to execute (must be SELECT only)
        role: User role ('admin' or 'viewer') for access control

    Returns:
        JSON string containing query results with columns, rows, and row_count
    """
    logger.info("LangChain tool: execute_sql_tool invoked")
    import json

    result = mcp_execute_sql(sql, role)
    return json.dumps(result)


@tool
def summarize_results_tool(question: str, results: str) -> str:
    """
    Generate an intelligent, human-readable summary of query results.

    This tool analyzes query results and provides insights, patterns, trends, and business implications.
    Use this tool LAST to create the final answer for the user.

    Args:
        question: Original natural language question from the user
        results: Query results as JSON string from execute_sql_tool

    Returns:
        Natural language summary with insights
    """
    logger.info("LangChain tool: summarize_results_tool invoked")
    import json

    # Parse results
    results_dict = json.loads(results)

    summary_result = mcp_summarize_results(
        question=question,
        columns=results_dict["columns"],
        rows=results_dict["rows"],
        row_count=results_dict["row_count"]
    )

    return summary_result["summary"]


# Export all tools
LANGCHAIN_TOOLS = [
    get_schema_tool,
    generate_sql_tool,
    execute_sql_tool,
    summarize_results_tool
]
