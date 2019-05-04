import argparse
import asyncio
import os
from typing import Optional

from dotenv import load_dotenv

from chat.client import ChatClientError
from chat.reader import ChatReader
from chat.writer import ChatWriter


def create_parser():
    parser = argparse.ArgumentParser(description='asyncio chat client')
    parser.add_argument('--host', type=str, help='Target host.')
    parser.add_argument('--port', type=int, help='Target port.')
    parser.add_argument('--history', help='Path to file to store chat history.')
    return parser


async def listen_chat(host: str, port: str, timeout: str, history_file_path: str):
    chat_client = ChatReader(host, port, timeout, history_file_path)
    connected = await chat_client.connect()
    while True:
        if not connected:
            connected = await chat_client.connect()
        else:
            try:
                await chat_client.read_message_from_stream()
            except ChatClientError:
                connected = False


async def send_message_to_chat(
        host: str,
        port: int,
        timeout: int,
        history_file_path: str,
        token: Optional[str],
        username: Optional[str]
):
    chat_client = ChatWriter(host, port, timeout, history_file_path)
    connected = await chat_client.connect()
    while True:
        if not connected:
            connected = await chat_client.connect()
        else:
            try:
                authenticated = await chat_client.authenticate(token)
            except ChatClientError:
                connected = False


def main():
    parser = create_parser()
    args = parser.parse_args()
    host = args.host or os.getenv('HOST')
    port = args.port or os.getenv('PORT')
    history_file_path = args.port or os.getenv('HISTORY')
    timeout = 5

    token = 'b4e3ecb4-6e76-11e9-944f-0242ac110002'
    username = None

    asyncio.run(send_message_to_chat(
        host,
        port,
        timeout,
        history_file_path,
        token=token,
        username=username
    ))


if __name__ == '__main__':
    load_dotenv()
    main()
