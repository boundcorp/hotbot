from pydantic import BaseModel
import openai 
from django.db.models import TextChoices

class Models(TextChoices):
    LARGE = "gpt-4o-2024-08-06"
    SMALL = "gpt-4o-mini"

DEFAULT_MODEL = Models.SMALL

client = openai.OpenAI()

class GenerativeModel(BaseModel):
    @classmethod
    def system_prompt(cls):
        pass

    @classmethod
    def parse_content(cls, user_prompt: str, model: str = DEFAULT_MODEL):
        return prompt_to_type(user_prompt, cls, system_prompt=cls.system_prompt(), model=model)

def prompt_to_type(user_prompt: str, output_type: GenerativeModel, system_prompt: str | None=None, model: str = DEFAULT_MODEL):
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

    if model.upper() in [choice[0] for choice in Models.choices]:
        model = [choice[0] for choice in Models.choices if choice[0] == model.upper()][0]

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        tools=[
            openai.pydantic_function_tool(output_type)
        ]
    )
    return completion.choices[0].message.tool_calls[0].function.parsed_arguments