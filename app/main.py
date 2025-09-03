import os
import logging
import json
import requests
import time
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Query
from fastapi.responses import PlainTextResponse
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(filename)s:%(lineno)d] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

load_dotenv(override=True)

app = FastAPI()


WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_SERVER_NUMBER_ID = os.getenv("WHATSAPP_SERVER_NUMBER_ID")


def send_message(msg_text, recipient_number, reply_to=None):
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_SERVER_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "text",
        "text": {"body": msg_text},
    }

    if reply_to:
        payload["context"] = {"message_id": reply_to}

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    logger.info(f"{response.status_code}, {response.text}")


def download_media(media_id: str, save_path: Path):
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    media_url = resp.json()["url"]

    media_resp = requests.get(media_url, headers=headers, timeout=60)
    media_resp.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(media_resp.content)

    logger.info(f"Image saved to {save_path.resolve()}")


def run_long_routine(task_duration, from_number, msg_id):
    starting_routine_msg_text = f"Starting long routine for {task_duration} seconds"
    logger.info(starting_routine_msg_text)
    send_message(
        msg_text=starting_routine_msg_text, recipient_number=from_number, reply_to=None
    )  # Example of simple message

    time.sleep(task_duration)  # Simulate a long task

    completed_routine_msg_text = (
        f"Completed long routine.\nDuration: {task_duration} seconds"
    )
    logger.info(completed_routine_msg_text)
    send_message(
        msg_text=completed_routine_msg_text,
        recipient_number=from_number,
        reply_to=msg_id,
    )  # Example of response message


@app.get("/webhook", response_class=PlainTextResponse)
def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        return hub_challenge or ""  # must be plain text
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        incoming_payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    logger.info(f"Incoming payload: {incoming_payload}")

    for entry in incoming_payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])

            for msg in messages:
                msg_type = msg.get("type")

                for msg in messages:
                    msg_id = msg.get("id")  # Use it as reply_to in send_message
                    from_number = msg.get("from")

                    if msg_type == "text":
                        text = msg.get("text", {}).get("body")
                        confirmation_msg_text = (
                            f"Successfully received your text: {text}"
                        )

                        if text.lower().startswith("run long task:"):
                            task_duration = int(text.split(":")[-1].strip())
                            background_tasks.add_task(
                                run_long_routine,
                                task_duration=task_duration,
                                from_number=from_number,
                                msg_id=msg_id,
                            )
                    elif msg_type == "image":
                        image = msg.get("image", {})
                        media_id = image.get("id")
                        save_path = Path(f"{media_id}.jpg")
                        download_media(media_id=media_id, save_path=save_path)
                        confirmation_msg_text = (
                            f"Successfully received your image: {save_path}"
                        )

                    send_message(
                        msg_text=confirmation_msg_text,
                        recipient_number=from_number,
                        reply_to=msg_id,
                    )  # Example of response message

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
