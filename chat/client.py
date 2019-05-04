from abc import ABCMeta
import datetime
import asyncio
import socket

from aiofile import AIOFile, Writer


class ChatClientError(Exception):
    pass


class ChatClient(metaclass=ABCMeta):
    def __init__(self, host: str, port: int, timeout: int, history_file_path: str = None):
        self._host = host
        self._port = port
        self._connection_attempts = 0
        self._timeout = timeout
        self._history_file_path = history_file_path
        self._stream_reader = None
        self._stream_writer = None

    async def connect(self):
        try:

            self._stream_reader, self._stream_writer = await asyncio.wait_for(
                asyncio.open_connection(host=self._host, port=self._port), self._timeout
            )

            self._connection_attempts = 0

            message = f'Connection established to {self._host}:{self._port}.\n'
            await self._save_message_to_history(message)

            return True
        except (
                asyncio.TimeoutError,
                ConnectionRefusedError,
                ConnectionError,
                socket.gaierror,
        ) as e:

            self._connection_attempts += 1
            if self._connection_attempts > 2:
                message = f'No connection to {self._host}:{self._port}. Retry after 2 seconds.\n'
                seconds_to_wait = 2
            else:
                message = f'No connection to {self._host}:{self._port}.\n'
                seconds_to_wait = 0

            await asyncio.sleep(seconds_to_wait)
            await self._save_message_to_history(message)

            return False

    async def _save_message_to_history(self, message: str):
        if self._history_file_path is None:
            return

        timestamp = ''.join(
            ['[', datetime.datetime.now().strftime('%Y.%m.%d %H:%M'), ']']
        )
        message = ' '.join([timestamp, message])
        print(message)
        async with AIOFile(self._history_file_path, 'a') as afp:
            writer = Writer(afp)
            await writer(message)
            await afp.fsync()
