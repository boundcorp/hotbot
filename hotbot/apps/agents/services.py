from typing import Type
import openai 

client = openai.OpenAI()

def prompt_to_type(user_prompt: str, output_type: openai.BaseModel, system_prompt: str | None=None):
    messages = [
        {
            "role": "system",
            "content": system_prompt or output_type.__doc__,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=messages,
        tools=[
            openai.pydantic_function_tool(output_type)
        ]
    )
    return completion.choices[0].message.tool_calls[0].function.parsed_arguments