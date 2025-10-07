import pytest
import hmac
import hashlib
import json
from unittest.mock import patch, Mock


class TestMessaging:
    """Test messaging and webhook functionality"""

    def test_hmac_signature_generation(self):
        """Test HMAC signature generation for Zapier webhooks"""
        from apps.worker.core.messaging import send_zapier_webhook

        # Mock the worker settings
        with patch('apps.worker.core.messaging.worker_settings') as mock_settings:
            mock_settings.ZAPIER_HMAC_SECRET = "test-secret"
            mock_settings.ZAPIER_MODE = "production"
            mock_settings.ZAPIER_CATCH_HOOK_URL = "https://test.zapier.com/hook"

            # Test payload
            payload = {"event": "test", "data": {"client_id": "123"}}
            payload_json = json.dumps(payload, separators=(',', ':'))

            # Calculate expected signature
            expected_signature = hmac.new(
                "test-secret".encode('utf-8'),
                payload_json.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Mock httpx client
            with patch('apps.worker.core.messaging.httpx.Client') as mock_client:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = "OK"
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response

                # Mock database operations
                with patch('apps.worker.core.messaging.create_webhook_record') as mock_create:
                    mock_webhook = Mock()
                    mock_webhook.id = "webhook-123"
                    mock_create.return_value = mock_webhook

                    with patch('apps.worker.core.messaging.update_webhook_success'):
                        # Call the function
                        result = send_zapier_webhook("test.event", {"client_id": "123"})

                        # Verify the call was made with correct headers
                        assert result is True
                        mock_client.return_value.__enter__.return_value.post.assert_called_once()
                        call_args = mock_client.return_value.__enter__.return_value.post.call_args

                        # Check that the signature header was included
                        headers = call_args[1]['headers']
                        assert 'X-Hook-Signature' in headers
                        assert headers['X-Hook-Signature'] == f'sha256={expected_signature}'

    def test_webhook_retry_logic(self):
        """Test webhook retry mechanism"""
        from apps.worker.core.messaging import update_webhook_failure

        # Mock database operations
        with patch('apps.worker.core.messaging.get_db') as mock_get_db:
            mock_db = Mock()
            mock_webhook = Mock()
            mock_webhook.attempt_count = 1

            mock_db.query.return_value.filter.return_value.first.return_value = mock_webhook
            mock_get_db.return_value = mock_db

            # Test failure update
            update_webhook_failure("webhook-123", "Connection timeout")

            # Verify attempt count was incremented
            assert mock_webhook.attempt_count == 2
            assert mock_webhook.last_error == "Connection timeout"

    def test_dev_mode_logging(self):
        """Test that dev mode logs instead of sending webhooks"""
        from apps.worker.core.messaging import send_zapier_webhook

        with patch('apps.worker.core.messaging.worker_settings') as mock_settings:
            mock_settings.ZAPIER_MODE = "dev_log"

            with patch('apps.worker.core.messaging.logger') as mock_logger:
                result = send_zapier_webhook("test.event", {"client_id": "123"})

                # Should return True but log instead of sending
                assert result is True
                mock_logger.info.assert_called()
                assert "DEV MODE" in str(mock_logger.info.call_args_list)

    def test_message_templates(self):
        """Test message template structure"""
        from apps.worker.core.messaging import MESSAGE_TEMPLATES

        # Verify all expected templates exist
        expected_templates = [
            'welcome_sms',
            'expiry_reminder',
            'checkin_reminder',
            'meetup_announcement'
        ]

        for template in expected_templates:
            assert template in MESSAGE_TEMPLATES
            assert isinstance(MESSAGE_TEMPLATES[template], str)
            assert len(MESSAGE_TEMPLATES[template]) > 0

        # Test template formatting for expiry reminder
        template = MESSAGE_TEMPLATES['expiry_reminder']
        formatted = template.format(name="John Doe", expires_on="2024-01-15")
        assert "John Doe" in formatted
        assert "2024-01-15" in formatted

    def test_webhook_record_creation(self):
        """Test webhook record database creation"""
        from apps.worker.core.messaging import create_webhook_record

        # Mock database and models
        with patch('apps.worker.core.messaging.get_db') as mock_get_db:
            with patch('apps.worker.core.messaging.WebhookOut') as mock_webhook_class:
                mock_db = Mock()
                mock_webhook = Mock()
                mock_webhook_class.return_value = mock_webhook
                mock_get_db.return_value = mock_db

                # Test record creation
                payload = {"event": "test", "data": {"client_id": "123"}}
                result = create_webhook_record("test.event", payload)

                # Verify webhook was created with correct data
                mock_webhook_class.assert_called_once()
                call_args = mock_webhook_class.call_args[1]
                assert call_args['event'] == "test.event"
                assert call_args['payload'] == payload
                assert 'status' in call_args
                assert call_args['attempt_count'] == 1

                # Verify database operations
                mock_db.add.assert_called_once_with(mock_webhook)
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once_with(mock_webhook)