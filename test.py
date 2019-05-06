import asyncio

import asynctest
import logging

from chat.client import ChatClient


def stream_reader_mock(host, port):
    reader = asynctest.mock.Mock(asyncio.StreamReader)
    writer = asynctest.mock.Mock(asyncio.StreamWriter)
    message = f'message from {host} {port}'
    reader.readline.return_value = message.encode()
    return reader, writer


def history_tracker_mixin_write_method_mock(history_file_path=None):
    return None


class TestChatClientReader(asynctest.TestCase):
    @asynctest.mock.patch('asyncio.open_connection', side_effect=stream_reader_mock)
    @asynctest.mock.patch(
        'chat.client.ChatClient._save_message_to_history',
        side_effect=history_tracker_mixin_write_method_mock,
    )
    async def test_one(self, open_connection_mock, writer_mock):
        host = 'host'
        port = 5000
        chat_reader_client = ChatClient(
            host,
            port,
            None,
            None,
            logging.getLogger(__file__)
        )
        connected = await chat_reader_client.connect()
        self.assertTrue(connected)
        message = await chat_reader_client.read_message_from_stream()
        self.assertEqual(message, f'message from {host} {port}')


if __name__ == '__main__':
    asynctest.main()
