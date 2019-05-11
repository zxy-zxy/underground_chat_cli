import datetime
import asyncio
import socket
from logging import Logger

from aiofile import AIOFile


class ChatClientError(Exception):
    pass


def seconds_to_suspend():
    seconds_counter = 0
    while True:
        if seconds_counter >= 2:
            yield 2
        else:
            yield 0
        seconds_counter += 1


class ChatClient:
    def __init__(
            self, host: str, port: int, timeout: int, history_file_path: str, logger: Logger
    ):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._history_file_path = history_file_path
        self._history_file_path_descriptor = None
        self._stream_reader = None
        self._stream_writer = None
        self._logger = logger

    async def __aenter__(self):

        if self._history_file_path:
            self._history_file_path_descriptor = await AIOFile(
                self._history_file_path, 'a')
            await self._history_file_path_descriptor.open()

        for seconds in seconds_to_suspend():

            try:
                self._stream_reader, self._stream_writer = await asyncio.wait_for(
                    asyncio.open_connection(host=self._host, port=self._port), self._timeout
                )

                message = f'Connection established to {self._host}:{self._port}.\n'
                await self._save_message_to_history(message)

                return self

            except (
                    asyncio.TimeoutError,
                    ConnectionRefusedError,
                    ConnectionError,
                    socket.gaierror,
            ) as e:
                message = (
                    'Cannot establish connection to {} {}'
                    '.An error occurred: {}\n'.format(self._host, self._port, str(e))
                )
                await self._save_message_to_history(message)

                self._logger.error(
                    f'Cannot open the connection. Retry after {seconds} seconds.'
                )

            if seconds:
                await asyncio.sleep(seconds)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._stream_writer.close()
        if self._history_file_path_descriptor:
            await self._history_file_path_descriptor.close()

    async def read_message_from_stream(self):
        if not self._stream_reader:
            raise ChatClientError('Stream reader has not been initialized properly.')

        try:

            data = await self._stream_reader.readline()

            message = data.decode('utf-8')

            if not message:
                return None

            await self._save_message_to_history(message)

            message = message.strip()

            self._logger.debug(f'receiver : {message}')

            return message

        except (ConnectionRefusedError, ConnectionError, ValueError) as e:
            raise ChatClientError(str(e))

    async def write_message_to_stream(self, message: str):

        sanitazed_message = message.replace('\n', '').strip()
        message_to_send = f'{sanitazed_message}\n\n'
        encoded_message = message_to_send.encode('utf-8')

        try:
            self._stream_writer.write(encoded_message)
            await self._stream_writer.drain()
            await self._save_message_to_history(f'You said: {sanitazed_message}\n')
            self._logger.debug(f'sender : {sanitazed_message}')
            return True

        except (asyncio.TimeoutError, ConnectionRefusedError, ConnectionError) as e:
            raise ChatClientError(str(e))

    async def _save_message_to_history(self, message: str):
        if not self._history_file_path_descriptor:
            return
        timestamp = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        timestamp = f'[{timestamp}]'
        message = f'{timestamp} {message}'
        await self._history_file_path_descriptor.write(message)
