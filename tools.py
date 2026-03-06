import json


def add(a: float, b: float) -> float:
    return a + b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def execute_python(code: str) -> str:
    """Execute LLM-generated Python code"""
    scope = {"__builtins__": {}, "add": add, "multiply": multiply, "divide": divide}
    try:
        print(f"  -> Executing code:\n{code}")
        exec(code, scope)
        result = scope.get("result", "No `result` variable found in code")
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


# Registry mapping tool names to their implementations
TOOL_FUNCTIONS = {
    "add": add,
    "multiply": multiply,
    "divide": divide,
    "execute_python": execute_python,
}

# Tool schemas for the OpenAI API
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "divide",
            "description": "Divide first number by second number",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Numerator"},
                    "b": {"type": "number", "description": "Denominator"},
                },
                "required": ["a", "b"],
            },
        },
    },
]


# Single-tool schema for code execution mode — LLM writes code instead of calling tools one by one
CODE_EXECUTION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": """
                "Execute Python code that uses the available math functions: "
                "add(a, b), multiply(a, b), divide(a, b). "
                "The code must store the final answer in a variable called `result`. "
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute. Must assign the final answer to `result`.",
                    },
                },
                "required": ["code"],
            },
        },
    },
]


def call_tool(name: str, arguments: str) -> str:
    """Execute a tool by name with JSON-encoded arguments and return the result as a string."""
    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        args = json.loads(arguments)
        result = func(**args)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})
