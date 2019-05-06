import json

from chat.client import ChatClient


class ScenarioError(Exception):
    pass


async def send_message_scenario(chat_client: ChatClient, token: str, message: str):
    """
    Implementation of send_message_with_authentication_scenario scenario:
    1) Skip intro:
    Hello %username%! Enter your personal hash or
    leave it empty to create new account.
    2) Send token to server
    3) Confirm your are authenticated
    4) Skip greetings:
    Welcome to chat! Post your message below.
    End it with an empty line.
    5) Confirm your message was delivered.
    successful
    """
    await chat_client.read_message_from_stream()
    await chat_client.write_message_to_stream(token)
    auth_response = await chat_client.read_message_from_stream()
    if auth_response == 'null':
        raise ScenarioError(
            'Your authentication token is invalid. Confirm its valid or register a new one.'
        )
    await chat_client.read_message_from_stream()
    await chat_client.write_message_to_stream(message)
    response = await chat_client.read_message_from_stream()
    return response


async def register_scenario(chat_client: ChatClient, username: str) -> str:
    """Implementation of registration scenario:
    1)Skip intro.
    Hello %username%! Enter your personal hash or
    leave it empty to create new account.
    2) Send an empty message to server
    to server to begin registration procedure.
    3)Skip message:
    Enter preferred nickname below:
    4) Send preferred nickname to server
    5) Confirm your request has been proceeded.
    """
    await chat_client.read_message_from_stream()
    await chat_client.write_message_to_stream('')
    await chat_client.read_message_from_stream()
    await chat_client.write_message_to_stream(username)
    signup_response = await chat_client.read_message_from_stream()
    try:
        signup_data = json.loads(signup_response)
    except json.JSONDecodeError as e:
        raise ScenarioError(f'Cannot parse response from server: {str(e)}')
    try:
        signed_up_successfully = '''
        Your nickname is: {}
        Your account_hash is: {}
        '''.format(
            signup_data['nickname'], signup_data['account_hash']
        )
    except KeyError as e:
        raise ScenarioError(f'Cannot parse response from server: {str(e)}')
    return signed_up_successfully
