from unittest import mock

import pytest
from anymail.message import AnymailMessage
from anymail.message import AnymailRecipientStatus
from anymail.signals import EventType
from django.core import mail

from sandwich.core.models import Email
from sandwich.core.models import Invitation
from sandwich.core.models import Patient
from sandwich.core.models.email import EmailStatus
from sandwich.core.models.email import EmailType
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.service.email_service import handle_tracking
from sandwich.core.service.email_service import record_email_delivery
from sandwich.core.service.email_service import send_email


@pytest.mark.django_db
def test_send_email_creates_entry_in_email_table() -> None:
    """Test that sending an email creates a database entry in the Email table."""
    to = "test@example.com"
    subject = "Test Subject"
    body = "Test body content"
    email_type = EmailType.task

    send_email(to=to, subject=subject, body=body, email_type=email_type)

    # Verify Email record was created
    email_records = Email.objects.all()
    assert len(email_records) == 1

    email_record = email_records[0]
    assert email_record.to == to
    assert email_record.type == email_type
    assert email_record.invitation is None


@pytest.mark.django_db
def test_send_email_successful_with_all_parameters(patient: Patient) -> None:
    """Test successful email sending with all parameters including invitation."""
    invitation = Invitation.objects.create(patient=patient)
    to = "test@example.com"
    subject = "Test Subject"
    body = "Test body content"
    email_type = EmailType.invitation

    send_email(to=to, subject=subject, body=body, email_type=email_type, invitation=invitation)

    # Verify email was sent
    assert len(mail.outbox) == 1
    sent_email = mail.outbox[0]
    assert sent_email.to == [to]
    assert sent_email.subject == subject
    assert sent_email.body == body
    assert sent_email.content_subtype == "html"

    # Verify Email record was created with invitation
    email_record = Email.objects.get()
    assert email_record.to == to
    assert email_record.type == email_type
    assert email_record.invitation == invitation


@pytest.mark.django_db
def test_send_email_with_empty_recipient() -> None:
    """Test that sending email with empty recipient logs warning and returns early."""
    with mock.patch("sandwich.core.service.email_service.logger") as mock_logger:
        send_email(to="", subject="Test", body="Test body", email_type=EmailType.task)

        # Verify warning was logged
        mock_logger.warning.assert_called_once_with(
            "Dropping email - no recipient specified", extra={"subject": "Test"}
        )

        # Verify no email was sent
        assert len(mail.outbox) == 0

        # Verify no Email record was created
        assert Email.objects.count() == 0


@pytest.mark.django_db
def test_send_email_with_none_recipient() -> None:
    """Test that sending email with None recipient logs warning and returns early."""
    with mock.patch("sandwich.core.service.email_service.logger") as mock_logger:
        send_email(to=None, subject="Test", body="Test body", email_type=EmailType.task)  # type: ignore[arg-type]

        # Verify warning was logged
        mock_logger.warning.assert_called_once_with(
            "Dropping email - no recipient specified", extra={"subject": "Test"}
        )

        # Verify no email was sent
        assert len(mail.outbox) == 0

        # Verify no Email record was created
        assert Email.objects.count() == 0


@pytest.mark.django_db
def test_record_email_delivery_with_anymail() -> None:
    to = "test@example.com"
    subject = "Test Subject"
    body = "Test body content"
    email_type = EmailType.task
    msg = AnymailMessage(
        subject=subject,
        body=body,
        from_email=None,
        to=[to],
    )
    msg.anymail_status.recipients = {
        "test@example.com": AnymailRecipientStatus(message_id="fake_message_id", status="sent")
    }

    with mock.patch("sandwich.core.service.email_service.ANYMAIL_INSTALLED", new=True):
        record_email_delivery(to=to, email_type=email_type, msg=msg)

    # Verify Email record was created even without message_id
    email_records = Email.objects.all()
    assert len(email_records) == 1

    email_record = email_records[0]
    assert email_record.to == to
    assert email_record.type == email_type
    assert email_record.message_id == "fake_message_id"
    assert email_record.status == EmailStatus.SENT
    assert email_record.invitation is None
    assert email_record.task is None


@pytest.mark.django_db
def test_send_email_handles_sending_exception() -> None:
    """Test that send_email handles exceptions during email sending and logs appropriately."""
    to = "test@example.com"
    subject = "Test Subject"
    body = "Test body content"

    with (
        mock.patch("sandwich.core.service.email_service.logger") as mock_logger,
        mock.patch.object(AnymailMessage, "send", side_effect=Exception("SMTP Error")),
    ):
        send_email(to=to, subject=subject, body=body, email_type=EmailType.task)

        mock_logger.exception.assert_called_once_with("Failed to send email", extra={"error_type": "Exception"})

        assert Email.objects.count() == 0


@pytest.mark.django_db
def test_handle_tracking_updates_correct_email_record() -> None:
    email = Email.objects.create(
        to="test@example.com", type=EmailType.task, message_id="test-message-id-123", status=EmailStatus.SENT
    )

    mock_event = mock.Mock()
    mock_event.event_type = EventType.BOUNCED
    mock_event.message_id = "test-message-id-123"
    mock_event.reject_reason = "Mailbox does not exist"

    # Call the function
    handle_tracking(sender=None, event=mock_event, esp_name="Amazon SES")

    # Verify the Email record was updated
    email.refresh_from_db()
    assert email.status == EmailStatus.BOUNCED


@pytest.mark.django_db
def test_handle_tracking_handles_delivered() -> None:
    email = Email.objects.create(
        to="test@example.com", type=EmailType.task, message_id="test-message-id-123", status=EmailStatus.SENT
    )

    mock_event = mock.Mock()
    mock_event.event_type = EventType.DELIVERED
    mock_event.message_id = "test-message-id-123"

    handle_tracking(sender=None, event=mock_event, esp_name="Amazon SES")

    # Verify the Email record was updated
    email.refresh_from_db()
    assert email.status == EmailStatus.DELIVERED


@pytest.mark.django_db
def test_handle_tracking_handles_complained() -> None:
    email = Email.objects.create(
        to="test@example.com", type=EmailType.task, message_id="test-message-id-123", status=EmailStatus.SENT
    )

    mock_event = mock.Mock()
    mock_event.event_type = EventType.COMPLAINED
    mock_event.message_id = "test-message-id-123"

    handle_tracking(sender=None, event=mock_event, esp_name="Amazon SES")

    # Verify the Email record was updated
    email.refresh_from_db()
    assert email.status == EmailStatus.COMPLAINED


@pytest.mark.django_db
def test_handle_tracking_updates_invitation_if_one_exists(patient: Patient) -> None:
    """Test that handle_tracking updates invitation status when email bounces and invitation exists."""
    # Create an invitation
    invitation = Invitation.objects.create(patient=patient, status=InvitationStatus.PENDING)

    # Create an Email record linked to the invitation
    email = Email.objects.create(
        to="test@example.com",
        type=EmailType.invitation,
        message_id="test-message-id-456",
        status=EmailStatus.SENT,
        invitation=invitation,
    )

    # Mock the event object for bounced event
    mock_event = mock.Mock()
    mock_event.event_type = "bounced"
    mock_event.message_id = "test-message-id-456"
    mock_event.reject_reason = "Mailbox does not exist"

    # Call the function
    handle_tracking(sender=None, event=mock_event, esp_name="Amazon SES")

    # Verify the Email record was updated
    email.refresh_from_db()
    assert email.status == EmailStatus.BOUNCED

    # Verify the Invitation record was updated to FAILED
    invitation.refresh_from_db()
    assert invitation.status == InvitationStatus.FAILED
