import time
import traceback
from pydantic import BaseModel
import openai 
from django.db.models import TextChoices
import logging

logger = logging.getLogger(__name__)

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
    def parse_content(cls, user_prompt: str | list[dict], system_prompt: str | None=None, model: str = DEFAULT_MODEL):
        return prompt_to_type(user_prompt, cls, system_prompt=system_prompt or cls.system_prompt(), model=model)

def prompt_to_type(user_prompt: str | list[dict], output_type: GenerativeModel, system_prompt: str | None=None, model: str = DEFAULT_MODEL, workflow: str | None = None):
    from .models import Message
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

    start_time = time.time()

    response_object = None

    try:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            tools=[
                openai.pydantic_function_tool(output_type)
            ]
        )
        success = True
        refusal_reason = completion.choices[0].message.refusal
        response_object: output_type = completion.choices[0].message.tool_calls[0].function.parsed_arguments
        response = response_object.model_dump()
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
    except Exception as e:
        logger.error(f"Error parsing content: {e}")
        traceback.print_exc()
        success = False
        refusal_reason = str(e)
        response = None
        prompt_tokens = None
        completion_tokens = None

    end_time = time.time()
    duration = end_time - start_time

    Message.objects.create(
        openai_id=completion.id if success else None,
        model=model,
        content=user_prompt,
        success=success,
        refusal_reason=refusal_reason,
        response=response,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        duration=duration,
        workflow=workflow or output_type.__name__,
    )

    return response_object