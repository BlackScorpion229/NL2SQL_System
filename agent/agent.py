"""LangChain agent setup with tool calling."""
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from loguru import logger
from pydantic import SecretStr
from app.config import settings
from agent.tools import LANGCHAIN_TOOLS
from mcp_tools.get_schema import get_schema as mcp_get_schema
import time
import json


class MySQLAnalyticalAgent:
    """MySQL Analytical Agent using LangChain with tool calling."""

    def __init__(self):
        """Initialize the agent with LLM and tools."""
        logger.info("Initializing MySQL Analytical Agent")

        # Initialize LLM with tools
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_ai_endpoint,
            api_key=SecretStr(settings.azure_ai_api_key),
            model=settings.azure_openai_deployment,
            api_version=settings.azure_ai_api_version,
            temperature=0,
            timeout=180.0  # 3 minute timeout for complex analytical queries
        )

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(LANGCHAIN_TOOLS)

        logger.info("Agent initialized successfully")

    def query(self, question: str, role: str = "admin") -> Dict[str, Any]:
        """
        Process a natural language question and return the analysis.

        Args:
            question: Natural language question about the database
            role: User role for RBAC filtering

        Returns:
            Dict containing:
            - answer: The summarized insights
            - execution_time: Time taken to process the query
            - reasoning_steps: Number of steps the agent took (for monitoring)
        """
        logger.info(f"Processing query: {question}")
        start_time = time.time()
        try:
            # 1. Mandatory Schema Preloading
            # Fetch RBAC-filtered schema before planning starts
            schema_dict = mcp_get_schema(role)
            schema_str = json.dumps(schema_dict, indent=2)

            # System message with injected schema
            system_msg = SystemMessage(content=f"""You are a MySQL analytical agent for an Indian-based application. 
            
CURRENT USER ROLE: {role}

ALLOWED DATABASE SCHEMA:
```json
{schema_str}
```

WORKFLOW - Follow these steps IN ORDER:
1. REVIEW the schema above. You MUST ONLY use tables and columns listed there.
2. Call generate_sql_tool(question, db_schema) to convert the question to SQL.
   - Pass the schema JSON provided above as the 'db_schema' argument.
3. Call execute_sql_tool(sql, role='{role}') to run the query with RBAC validation.
4. Call summarize_results_tool(question, results) to create insights.

IMPORTANT RULES:
- STRICTLY RESPECT THE SCHEMA. Do not guess table names like 'sales' or 'users' if they are not in the JSON above.
- If the information is not in the schema, answer "I cannot answer that with the available data."
- Use previous tool outputs for subsequent steps.
- All monetary values in Indian Rupees (₹).
- Use Indian number system (lakhs, crores).""")

            human_msg = HumanMessage(content=question)

            messages = [system_msg, human_msg]
            steps = 0
            max_iterations = 10

            # Agent loop - call tools until we get a final answer
            while steps < max_iterations:
                response = self.llm_with_tools.invoke(messages)
                steps += 1

                # Check if there are tool calls
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    messages.append(response)

                    # Execute each tool call
                    for tool_call in response.tool_calls:
                        tool_name = tool_call['name']
                        tool_args = tool_call['args']

                        logger.info(f"Calling tool: {tool_name}")

                        # Find and execute the tool
                        tool = next(
                            (t for t in LANGCHAIN_TOOLS if t.name == tool_name), None)
                        if tool:
                            try:
                                tool_result = tool.invoke(tool_args)

                                # Add tool result to messages
                                messages.append(ToolMessage(
                                    content=str(tool_result),
                                    tool_call_id=tool_call['id']
                                ))
                            except Exception as e:
                                logger.error(f"Tool {tool_name} failed: {e}")
                                messages.append(ToolMessage(
                                    content=f"Error: {str(e)}",
                                    tool_call_id=tool_call['id']
                                ))
                else:
                    # No more tool calls - we have the final answer
                    final_answer = response.content
                    execution_time = time.time() - start_time

                    return {
                        "answer": final_answer,
                        "execution_time": round(execution_time, 2),
                        "reasoning_steps": steps
                    }

            # Max iterations reached
            execution_time = time.time() - start_time
            return {
                "answer": "I reached the maximum number of steps without completing the analysis. Please try a simpler question.",
                "execution_time": round(execution_time, 2),
                "reasoning_steps": steps,
                "error": "Max iterations reached"
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query processing failed: {e}")

            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "execution_time": round(execution_time, 2),
                "reasoning_steps": 0,
                "error": str(e)
            }

    def query_stream(self, question: str, role: str = "admin"):
        """
        Process a natural language question and yield streaming events.

        Yields events for:
        - Reasoning step start (tool being called)
        - Reasoning step complete (tool result)
        - Final answer chunks (for streaming display)

        Args:
            question: Natural language question about the database

        Yields:
            Dict events with types: 'step_start', 'step_complete', 'answer_chunk', 'done', 'error'
        """
        logger.info(f"Processing streaming query: {question}")
        start_time = time.time()

        try:
            # System message with workflow instructions and role awareness
            system_msg = SystemMessage(content=f"""You are a MySQL analytical agent for an Indian-based application. 

WORKFLOW - Follow these steps IN ORDER:
1. Call get_schema_tool(role='{role}') to get the database schema filtered by user permissions
2. Call generate_sql_tool(question, db_schema) to convert the question to SQL
3. Call execute_sql_tool(sql, role='{role}') to run the query with RBAC validation
4. Call summarize_results_tool(question, results) to create insights

IMPORTANT:
- Complete ALL 4 steps
- Use tool results from previous steps as inputs to next steps
- Your final response must be the summary from step 4
- All monetary values should be in Indian Rupees (₹)
- Use Indian number system (thousands, lakhs, crores) not millions/billions
- Respect the schema provided - do not reference tables or columns not in the schema""")

            human_msg = HumanMessage(content=question)

            messages = [system_msg, human_msg]
            steps = 0
            max_iterations = 10

            # Map tool names to user-friendly step names
            step_names = {
                'get_schema_tool': 'Getting Database Schema',
                'generate_sql_tool': 'Generating SQL Query',
                'execute_sql_tool': 'Executing Query',
                'summarize_results_tool': 'Analyzing Results'
            }

            # Capture query results for visualization
            last_query_results = None

            # Agent loop - call tools until we get a final answer
            while steps < max_iterations:
                response = self.llm_with_tools.invoke(messages)
                steps += 1

                # Check if there are tool calls
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    messages.append(response)

                    # Execute each tool call
                    for tool_call in response.tool_calls:
                        tool_name = tool_call['name']
                        tool_args = tool_call['args']

                        # Emit step start event
                        yield {
                            'type': 'step_start',
                            'step_name': step_names.get(tool_name, tool_name),
                            'tool_name': tool_name,
                            'step_number': steps
                        }

                        logger.info(f"Calling tool: {tool_name}")

                        # Find and execute the tool
                        tool = next(
                            (t for t in LANGCHAIN_TOOLS if t.name == tool_name), None)
                        if tool:
                            try:
                                tool_result = tool.invoke(tool_args)

                                # Capture query results if this is execute_sql_tool
                                if tool_name == 'execute_sql_tool':
                                    try:
                                        # Parse the result if it's JSON-like
                                        if isinstance(tool_result, str):
                                            last_query_results = json.loads(tool_result)
                                        else:
                                            last_query_results = tool_result
                                    except:
                                        last_query_results = tool_result

                                # Emit step complete event
                                yield {
                                    'type': 'step_complete',
                                    'step_name': step_names.get(tool_name, tool_name),
                                    'tool_name': tool_name,
                                    'step_number': steps,
                                    'status': 'success',
                                    'tool_result': str(tool_result)
                                }

                                # Add tool result to messages
                                messages.append(ToolMessage(
                                    content=str(tool_result),
                                    tool_call_id=tool_call['id']
                                ))
                            except Exception as e:
                                logger.error(f"Tool {tool_name} failed: {e}")

                                # Emit error event for this step
                                yield {
                                    'type': 'step_complete',
                                    'step_name': step_names.get(tool_name, tool_name),
                                    'tool_name': tool_name,
                                    'step_number': steps,
                                    'status': 'error',
                                    'error': str(e)
                                }

                                messages.append(ToolMessage(
                                    content=f"Error: {str(e)}",
                                    tool_call_id=tool_call['id']
                                ))
                else:
                    # No more tool calls - we have the final answer
                    final_answer = response.content
                    if isinstance(final_answer, list):
                        final_answer = ' '.join(
                            str(item) for item in final_answer if isinstance(item, str))
                    execution_time = time.time() - start_time

                    # Stream the answer in chunks (split by sentences or words)
                    words = final_answer.split(' ')
                    for i, word in enumerate(words):
                        yield {
                            'type': 'answer_chunk',
                            'content': word + (' ' if i < len(words) - 1 else '')
                        }

                    # Emit done event with query results for visualization
                    done_event = {
                        'type': 'done',
                        'execution_time': round(execution_time, 2),
                        'reasoning_steps': steps
                    }
                    
                    # Include query results if available
                    if last_query_results:
                        done_event['data'] = last_query_results
                        logger.info(f"Sending {len(last_query_results) if isinstance(last_query_results, list) else '?'} result rows to frontend")
                    
                    yield done_event
                    return

            # Max iterations reached
            execution_time = time.time() - start_time
            yield {
                'type': 'error',
                'error': 'Max iterations reached',
                'execution_time': round(execution_time, 2),
                'reasoning_steps': steps
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Streaming query processing failed: {e}")

            yield {
                'type': 'error',
                'error': str(e),
                'execution_time': round(execution_time, 2),
                'reasoning_steps': 0
            }


# Global agent instance (initialized on first use)
_agent_instance = None


def get_agent() -> MySQLAnalyticalAgent:
    """
    Get or create the global agent instance.

    Returns:
        MySQLAnalyticalAgent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = MySQLAnalyticalAgent()
    return _agent_instance


if __name__ == "__main__":
    # Test the agent
    agent = get_agent()

    test_question = "How many records are in the database?"
    result = agent.query(test_question)

    print("\n" + "="*80)
    print("ANSWER:")
    print(result["answer"])
    print(f"\nExecution Time: {result['execution_time']}s")
    print(f"Reasoning Steps: {result['reasoning_steps']}")
    print("="*80)
