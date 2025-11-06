from crispy_forms.layout import Button


class RoundIconButton(Button):
    def __init__(
        self,
        icon: str,
        wrapper_classes: str | None = None,
        field_classes: str | None = None,
        icon_classes: str | None = None,
        **kwargs,
    ):
        self.icon = icon
        self.wrapper_classes = wrapper_classes or "btn btn-primary btn-circle absolute bottom-2.5 right-2.5 z-100"
        self.field_classes = field_classes or "absolute inset-0 w-full h-full"
        self.icon_classes = (
            icon_classes or "icon absolute inset-0 flex items-center justify-center pointer-events-none"
        )
        super().__init__(name="submit", value="", **kwargs)
