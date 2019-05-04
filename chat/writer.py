import asyncio

from .client import ChatClientError
from .reader import ChatReader


class ChatWriter(ChatReader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def authenticate(self, token: str):
        greetings = await self.read_message_from_stream()

    async def _write_message_to_stream(self, message: str):

        encoded_message = message.encode('utf-8')

        try:
            await asyncio.wait_for(
                self._stream_writer.write(encoded_message),
                self._timeout
            )
            await self._stream_writer.drain()
            await self._save_message_to_history(f'You said: {message}')
            return True

        except (asyncio.TimeoutError, ConnectionRefusedError, ConnectionError) as e:
            raise ChatClientError
