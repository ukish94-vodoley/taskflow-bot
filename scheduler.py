from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.task_service import get_uncompleted_tasks
from services.notification_service import send_reminder_notification

scheduler = AsyncIOScheduler()


async def reminder_job():
    try:
        data = await get_uncompleted_tasks()

        for telegram_id, info in data.items():
            await send_reminder_notification(
                telegram_id=telegram_id,
                employee_name=info["employee"],
                tasks=info["tasks"],
            )

    except Exception as e:
        print("Scheduler xatosi:", e)


def start_scheduler():

    scheduler.add_job(
        reminder_job,
        trigger="cron",
        hour=8,
        minute=0,
        id="reminder_08",
        replace_existing=True,
    )

    scheduler.add_job(
        reminder_job,
        trigger="cron",
        hour=11,
        minute=0,
        id="reminder_11",
        replace_existing=True,
    )

    scheduler.add_job(
        reminder_job,
        trigger="cron",
        hour=15,
        minute=0,
        id="reminder_15",
        replace_existing=True,
    )

    scheduler.add_job(
        reminder_job,
        trigger="cron",
        hour=18,
        minute=0,
        id="reminder_18",
        replace_existing=True,
    )

    scheduler.start()