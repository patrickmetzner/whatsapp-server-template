from fastapi.testclient import TestClient
from unittest.mock import patch

import app.main as main
from app.main import app

client = TestClient(app)


def test_receive_webhook_text_message():
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.test123",
                                    "from": "1234567890",
                                    "type": "text",
                                    "text": {"body": "hello world"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    with patch.object(main, "send_message") as mock_send:
        response = client.post("/webhook", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_send.assert_called()  # at least once
