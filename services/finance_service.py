from sqlalchemy import select, func
from sqlalchemy.orm import aliased

from database.database import SessionLocal
from models.finance import Finance
from models.user import User


async def add_topup(
    employee_id: int,
    leader_id: int,
    amount: int,
    description: str = "",
):
    async with SessionLocal() as session:
        finance = Finance(
            employee_id=employee_id,
            leader_id=leader_id,
            task_id=None,
            type="topup",
            amount=amount,
            description=description,
        )

        session.add(finance)
        await session.commit()


async def add_expense(
    employee_id: int,
    leader_id: int,
    task_id: int | None,
    amount: int,
    description: str,
    photo: str = "",
):
    async with SessionLocal() as session:
        finance = Finance(
            employee_id=employee_id,
            leader_id=leader_id,
            task_id=task_id,
            type="expense",
            amount=amount,
            description=description,
            photo=photo,
        )

        session.add(finance)
        await session.commit()


async def get_employee_balance(employee_id: int):
    async with SessionLocal() as session:

        topup = await session.scalar(
            select(func.coalesce(func.sum(Finance.amount), 0)).where(
                Finance.employee_id == employee_id,
                Finance.type == "topup",
            )
        )

        expense = await session.scalar(
            select(func.coalesce(func.sum(Finance.amount), 0)).where(
                Finance.employee_id == employee_id,
                Finance.type == "expense",
            )
        )

        return topup - expense


async def get_all_balances():
    async with SessionLocal() as session:

        employees = (
            await session.execute(
                select(User).where(User.role == "employee")
            )
        ).scalars().all()

        balances = []

        for employee in employees:

            balance = await get_employee_balance(employee.id)

            balances.append(
                {
                    "employee": employee,
                    "balance": balance,
                }
            )

        return balances


async def get_leader_balances(leader_id: int):
    async with SessionLocal() as session:

        employees = (
            await session.execute(
                select(User).where(
                    User.role == "employee",
                    User.leader_id == leader_id,
                )
            )
        ).scalars().all()

        balances = []

        for employee in employees:

            balance = await get_employee_balance(employee.id)

            balances.append(
                {
                    "employee": employee,
                    "balance": balance,
                }
            )

        return balances


async def get_finance_history(limit: int = 50):
    async with SessionLocal() as session:

        Employee = aliased(User)
        Leader = aliased(User)

        result = await session.execute(
            select(
                Finance,
                Employee.full_name,
                Leader.full_name,
            )
            .join(
                Employee,
                Finance.employee_id == Employee.id,
            )
            .join(
                Leader,
                Finance.leader_id == Leader.id,
            )
            .order_by(Finance.created_at.desc())
            .limit(limit)
        )

        history = []

        for finance, employee_name, leader_name in result.all():

            history.append(
                {
                    "finance": finance,
                    "employee_name": employee_name,
                    "leader_name": leader_name,
                }
            )

        return history


async def get_employee_history(employee_id: int, limit: int = 20):
    async with SessionLocal() as session:

        result = await session.execute(
            select(Finance)
            .where(Finance.employee_id == employee_id)
            .order_by(Finance.created_at.desc())
            .limit(limit)
        )

        return result.scalars().all()

async def get_employee_finance_summary(employee_id: int):
    balance = await get_employee_balance(employee_id)
    history = await get_employee_history(employee_id, limit=10)
    return {
        "balance": balance,
        "history": history,
    }


async def create_edit_request(finance_id:int,new_amount:int,reason:str):
    return False

async def approve_edit_request(finance_id:int,leader_id:int):
    return False

async def reject_edit_request(finance_id:int,leader_id:int):
    return False
