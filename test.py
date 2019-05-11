import asyncio

import asynctest
import logging

from chat.client import ChatClient


def open_connection_mock(host, port):
    reader = asynctest.mock.Mock(asyncio.StreamReader)
    writer = asynctest.mock.Mock(asyncio.StreamWriter)
    message = f'message from {host} {port}'
    reader.readline.return_value = message.encode()
    return reader, writer


def history_tracker_mixin_write_method_mock(history_file_path=None):
    return None


@asynctest.mock.patch('asyncio.open_connection', side_effect=open_connection_mock)
@asynctest.mock.patch(
    'chat.client.ChatClient._save_message_to_history',
    side_effect=history_tracker_mixin_write_method_mock,
)
class TestChatClient(asynctest.TestCase):
    async def setUp(self):
        self.host = 'host'
        self.port = 5000
        self.chat_reader_client = ChatClient(
            self.host, self.port, None, None, logging.getLogger(__file__)
        )

    async def test_chat_client_read_correct(
            self, open_connection_mock, save_message_to_history_mock
    ):
        async with self.chat_reader_client:
            message = await self.chat_reader_client.read_message_from_stream()
            self.assertEqual(message, f'message from {self.host} {self.port}')

    async def test_chat_client_write_correct(
            self, open_connection_mock, save_message_to_history_mock
    ):
        async with self.chat_reader_client:
            res = await self.chat_reader_client.write_message_to_stream('message')
            self.assertTrue(res)


if __name__ == '__main__':
    asynctest.main()
