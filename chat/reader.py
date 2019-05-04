import asyncio

from .client import ChatClient, ChatClientError


class ChatReader(ChatClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def read_message_from_stream(self):
        if not self._stream_reader:
            raise ChatClientError

        try:
            data = await asyncio.wait_for(self._stream_reader.readline(), self._timeout)
            message = data.decode()

            if not message:
                return None

            await self._save_message_to_history(message)
            return message

        except (asyncio.TimeoutError, ConnectionRefusedError, ConnectionError) as e:
            raise ChatClientError
