import time

from tools import TOOLS, CODE_EXECUTION_TOOLS, call_tool
from client import get_client

SYSTEM_PROMPT = "You are a helpful assistant with access to math tools. Use them to answer the user's questions."

CODE_EXECUTION_SYSTEM_PROMPT = """\
You are a helpful assistant with access to math tools. Use them to answer the user's questions.

If the `execute_python` tool is available, follow these rules:
- Always use it to solve the problem in a single call by composing functions together.
- Use only the provided functions: add(a, b), multiply(a, b), divide(a, b). Never use raw operators like +, -, *, / directly.
- Write the complete solution in one code block. Do not make multiple calls to execute_python.
- Store the final answer in a variable called `result`.
- Don't use any code comments or explanations, just the code itself. \
"""


def print_stats(
    llm_calls, tool_calls, input_tokens, output_tokens, total_tokens, latency
):
    print("\n============= STATS =============")
    print(f"\n  LLM calls:     {llm_calls}")
    print(f"  Tool calls:    {tool_calls}")
    print(f"  Input tokens:  {input_tokens}")
    print(f"  Output tokens: {output_tokens}")
    print(f"  Total tokens:  {total_tokens}")
    print(f"  Latency:       {latency:.2f} seconds")
    print("\n================================\n")


def run_agent(
    user_message: str, model: str = "gpt-4.1", code_execution: bool = False
) -> str:
    client = get_client()
    system_prompt = CODE_EXECUTION_SYSTEM_PROMPT if code_execution else SYSTEM_PROMPT
    tools = CODE_EXECUTION_TOOLS if code_execution else TOOLS
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    input_tokens = output_tokens = total_tokens = llm_calls = tool_calls = 0
    start = time.perf_counter()

    # Agent loop: keep calling the model until it produces a final response
    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )

        llm_calls += 1
        if response.usage:
            input_tokens += response.usage.prompt_tokens
            output_tokens += response.usage.completion_tokens
            total_tokens += response.usage.total_tokens

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            latency = time.perf_counter() - start
            print_stats(
                llm_calls,
                tool_calls,
                input_tokens,
                output_tokens,
                total_tokens,
                latency,
            )
            return message.content

        # Execute each tool call and append results
        for tool_call in message.tool_calls:
            tool_calls += 1
            print(
                f"  -> Calling tool: {tool_call.function.name}({tool_call.function.arguments})"
            )
            result = call_tool(tool_call.function.name, tool_call.function.arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )
