from datetime import datetime
from sqlalchemy.orm import Session

from TelegramBot.data_base import Logging
from TelegramBot.enum_types import LogTypeEnum


def get_log(db: Session, log_type: LogTypeEnum, log_date: datetime, user_telegram_id: int, user_id: int, log_text: str):
    log = Logging(log_type=log_type,
                  log_date=log_date,
                  user_telegram_id=user_telegram_id,
                  user_id=user_id,
                  log_text=log_text)
    db.add(log)
    db.commit()