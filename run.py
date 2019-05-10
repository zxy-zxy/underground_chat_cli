import argparse
import asyncio
import os
import sys
import logging

from dotenv import load_dotenv

from utils.logger_config import get_logger
from chat.client import ChatClient, ChatClientError
from utils.scenario import send_message_scenario, register_scenario, ScenarioError


def create_parser():
    parser = argparse.ArgumentParser(
        description='Minecraft chat which is built with asyncio.'
    )

    parser.add_argument(
        '--host', type=str, help='Target host.', default=os.getenv('HOST')
    )
    parser.add_argument(
        '--port', type=int, help='Target port.', default=os.getenv('PORT')
    )
    parser.add_argument(
        '--history',
        help='Path to file to store chat history.',
        default=os.getenv('HISTORY'),
    )

    parser.add_argument(
        '--timeout', help='Chat response timeout.', default=os.getenv('TIMEOUT')
    )

    subparsers = parser.add_subparsers(dest='command')

    listen_parser = subparsers.add_parser('listen', help='Listen chat.')

    message_sender_parser = subparsers.add_parser(
        'send', help='Send message with a valid auth token.'
    )
    message_sender_parser.add_argument(
        '--message',
        type=str,
        help='Message to send to server.',
        default=os.getenv('MESSAGE'),
    )
    message_sender_parser.add_argument(
        '--token', type=str, help='Authentication token.', default=os.getenv('TOKEN')
    )

    register_parser = subparsers.add_parser('register', help='Register a new account.')
    register_parser.add_argument(
        '--username',
        type=str,
        help='Your new account name.',
        default=os.getenv('USERNAME'),
    )
    return parser


async def initialize_connection(chat_client: ChatClient):
    attempts = 1
    attempts_limit_without_suspend = 2
    seconds_to_suspend = 2
    connected = await chat_client.connect()

    while not connected:
        if attempts > attempts_limit_without_suspend:
            sys.stdout.write(
                f'Cannot open the connection. Retry after {seconds_to_suspend} seconds.\n'
            )
            await asyncio.sleep(seconds_to_suspend)
        else:
            sys.stdout.write('Cannot open the connection. Retry.\n')

        connected = await chat_client.connect()
        attempts += 1


async def listen_chat(chat_client: ChatClient):
    await initialize_connection(chat_client)
    while True:
        try:
            await chat_client.read_message_from_stream()
        except ChatClientError:
            await initialize_connection(chat_client)
        except KeyboardInterrupt:
            sys.stdout.write('gently closing')
            break


async def process_scenario(chat_client: ChatClient, async_function: function, **kwargs):
    await initialize_connection(chat_client)
    while True:
        try:
            response = await async_function(chat_client, **kwargs)
            if response:
                sys.stdout.write(response)
                break
        except ChatClientError:
            await initialize_connection(chat_client)
        except ScenarioError as e:
            sys.stdout.write(f'{str(e)}')
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

    if not os.path.isfile(history_file_path):
        sys.stdout.write(f'File is not exists or cannot be open: {history_file_path}')
        sys.exit(1)

    chat_client = ChatClient(host, port, timeout, history_file_path, logger)

    try:

        if args.command == 'listen':
            asyncio.run(listen_chat(chat_client))
        elif args.command == 'register':
            async_function = register_scenario
            asyncio.run(
                process_scenario(chat_client, async_function, username=args.username)
            )
        elif args.command == 'send':
            async_function = send_message_scenario
            print(type(async_function))
            asyncio.run(
                process_scenario(
                    chat_client, async_function, token=args.token, message=args.message)
            )
        else:
            sys.stdout.write('Wrong command.')
            sys.exit(1)
    except KeyboardInterrupt as e:
        sys.stdout.write('gently closing\n')


if __name__ == '__main__':
    load_dotenv()
    main()
