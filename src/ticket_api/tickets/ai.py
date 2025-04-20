from typing import AsyncGenerator

from openai import AsyncOpenAI

from .schemas import MessageRead, TicketRead

from ..config import settings


class AIService:
    """Class to handle AI interactions for ticket responses.

    This class is responsible for generating prompts and streaming responses from the AI model.
    It utilizes the OpenAI API to create a chat completion based on the provided ticket and message history.
    OpenAI usage lets it work with different models that support similar interfaces.

    Attributes:
        client (AsyncOpenAI): An instance of the OpenAI API client for making requests.

    """

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
        )

    def build_prompt(
        self,
        ticket: TicketRead,
        message_history: list[MessageRead],
        last_customer_message: MessageRead | None = None,
    ) -> list[dict[str, str]]:
        """Prepares the prompt for the AI model.

        Args:
            ticket (TicketRead): The ticket object containing the issue description.
            message_history (list[MessageRead]): The history of messages exchanged in the ticket.
            last_customer_message (MessageRead | None): The last message from the customer, if not present, the ticket description is used.

        Returns:
            list[dict[str, str]]: A list of dictionaries representing the messages to be sent to the AI model.

        """

        ticket_description = ticket.description
        message_history_str = "\n".join(
            [
                f"{'Agent' if msg.is_ai else 'Customer'}: {msg.content}"
                for msg in message_history
            ]
        )
        last_customer_message_str = (
            f"Customer: {last_customer_message.content}"
            if last_customer_message
            else f"Customer: {ticket.description}"
        )

        return [
            {
                "role": "system",
                "content": "You're a friendly and knowledgeable customer support assistant.",
            },
            {
                "role": "user",
                "content": (
                    f"A customer is facing this issue: {ticket_description}\n\n"
                    f"Messages history: {message_history_str}\n\n"
                    f"Their latest message is: {last_customer_message_str}\n\n"
                    "Please craft a helpful and thoughtful response to assist them."
                ),
            },
        ]

    async def stream_response(
        self,
        prompt: list[dict[str, str]],
    ) -> AsyncGenerator[str, None]:
        """Streams the response from the AI model.

        It uses the OpenAI API to create a chat completion and yields the response chunks as they are received.

        Args:
            prompt (list[dict[str, str]]): The prompt to be sent to the AI model.

        Returns:
            AsyncGenerator[str, None]: An asynchronous generator that yields the response chunks.
        """

        stream = await self.client.chat.completions.create(
            messages=prompt,
            model="llama3-70b-8192",
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1.0,
            stop=None,
            stream=True,
        )

        async for chunk in stream:
            yield chunk.choices[0].delta.content
