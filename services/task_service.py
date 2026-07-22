from datetime import datetime

from sqlalchemy import select

from database.database import SessionLocal
from models.task import Task


async def create_task(
    object_name: str,
    task_name: str,
    leader_id: int,
    employee_id: int,
    deadline: str,
    priority: str,
):
    async with SessionLocal() as session:

        task = Task(
            object_name=object_name,
            task_name=task_name,
            leader_id=leader_id,
            employee_id=employee_id,
            deadline=deadline,
            priority=priority,
        )

        session.add(task)

        await session.commit()

        await session.refresh(task)

        return task


async def get_tasks():
    async with SessionLocal() as session:

        result = await session.execute(
            select(Task).order_by(Task.id.desc())
        )

        return result.scalars().all()


async def get_task(task_id: int):
    async with SessionLocal() as session:

        return await session.get(Task, task_id)


async def save_task_result(
    task_id: int,
    photo: str,
    comment: str,
):
    async with SessionLocal() as session:

        task = await session.get(
            Task,
            task_id,
        )

        if task is None:
            return False

        task.photo = photo
        task.comment = comment
        task.status = "Tekshirilmoqda"
        task.completed_at = datetime.utcnow()

        await session.commit()

        return True


async def complete_task(task_id: int):
    async with SessionLocal() as session:

        task = await session.get(
            Task,
            task_id,
        )

        if task is None:
            return False

        task.status = "Bajarildi"
        task.completed_at = datetime.utcnow()

        await session.commit()

        return True


async def delete_task(task_id: int):
    async with SessionLocal() as session:

        task = await session.get(
            Task,
            task_id,
        )

        if task is None:
            return False

        await session.delete(task)

        await session.commit()

        return True

from sqlalchemy import or_
from models.user import User

async def search_tasks(query: str):
    async with SessionLocal() as session:
        q = query.strip()
        if not q:
            return []
        doc = q.upper().replace("DOC-", "").replace("DOC", "").lstrip("0")
        stmt = select(Task, User).join(User, Task.employee_id == User.id)
        if doc.isdigit():
            stmt = stmt.where(Task.id == int(doc))
        else:
            like = f"%{q}%"
            stmt = stmt.where(or_(
                Task.object_name.ilike(like),
                Task.task_name.ilike(like),
                Task.comment.ilike(like),
                Task.status.ilike(like),
                Task.deadline.ilike(like),
                Task.priority.ilike(like),
                User.full_name.ilike(like),
            ))
        stmt = stmt.order_by(Task.id.desc())
        rows = (await session.execute(stmt)).all()
        result = []
        for task, user in rows:
            result.append({
                "task_id": task.id,
                "doc": f"DOC-{task.id:06d}",
                "employee": user.full_name,
                "task": task.task_name,
                "status": task.status,
                "deadline": task.deadline,
                "priority": task.priority,
            })
        return result
    


async def get_uncompleted_tasks():
    async with SessionLocal() as session:

        stmt = (
            select(Task, User)
            .join(User, Task.employee_id == User.id)
            .where(Task.status == "Yangi")
            .order_by(User.id, Task.id)
        )

        rows = (await session.execute(stmt)).all()

        result = {}

        for task, user in rows:

            if user.telegram_id not in result:
                result[user.telegram_id] = {
                    "employee": user.full_name,
                    "tasks": [],
                }

            result[user.telegram_id]["tasks"].append(
                {
                    "id": task.id,
                    "object": task.object_name,
                    "task": task.task_name,
                    "deadline": task.deadline,
                    "priority": task.priority,
                }
            )

        return result