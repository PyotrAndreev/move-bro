import enum

class TrackerStatusEnum(str, enum.Enum):
    wait_for_courier = "Ждем пока путешественник отправится в путь"
    wait_for_courier_claiming = "Путешественник едет забирать посылку"
    in_travel = "Путешественник в пути"
    delivering = "Путешественник едет отдавать посылку"
    complete = "Доставлено"
    delay = "Путешественник задерживается"
    wrong_address = "Неверный адрес"
    cancelled = "Отменено"

class PaymentMethodEnum(str, enum.Enum):
    tmp = "bruh"
    #ToDo

class PaymentStatusEnum(str, enum.Enum):
    complete = "Оплачено"
    uncomplete = "Не оплачено"
    cancelled = "Отменено"
    error = "Ошибка оплаты"

class CourierStatusEnum(str, enum.Enum):
    inactive = "Неактивен"
    prepare = "Готовится к следующему путешествию"
    in_travel = "В пути"

class PackageStatusEnum(str, enum.Enum):
    no_courier = "Нет курьера"
    not_brought = "Есть курьер, но не забрана"
    in_process = "В пути"
    complete = "Доставлена"
    delayed = "Задерживается"
    error = "Возникли проблемы"

class SenderEnum(str, enum.Enum):
    courier = "Курьер"
    customer = "Клиент"
    none = "Неопределено"

class LogTypeEnum(str, enum.Enum):
    INFO = "Информация"
    WARN = "Предупреждение"
    ERROR = "Ошибка"
    FEEDBACK = "feedback"
    RESOLVED = "resolved"