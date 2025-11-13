import itertools
import uuid
from collections.abc import Iterable

from langchain_core.language_models import BaseChatModel
from prompt_toolkit import print_formatted_text
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer
from prompt_toolkit.completion import WordCompleter

from sandwich.core.models import Patient
from sandwich.core.service.agent_service.config import configure
from sandwich.core.service.agent_service.memory import purge_thread
from sandwich.core.service.chat_service.chat import receive_chat_message
from sandwich.users.models import User

commands = {
    "exit": ["exit", "quit", "q"],
    "reset": ["reset", "clear", "startover"],
    "help": ["help", "h", "?"],
}


def cli_commands(effect: str | None = None) -> Iterable[str]:
    if effect:
        return commands.get(effect, [])
    return itertools.chain.from_iterable(commands.values())


def cli_completer() -> Completer:
    return WordCompleter(list(cli_commands()), ignore_case=True)


def action_for_command(param: str) -> str | None:
    param = param.lower().strip()
    for effect in commands:
        if param in cli_commands(effect):
            return effect
    return None


def cli_loop(model: BaseChatModel, user: User, patient: Patient) -> None:
    thread_id = f"{user.id}-{patient.id}"

    while True:
        user_response = prompt("> ", completer=cli_completer()).strip()
        if not user_response:
            continue
        if user_response.startswith("/"):
            command = user_response[1:].strip()
            match action_for_command(command):
                case "exit":
                    print_formatted_text("Bye!")
                    break
                case "reset":
                    purge_thread(thread_id)
                    print_formatted_text(f"Purged thread {thread_id}. History cleared.")
                    continue
                case "help":
                    print_formatted_text(
                        "Available commands:\n"
                        "/exit, /quit, /q - leave the chat\n"
                        "/reset, /clear, /startover - remove your history and start again\n"
                        "/help, /h, /? - show this help"
                    )
                    continue
                case _:
                    print_formatted_text(f"Unknown command: {command}. Type /help for list of commands.")
                    continue

        response = receive_chat_message(
            message_id=str(uuid.uuid4()),
            message=user_response,
            config=configure(thread_id),
            user=user,
            patient=patient,
            model=model,
        )
        print_formatted_text(response)
