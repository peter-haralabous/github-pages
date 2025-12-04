from typing import Protocol

from sandwich.core.management.lib.logging import LoggingMixin


class InputMixinProtocol(Protocol):
    def confirm(self, prompt: str) -> bool: ...


class InputMixin(LoggingMixin):
    def confirm(self, prompt: str) -> bool:
        return self.get_boolean(
            prompt=prompt,
            true_values={"Yes", "Y", "yes", "y"},
            false_values={"No", "N", "no", "n"},
        )

    def get_boolean(
        self,
        prompt: str = "",
        invalid_response: str = "Invalid response",
        true_values: set[str] | None = None,
        false_values: set[str] | None = None,
    ) -> bool:
        if true_values is None:
            true_values = {"True", "true", "TRUE", "T", "t", "1"}
        if false_values is None:
            false_values = {"False", "false", "FALSE", "F", "f", "0"}
        while True:
            self.info(prompt)
            response = input()
            if response in true_values:
                return True
            if response in false_values:
                return False
            self.warning(invalid_response)
