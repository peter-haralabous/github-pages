from sandwich.providers.forms.task import AddTaskForm


def test_sets_initial_value_if_only_one_option() -> None:
    available_forms = [{"id": "form1", "name": "Test Form"}]
    form = AddTaskForm(available_forms=available_forms, form_action="/test/")

    assert form.fields["selected_form"].initial == ("form1", "Test Form")


def test_no_initial_value_with_multiple_options() -> None:
    available_forms = [{"id": "form1", "name": "First Form"}, {"id": "form2", "name": "Second Form"}]
    form = AddTaskForm(available_forms=available_forms, form_action="/test/")

    assert form.fields["selected_form"].initial is None


def test_initial_value_set_to_none_does_not_pass_validation() -> None:
    available_forms = [{"id": "form1", "name": "First Form"}, {"id": "form2", "name": "Second Form"}]
    form = AddTaskForm(available_forms=available_forms, form_action="/test/")

    assert form.is_valid() is False


def test_choices_include_all_available_forms() -> None:
    available_forms = [{"id": "form1", "name": "First Form"}, {"id": "form2", "name": "Second Form"}]
    form = AddTaskForm(available_forms=available_forms, form_action="/test/")

    choices = form.fields["selected_form"].choices  # type: ignore[attr-defined]
    assert len(choices) == 3  # placeholder + 2 forms
    assert choices[1] == ("form1", "First Form")
    assert choices[2] == ("form2", "Second Form")


def test_form_action_is_set() -> None:
    available_forms = [{"id": "form1", "name": "Test Form"}]
    form_action = "/providers/tasks/add/"
    form = AddTaskForm(available_forms=available_forms, form_action=form_action)

    assert form.helper.form_action == form_action


def test_selected_form_field_is_required() -> None:
    available_forms = [{"id": "form1", "name": "Test Form"}]
    form = AddTaskForm(available_forms=available_forms, form_action="/test/")

    assert form.fields["selected_form"].required is True


def test_selected_form_field_has_correct_widget_class() -> None:
    available_forms = [{"id": "form1", "name": "Test Form"}]
    form = AddTaskForm(available_forms=available_forms, form_action="/test/")

    widget_attrs = form.fields["selected_form"].widget.attrs
    assert widget_attrs["class"] == "select select-bordered w-full"
