import argparse
import asyncio
import os
import sys
import logging
from typing import Optional

from dotenv import load_dotenv

from logger_config import get_logger
from chat.client import ChatClient, ChatClientError
from scenario import (
    send_message_scenario,
    register_scenario,
    ScenarioError,
)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Minecraft chat which is built with asyncio.')

    parser.add_argument(
        '--host',
        type=str,
        help='Target host.',
        default=os.getenv('HOST')
    )
    parser.add_argument(
        '--port',
        type=int,
        help='Target port.',
        default=os.getenv('PORT')
    )
    parser.add_argument(
        '--history',
        help='Path to file to store chat history.',
        default=os.getenv('HISTORY')
    )

    parser.add_argument(
        '--timeout',
        help='Chat response timeout.',
        default=os.getenv('TIMEOUT')
    )

    subparsers = parser.add_subparsers(dest='command')

    listen_parser = subparsers.add_parser(
        'listen',
        help='Listen chat.'
    )

    message_sender_parser = subparsers.add_parser(
        'send',
        help='Send message with a valid auth token.'
    )
    message_sender_parser.add_argument(
        '--message',
        type=str,
        help='Message to send to server.',
        default=os.getenv('MESSAGE')
    )
    message_sender_parser.add_argument(
        '--token',
        type=str,
        help='Authentication token.',
        default=os.getenv('TOKEN')
    )

    register_parser = subparsers.add_parser(
        'register',
        help='Register a new account.'
    )
    register_parser.add_argument(
        '--username',
        type=str,
        help='Your new account name.',
        default=os.getenv('USERNAME')
    )
    return parser


async def listen_chat(chat_client: ChatClient):
    connected = await chat_client.connect()
    while True:
        if not connected:
            connected = await chat_client.connect()
        else:
            try:
                await chat_client.read_message_from_stream()
            except ChatClientError:
                connected = False
            except KeyboardInterrupt:
                sys.stdout.write('gently closing')
                break


async def process_scenario(chat_client: ChatClient, coroutine, **kwargs):
    connected = await chat_client.connect()
    while True:
        if not connected:
            connected = await chat_client.connect()
        else:
            try:
                response = await coroutine(chat_client, **kwargs)
                if response:
                    sys.stdout.write(response)
                    break
            except ChatClientError:
                connected = False
            except ScenarioError as e:
                sys.stdout.write(
                    f'{str(e)}'
                )
                break
            except KeyboardInterrupt:
                sys.stdout.write('gently closing')
                break


def main():
    parser = create_parser()
    args = parser.parse_args()
    host = args.host
    port = args.port
    history_file_path = args.history
    timeout = int(args.timeout)

    logger = get_logger('general_logger', logging.DEBUG)

    chat_client = ChatClient(
        host, port, timeout, history_file_path, logger
    )

    if args.command == 'listen':
        asyncio.run(listen_chat(chat_client))
    elif args.command == 'register':
        coroutine = register_scenario
        asyncio.run(process_scenario(chat_client, coroutine, username=args.username))
    elif args.command == 'send':
        coroutine = send_message_scenario
        asyncio.run(process_scenario(chat_client, coroutine, token=args.token, message=args.message))


if __name__ == '__main__':
    load_dotenv()
    main()
