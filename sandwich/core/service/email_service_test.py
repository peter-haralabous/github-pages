import json
from unittest import mock

import pytest
from django.core import mail
from django.core.mail import EmailMessage

from sandwich.core.models import Email
from sandwich.core.models import Invitation
from sandwich.core.models import Patient
from sandwich.core.models.email import EmailStatus
from sandwich.core.models.email import EmailType
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.service.email_service import email_sent_post_process
from sandwich.core.service.email_service import handle_tracking
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

    # Verify X-Email-Id header is set correctly
    expected_header = f'{{"email_id": "{email_record.id}"}}'
    assert sent_email.extra_headers["X-Email-Id"] == expected_header


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
def test_send_email_handles_sending_exception() -> None:
    """Test that send_email handles exceptions during email sending and logs appropriately."""
    to = "test@example.com"
    subject = "Test Subject"
    body = "Test body content"

    with (
        mock.patch("sandwich.core.service.email_service.logger") as mock_logger,
        mock.patch.object(EmailMessage, "send", side_effect=Exception("SMTP Error")),
    ):
        send_email(to=to, subject=subject, body=body, email_type=EmailType.task)

        # Verify exception was logged
        mock_logger.exception.assert_called_once_with("Failed to send email", extra={"error_type": "Exception"})

        # Verify Email record was still created even though sending failed
        assert Email.objects.count() == 1


@pytest.mark.django_db
def test_send_email_sets_correct_message_headers() -> None:
    """Test that send_email sets correct message headers including X-Email-Id."""
    to = "test@example.com"
    subject = "Test Subject"
    body = "Test body content"

    send_email(to=to, subject=subject, body=body, email_type=EmailType.task)

    # Verify email was sent with correct headers
    assert len(mail.outbox) == 1
    sent_email = mail.outbox[0]

    # Verify X-Email-Id header format
    email_id_header = sent_email.extra_headers["X-Email-Id"]
    email_record = Email.objects.get()

    # Parse the JSON header to verify format
    header_data = json.loads(email_id_header)
    assert header_data["email_id"] == str(email_record.id)


@pytest.mark.django_db
def test_email_sent_post_process() -> None:
    # Create an Email record
    email = Email.objects.create(to="test@example.com", type=EmailType.task)

    # Mock the message object with X-Email-Id header as dictionary
    mock_message = mock.Mock()
    mock_message.extra_headers = {"X-Email-Id": f'{{"email_id": "{email.id}"}}'}

    # Mock recipient status
    mock_recipient_status = mock.Mock()
    mock_recipient_status.status = EmailStatus.SENT
    mock_recipient_status.message_id = "test-message-id-123"

    # Mock status object with recipients
    mock_status = mock.Mock()
    mock_status.recipients.items.return_value = [mock_recipient_status]

    # Call the function
    email_sent_post_process(sender=None, message=mock_message, status=mock_status, esp_name="Amazon SES")

    # Verify the Email record was updated
    email.refresh_from_db()
    assert email.status == EmailStatus.SENT
    assert email.message_id == "test-message-id-123"


@pytest.mark.django_db
def test_email_sent_post_process_handles_multiple_recipients() -> None:
    """Test that email_sent_post_process handles multiple recipients correctly with dict header."""
    # Create Email records
    email1 = Email.objects.create(to="test1@example.com", type=EmailType.task)

    # Mock the message object with X-Email-Id header as dictionary
    mock_message = mock.Mock()
    mock_message.extra_headers = {"X-Email-Id": f'{{"email_id": "{email1.id}"}}'}

    # Mock recipient statuses
    mock_recipient_status1 = mock.Mock()
    mock_recipient_status1.status = EmailStatus.SENT
    mock_recipient_status1.message_id = "message-id-1"

    mock_recipient_status2 = mock.Mock()
    mock_recipient_status2.status = EmailStatus.DELIVERED
    mock_recipient_status2.message_id = "message-id-2"

    # Mock status object with multiple recipients
    mock_status = mock.Mock()
    mock_status.recipients.items.return_value = [
        mock_recipient_status1,
        mock_recipient_status2,
    ]

    # Call the function
    email_sent_post_process(sender=None, message=mock_message, status=mock_status, esp_name="Amazon SES")

    # Verify both calls tried to update the same email record (email1)
    # Since we're using the same email_id in the header, both iterations will update email1
    email1.refresh_from_db()
    # The last update should be from the second recipient
    assert email1.status == EmailStatus.DELIVERED
    assert email1.message_id == "message-id-2"


@pytest.mark.django_db
def test_email_sent_post_process_handles_missing_x_email_id_header() -> None:
    """Test that email_sent_post_process handles missing X-Email-Id header gracefully."""
    # Create an Email record
    email = Email.objects.create(to="test@example.com", type=EmailType.task)

    # Mock the message object without X-Email-Id header
    mock_message = mock.Mock()
    mock_message.extra_headers = {}

    # Mock recipient status
    mock_recipient_status = mock.Mock()
    mock_recipient_status.status = EmailStatus.SENT
    mock_recipient_status.message_id = "test-message-id-123"

    # Mock status object
    mock_status = mock.Mock()
    mock_status.recipients.items.return_value = [("test@example.com", mock_recipient_status)]

    # Call the function - should not raise an exception
    email_sent_post_process(sender=None, message=mock_message, status=mock_status, esp_name="Amazon SES")

    # Verify the Email record was not updated (should still have default values)
    email.refresh_from_db()
    assert email.status == ""
    assert email.message_id == ""


@pytest.mark.django_db
def test_handle_tracking_updates_correct_email_record() -> None:
    """Test that handle_tracking updates the correct email record when bounce event is received."""
    # Create an Email record with a message_id
    email = Email.objects.create(
        to="test@example.com", type=EmailType.task, message_id="test-message-id-123", status=EmailStatus.SENT
    )

    # Mock the event object for bounced event
    mock_event = mock.Mock()
    mock_event.event_type = "bounced"
    mock_event.message_id = "test-message-id-123"
    mock_event.reject_reason = "Mailbox does not exist"

    # Call the function
    handle_tracking(sender=None, event=mock_event, esp_name="Amazon SES")

    # Verify the Email record was updated
    email.refresh_from_db()
    assert email.status == EmailStatus.BOUNCED


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
