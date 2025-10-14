import pytest

from sandwich.core.models import Task
from sandwich.core.service.invitation_service_test import mask_uuids
from sandwich.core.service.task_service import send_task_added_email


@pytest.mark.django_db
def test_send_task_added_email(template_fixture: None, task_wo_user: Task, mailoutbox, snapshot):
    send_task_added_email(task_wo_user)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [task_wo_user.patient.email]

    # if the template changes, the snapshot will need to be updated
    assert mask_uuids(mailoutbox[0].body) == snapshot
