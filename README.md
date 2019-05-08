# Python [asyncio](https://docs.python.org/3/library/asyncio.html) based chat client.
Terminal chat-client for [devman](http://dvmn.org/) chat.
As of now client supports several operations:
* listen  - listen the chat.
* send - send new message to the chat.
* register - register a new account.

## Requirements
Python >= 3.7 is required.

Install dependencies with 
```bash
pip install -r requirements.txt
```
For better interaction is recommended to use [virtualenv](https://github.com/pypa/virtualenv).

## Usage

#### Tests
Run tests with 
```bash
python -m unittest 
```
#### Example
Configure .env file with needed parameters or provide them as arguments.
Example.env is provided within the repository.
```bash
python run.py --help
python run.py listen
```
