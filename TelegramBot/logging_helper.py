from datetime import datetime
from sqlalchemy.orm import Session

from TelegramBot.data_base import Logging
from TelegramBot.enum_types import LogTypeEnum


def set_log(db: Session, log_type: LogTypeEnum, user_telegram_id: int, user_id: int, log_text: str):
    log = Logging(log_type=log_type,
                  log_date=datetime.now(),
                  user_telegram_id=user_telegram_id,
                  user_id=user_id,
                  log_text=log_text)
    db.add(log)
    db.commit()

def set_error_log(db: Session, user_telegram_id: int, user_id: int, log_text: str):
    set_log(db, LogTypeEnum.ERROR, user_telegram_id, user_id, log_text)

def set_warn_log(db: Session, user_telegram_id: int, user_id: int, log_text: str):
    set_log(db, LogTypeEnum.WARN, user_telegram_id, user_id, log_text)

def set_info_log(db: Session, user_telegram_id: int, user_id: int, log_text: str):
    set_log(db, LogTypeEnum.INFO, user_telegram_id, user_id, log_text)