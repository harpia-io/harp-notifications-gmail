from logger.logging import service_logger
import traceback
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import harp_notifications_gmail.settings as settings
from harp_notifications_gmail.logic.gmail_processor import GmailNotifications

log = service_logger()

router = APIRouter(prefix=settings.URL_PREFIX)


class GmailNotification(BaseModel):
    recipients: list
    email_subject: str
    email_body: str


@router.post('/notifications/gmail')
async def create_notification(row_data: GmailNotification):
    """
    Create new notification
    """

    data = row_data.dict()

    try:
        notification = GmailNotifications(
            recipients=data['recipients'],
            email_subject=data['email_subject'],
            email_body=data['email_body'],
            email_user=data['email_user'] if 'email_user' in data else None,
            email_password=data['email_password'] if 'email_password' in data else None
        )
        status = notification.create_email()

        log.info(
            msg=f"Email notification has been sent to {data['recipients']}",
            extra={'tags': {}}
        )

        return status
    except Exception as err:
        log.error(
            msg=f"Can`t send Email notification \nException: {str(err)} \nTraceback: {traceback.format_exc()}",
            extra={'tags': {}})

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
