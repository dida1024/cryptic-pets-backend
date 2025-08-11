from enum import Enum


class UserTypeEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
