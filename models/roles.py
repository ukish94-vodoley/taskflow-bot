from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    LEADER = "leader"
    EMPLOYEE = "employee"