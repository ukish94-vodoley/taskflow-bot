from sqlalchemy import select, func
from sqlalchemy.orm import aliased

from database.database import SessionLocal
from models.finance import Finance
from models.user import User

from datetime import datetime, timedelta
from sqlalchemy import select
from models.finance import Finance


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


async def get_employee_history_for_period(
    employee_id: int,
    days: int | None = None,
):
    async with SessionLocal() as session:
        query = select(Finance).where(Finance.employee_id == employee_id)

        if days is not None:
            query = query.where(Finance.created_at >= datetime.utcnow() - timedelta(days=days))

        result = await session.execute(query.order_by(Finance.created_at.desc()))
        return result.scalars().all()


async def get_finance_report_data(days: int | None = None):
    async with SessionLocal() as session:
        Employee = aliased(User)
        Leader = aliased(User)
        query = (
            select(Finance, Employee.full_name, Leader.full_name)
            .join(Employee, Finance.employee_id == Employee.id)
            .join(Leader, Finance.leader_id == Leader.id)
        )
        if days is not None:
            query = query.where(Finance.created_at >= datetime.utcnow() - timedelta(days=days))
        result = await session.execute(query.order_by(Finance.created_at.desc()))
        return result.all()


async def get_last_week_report(employee_id: int | None = None):
    async with SessionLocal() as session:

        start_date = datetime.now() - timedelta(days=7)

        query = select(Finance).where(
            Finance.created_at >= start_date
        )

        if employee_id:
            query = query.where(
                Finance.employee_id == employee_id
            )

        query = query.order_by(
            Finance.created_at.desc()
        )

        result = await session.execute(query)

        return result.scalars().all()


async def get_last_month_report(employee_id: int | None = None):
    async with SessionLocal() as session:

        start_date = datetime.now() - timedelta(days=30)

        query = select(Finance).where(
            Finance.created_at >= start_date
        )

        if employee_id:
            query = query.where(
                Finance.employee_id == employee_id
            )

        query = query.order_by(
            Finance.created_at.desc()
        )

        result = await session.execute(query)

        return result.scalars().all()


async def get_month_report(
    year: int,
    month: int,
    employee_id: int | None = None,
):
    async with SessionLocal() as session:

        start_date = datetime(year, month, 1)

        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        query = select(Finance).where(
            Finance.created_at >= start_date,
            Finance.created_at < end_date,
        )

        if employee_id:
            query = query.where(
                Finance.employee_id == employee_id
            )

        query = query.order_by(
            Finance.created_at.desc()
        )

        result = await session.execute(query)

        return result.scalars().all()            
