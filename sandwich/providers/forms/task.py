from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class AddTaskForm(forms.Form):
    def __init__(self, *args, available_forms: list[dict[str, str]], form_action: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        choices = [("", "Please select a form")]
        choices.extend([(form["id"], form["name"]) for form in available_forms])

        initial = None
        if len(available_forms) == 1:
            initial = choices[1]

        self.fields["selected_form"] = forms.ChoiceField(
            choices=choices,
            widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
            label="Select a form",
            required=True,
            initial=initial,
        )
        self.helper = FormHelper()
        self.helper.attrs["hx-post"] = form_action
        self.helper.attrs["hx-trigger"] = "submit"
        self.helper.attrs["hx-swap"] = "outerHTML"
        self.helper.attrs["hx-target"] = "dialog"

        self.helper.add_input(Submit("submit", "Assign task", css_class="btn-primary"))

        if form_action:
            self.helper.form_action = form_action
