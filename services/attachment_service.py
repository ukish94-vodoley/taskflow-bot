from sqlalchemy import select

from database.database import SessionLocal
from models.task_attachment import TaskAttachment


async def save_attachment(
    task_id: int,
    file_id: str,
    file_type: str,
    file_name: str = "",
):
    async with SessionLocal() as session:

        attachment = TaskAttachment(
            task_id=task_id,
            file_id=file_id,
            file_type=file_type,
            file_name=file_name,
        )

        session.add(attachment)

        await session.commit()

        await session.refresh(attachment)

        return attachment


async def get_task_attachments(task_id: int):
    async with SessionLocal() as session:

        result = await session.execute(
            select(TaskAttachment)
            .where(TaskAttachment.task_id == task_id)
            .order_by(TaskAttachment.id)
        )

        return result.scalars().all()


async def delete_attachment(attachment_id: int):
    async with SessionLocal() as session:

        attachment = await session.get(
            TaskAttachment,
            attachment_id,
        )

        if attachment is None:
            return False

        await session.delete(attachment)

        await session.commit()

        return True


async def count_attachments(task_id: int):
    async with SessionLocal() as session:

        result = await session.execute(
            select(TaskAttachment)
            .where(TaskAttachment.task_id == task_id)
        )

        return len(result.scalars().all())