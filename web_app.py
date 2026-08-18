import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from aiogram import Bot
from fastapi import BackgroundTasks, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import func, select

from config import BOT_TOKEN, WEB_SECRET_KEY
from database.database import SessionLocal
from database.init_db import init_db
from models.announcement import Announcement
from models.finance import Finance
from models.task import Task
from models.user import User
from models.web_login_code import WebLoginCode


ROOT = Path(__file__).resolve().parent
app = FastAPI(title="TaskFlow kabinet")
app.add_middleware(SessionMiddleware, secret_key=WEB_SECRET_KEY, same_site="lax", https_only=False)
app.mount("/static", StaticFiles(directory=ROOT / "web_static"), name="static")
templates = Jinja2Templates(directory=ROOT / "web_templates")


def normalize_phone(phone: str) -> str:
    digits = "".join(char for char in phone if char.isdigit())
    if digits.startswith("998"):
        return "+" + digits
    return phone.strip()


def redirect(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=303)


def notice(request: Request, message: str, kind: str = "success") -> None:
    request.session["notice"] = {"message": message, "kind": kind}


def csrf_token(request: Request) -> str:
    return request.session.setdefault("csrf_token", secrets.token_urlsafe(24))


def valid_csrf(request: Request, token: str) -> bool:
    expected = request.session.get("csrf_token", "")
    return bool(expected) and secrets.compare_digest(expected, token)


async def current_user(request: Request) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if user is None or not user.active:
            request.session.clear()
            return None
        return user


async def send_announcement_notifications(recipient_ids: list[int], title: str, body: str) -> None:
    if not recipient_ids:
        return
    async with SessionLocal() as session:
        recipients = (await session.execute(
            select(User).where(User.id.in_(recipient_ids), User.active == 1, User.telegram_id.is_not(None))
        )).scalars().all()
    bot = Bot(BOT_TOKEN)
    try:
        for recipient in recipients:
            try:
                await bot.send_message(recipient.telegram_id, f"📢 <b>{title}</b>\n\n{body}", parse_mode="HTML")
            except Exception:
                continue
    finally:
        await bot.session.close()


async def send_task_assignment_notification(telegram_id: int | None, task: Task) -> None:
    if not telegram_id:
        return
    bot = Bot(BOT_TOKEN)
    try:
        await bot.send_message(
            telegram_id,
            "🔔 <b>Sizga yangi vazifa biriktirildi</b>\n\n"
            f"🏢 Obyekt: {task.object_name}\n"
            f"📝 Vazifa: {task.task_name}\n"
            f"📅 Muddat: {task.deadline}\n"
            f"⚠️ Muhimlik: {task.priority}",
            parse_mode="HTML",
        )
    finally:
        await bot.session.close()


async def allowed_employees(user: User) -> list[User]:
    async with SessionLocal() as session:
        query = select(User).where(User.role == "employee", User.active == 1)
        if user.role == "leader":
            query = query.where(User.leader_id == user.id)
        elif user.role != "super_admin":
            query = query.where(User.id == user.id)
        return (await session.execute(query.order_by(User.full_name))).scalars().all()


async def employees_with_balances(user: User):
    employees = await allowed_employees(user)
    employee_ids = [employee.id for employee in employees]
    if not employee_ids:
        return []
    async with SessionLocal() as session:
        entries = (await session.execute(select(Finance).where(Finance.employee_id.in_(employee_ids)))).scalars().all()
    balances = {employee_id: 0 for employee_id in employee_ids}
    for entry in entries:
        balances[entry.employee_id] += entry.amount if entry.type == "topup" else -entry.amount
    return [{"employee": employee, "balance": balances[employee.id]} for employee in employees]


def render(request: Request, name: str, **context):
    context["user"] = context.get("user")
    context["csrf_token"] = csrf_token(request)
    context["notice"] = request.session.pop("notice", None)
    return templates.TemplateResponse(request, name, context)


@app.on_event("startup")
async def setup_database():
    await init_db()


@app.get("/")
async def dashboard(request: Request):
    user = await current_user(request)
    if user is None:
        return redirect("/login")

    async with SessionLocal() as session:
        announcements = (await session.execute(
            select(Announcement).where(Announcement.active == 1).order_by(Announcement.created_at.desc()).limit(5)
        )).scalars().all()
        balance = 0
        if user.role == "employee":
            topups = await session.scalar(select(func.coalesce(func.sum(Finance.amount), 0)).where(Finance.employee_id == user.id, Finance.type == "topup"))
            expenses = await session.scalar(select(func.coalesce(func.sum(Finance.amount), 0)).where(Finance.employee_id == user.id, Finance.type == "expense"))
            balance = topups - expenses
    return render(request, "dashboard.html", user=user, announcements=announcements, balance=balance)


@app.get("/login")
async def login_page(request: Request):
    if await current_user(request):
        return redirect("/")
    return render(request, "login.html")


@app.post("/login")
async def request_login_code(request: Request, phone: str = Form(...)):
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.phone == normalize_phone(phone), User.active == 1))
        if user is None or not user.telegram_id:
            notice(request, "Telefon raqam topilmadi yoki Telegram hali ulanmagan.", "error")
            return redirect("/login")

        code = f"{secrets.randbelow(1_000_000):06d}"
        session.add(WebLoginCode(
            user_id=user.id,
            code_hash=hashlib.sha256(code.encode()).hexdigest(),
            expires_at=datetime.utcnow() + timedelta(minutes=5),
        ))
        await session.commit()

    bot = Bot(BOT_TOKEN)
    try:
        await bot.send_message(user.telegram_id, f"TaskFlow kabinetiga kirish kodi: {code}\nKod 5 daqiqa amal qiladi.")
    except Exception:
        notice(request, "Kod yuborilmadi. Avval botga /start yuborganingizni tekshiring.", "error")
        return redirect("/login")
    finally:
        await bot.session.close()

    request.session["login_user_id"] = user.id
    return redirect("/verify")


@app.get("/verify")
async def verify_page(request: Request):
    if not request.session.get("login_user_id"):
        return redirect("/login")
    return render(request, "verify.html")


@app.post("/verify")
async def verify_login_code(request: Request, code: str = Form(...)):
    user_id = request.session.get("login_user_id")
    code_hash = hashlib.sha256(code.strip().encode()).hexdigest()
    if not user_id:
        return redirect("/login")

    async with SessionLocal() as session:
        login_code = await session.scalar(
            select(WebLoginCode).where(
                WebLoginCode.user_id == user_id,
                WebLoginCode.code_hash == code_hash,
                WebLoginCode.used_at.is_(None),
                WebLoginCode.expires_at > datetime.utcnow(),
            ).order_by(WebLoginCode.created_at.desc())
        )
        if login_code is None:
            notice(request, "Kod noto‘g‘ri yoki uning muddati tugagan.", "error")
            return redirect("/verify")
        login_code.used_at = datetime.utcnow()
        await session.commit()

    request.session.clear()
    request.session["user_id"] = user_id
    notice(request, "Kabinetga muvaffaqiyatli kirdingiz.")
    return redirect("/")


@app.post("/logout")
async def logout(request: Request, csrf: str = Form(...)):
    if valid_csrf(request, csrf):
        request.session.clear()
    return redirect("/login")


@app.get("/announcements")
async def announcements_page(request: Request):
    user = await current_user(request)
    if user is None:
        return redirect("/login")
    async with SessionLocal() as session:
        announcements = (await session.execute(select(Announcement).where(Announcement.active == 1).order_by(Announcement.created_at.desc()))).scalars().all()
    return render(request, "announcements.html", user=user, announcements=announcements, employees=await allowed_employees(user))


@app.get("/employees")
async def employees_page(request: Request):
    user = await current_user(request)
    if user is None:
        return redirect("/login")
    if user.role not in {"super_admin", "leader"}:
        notice(request, "Xodimlar ro‘yxati faqat rahbarlar uchun.", "error")
        return redirect("/")
    return render(request, "employees.html", user=user, items=await employees_with_balances(user))


@app.post("/announcements")
async def create_announcement(
    request: Request,
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    body: str = Form(...),
    send_to_all: str | None = Form(None),
    recipient_ids: list[int] = Form(default=[]),
    csrf: str = Form(...),
):
    user = await current_user(request)
    if user is None:
        return redirect("/login")
    if user.role not in {"super_admin", "leader"} or not valid_csrf(request, csrf):
        notice(request, "Bu amal uchun ruxsat yo‘q.", "error")
        return redirect("/announcements")
    if not title.strip() or not body.strip():
        notice(request, "E’lon sarlavhasi va matnini kiriting.", "error")
        return redirect("/announcements")
    employees = await allowed_employees(user)
    allowed_ids = {employee.id for employee in employees}
    selected_ids = list(allowed_ids) if send_to_all == "yes" else [employee_id for employee_id in recipient_ids if employee_id in allowed_ids]
    if not selected_ids:
        notice(request, "E’lon uchun kamida bitta xodimni tanlang.", "error")
        return redirect("/announcements")
    async with SessionLocal() as session:
        session.add(Announcement(title=title.strip()[:255], body=body.strip(), author_id=user.id))
        await session.commit()
    background_tasks.add_task(send_announcement_notifications, selected_ids, title.strip()[:255], body.strip())
    notice(request, f"E’lon joylandi va {len(selected_ids)} xodimga Telegram orqali yuborilmoqda.")
    return redirect("/announcements")


@app.get("/tasks")
async def tasks_page(request: Request):
    user = await current_user(request)
    if user is None:
        return redirect("/login")
    async with SessionLocal() as session:
        query = select(Task, User.full_name).join(User, Task.employee_id == User.id)
        if user.role == "leader":
            query = query.where(Task.leader_id == user.id)
        elif user.role == "employee":
            query = query.where(Task.employee_id == user.id)
        tasks = (await session.execute(query.order_by(Task.created_at.desc()))).all()
    employees = await allowed_employees(user) if user.role in {"super_admin", "leader"} else []
    return render(request, "tasks.html", user=user, tasks=tasks, employees=employees)


@app.post("/tasks")
async def create_task(
    request: Request,
    background_tasks: BackgroundTasks,
    object_name: str = Form(...),
    task_name: str = Form(...),
    employee_id: int = Form(...),
    deadline: str = Form(...),
    priority: str = Form(...),
    csrf: str = Form(...),
):
    user = await current_user(request)
    if user is None:
        return redirect("/login")
    if user.role not in {"super_admin", "leader"} or not valid_csrf(request, csrf):
        notice(request, "Bu amal uchun ruxsat yo‘q.", "error")
        return redirect("/tasks")
    if employee_id not in {employee.id for employee in await allowed_employees(user)}:
        notice(request, "Bu xodimga vazifa biriktira olmaysiz.", "error")
        return redirect("/tasks")
    async with SessionLocal() as session:
        employee = await session.get(User, employee_id)
        task = Task(
            object_name=object_name.strip()[:255], task_name=task_name.strip()[:1000],
            leader_id=user.id, employee_id=employee_id, deadline=deadline.strip()[:100],
            priority=priority, status="Yangi",
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
    background_tasks.add_task(send_task_assignment_notification, employee.telegram_id, task)
    notice(request, "Vazifa yaratildi va xodimga Telegram orqali yuborildi.")
    return redirect("/tasks")


@app.post("/tasks/{task_id}/status")
async def change_task_status(request: Request, task_id: int, status: str = Form(...), csrf: str = Form(...)):
    user = await current_user(request)
    if user is None:
        return redirect("/login")
    if not valid_csrf(request, csrf):
        notice(request, "Sahifa yangilangan. Qayta urinib ko‘ring.", "error")
        return redirect("/tasks")
    allowed = {"Tekshirilmoqda"} if user.role == "employee" else {"Bajarildi", "Qayta ishlashda"}
    if status not in allowed:
        notice(request, "Bu holatni o‘zgartirishga ruxsat yo‘q.", "error")
        return redirect("/tasks")
    async with SessionLocal() as session:
        task = await session.get(Task, task_id)
        if task is None or (user.role == "employee" and task.employee_id != user.id) or (user.role == "leader" and task.leader_id != user.id):
            notice(request, "Vazifa topilmadi yoki ruxsat yo‘q.", "error")
            return redirect("/tasks")
        task.status = status
        if status == "Bajarildi":
            task.completed_at = datetime.utcnow()
        await session.commit()
    notice(request, "Vazifa holati yangilandi.")
    return redirect("/tasks")


@app.get("/finance")
async def finance_page(request: Request):
    user = await current_user(request)
    if user is None:
        return redirect("/login")
    if user.role not in {"super_admin", "leader"}:
        notice(request, "Balans to‘ldirish faqat rahbarlar uchun.", "error")
        return redirect("/")
    return render(request, "finance.html", user=user, employees=await allowed_employees(user))


@app.post("/finance/topup")
async def add_balance(request: Request, employee_id: int = Form(...), amount: str = Form(...), description: str = Form(""), csrf: str = Form(...)):
    user = await current_user(request)
    if user is None:
        return redirect("/login")
    if user.role not in {"super_admin", "leader"} or not valid_csrf(request, csrf):
        notice(request, "Bu amal uchun ruxsat yo‘q.", "error")
        return redirect("/finance")
    try:
        value = int("".join(char for char in amount if char.isdigit()))
        if value <= 0:
            raise ValueError
    except ValueError:
        notice(request, "Summani musbat raqamda kiriting.", "error")
        return redirect("/finance")

    employees = await allowed_employees(user)
    if employee_id not in {employee.id for employee in employees}:
        notice(request, "Xodimni tanlashga ruxsatingiz yo‘q.", "error")
        return redirect("/finance")
    async with SessionLocal() as session:
        session.add(Finance(employee_id=employee_id, leader_id=user.id, task_id=None, type="topup", amount=value, description=description.strip()[:1000], status="approved"))
        await session.commit()
    notice(request, "Balans muvaffaqiyatli to‘ldirildi.")
    return redirect("/history")


@app.get("/history")
async def history_page(request: Request, employee_id: int | None = None):
    user = await current_user(request)
    if user is None:
        return redirect("/login")
    employees = await allowed_employees(user)
    if not employees:
        return render(request, "history.html", user=user, employees=[], selected_id=None, entries=[], balance=0)
    permitted = {employee.id for employee in employees}
    selected_id = employee_id if employee_id in permitted else (user.id if user.role == "employee" else None)
    async with SessionLocal() as session:
        query = select(Finance, User.full_name).join(User, Finance.employee_id == User.id)
        if selected_id is not None:
            query = query.where(Finance.employee_id == selected_id)
        else:
            query = query.where(Finance.employee_id.in_(permitted))
        rows = (await session.execute(query.order_by(Finance.created_at.desc()))).all()
    entries = [{"finance": finance, "employee_name": employee_name} for finance, employee_name in rows]
    balance = sum(item["finance"].amount if item["finance"].type == "topup" else -item["finance"].amount for item in entries)
    return render(request, "history.html", user=user, employees=employees, selected_id=selected_id, entries=entries, balance=balance)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="127.0.0.1", port=8000, reload=True)
