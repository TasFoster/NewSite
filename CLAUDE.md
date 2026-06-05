# CLAUDE.md

## Назначение

Это эталонный учебный проект на Django — **TicketManager** (командный таск-трекер).
Используется как образец: студенты пишут аналогичное приложение и прикладывают к нему
короткий отчёт. В этой же папке лежит **шаблон отчёта** для студентов (см. ниже).

## Стек

- Python 3, Django 6.0.5, база данных SQLite (`db.sqlite3`).
- Стандартная модель пользователя Django (кастомной нет; `accounts/models.py` пустой).
- Зависимости — `requirements.txt`.

## Запуск

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Приложение: http://127.0.0.1:8000/ . Логин: `/accounts/login/`, регистрация: `/accounts/signup/`.
`LOGIN_REDIRECT_URL = '/'` — дашборд.

## Структура

Проект `ticketmanager/` (settings, urls, wsgi/asgi) + три приложения:

- **accounts/** — регистрация. `SignUpView` (`CreateView`) на `/accounts/signup/`.
  Вход/выход — через встроенный `django.contrib.auth.urls`.
- **teams/** — команды и участники.
  - Модели: `Team` (name, description, captain, members M2M через `TeamMembership`),
    `TeamMembership` (team, user, role, joined_at; `unique_together = (team, user)`).
  - Вьюхи: `DashboardView`, `TeamCreateView`, `TeamDetailView`, `MembersView`,
    `AddMemberView`, `EditMembershipView`, `RemoveMembershipView`.
- **tickets/** — задачи.
  - Модель `Ticket`: team(FK), title, description, status, assignee, created_by,
    created_at/updated_at/completed_at.
  - Статусы (`Ticket.Status`): backlog → todo → in_progress → review → done.
    `Ticket.set_status()` сам проставляет/сбрасывает `completed_at` при переходе в/из `done`.
  - Вьюхи: `TicketCreateView`, `TicketDetailView`, `TicketEditView`,
    `TicketStatusView`, `TicketDeleteView`.

## Контроль доступа

`teams/permissions.py`:
- `is_captain(user, team)`, `is_member(user, team)` — хелперы.
- `TeamAccessMixin(LoginRequiredMixin)` — резолвит `self.team` из URL-kwarg `team_id`,
  требует членства в команде; при `captain_only = True` — только капитан. Иначе `PermissionDenied`.

Этот миксин используется во вьюхах teams и tickets для проверки прав.

## Шаблоны

`APP_DIRS = True` + общая папка `templates/` (`DIRS = [BASE_DIR/templates]`).
- Общие: `templates/base.html`, `templates/registration/login.html`, `templates/accounts/signup.html`.
- По приложениям: `teams/templates/teams/*.html`, `tickets/templates/tickets/*.html`.

## Заметки / соглашения

- `LANGUAGE_CODE = 'en-us'`, `TIME_ZONE = 'UTC'` (значения по умолчанию).
- Тесты (`*/tests.py`) пока пустые — тест-кейсов нет.
- Не git-репозиторий.

## Шаблон отчёта для студентов

- **`Шаблон_отчёта.docx`** — гибридный шаблон (~5–6 стр.), оформление под ГОСТ
  (Times New Roman 14, полуторный интервал, поля 3/1.5/2/2 см).
  - Полный титульный лист + разделы: 1) Цель и задачи, 2) Описание функционала,
    3) Структура и модели, 4) Использованные технологии *(заполнен как образец)*,
    5) Запуск проекта *(заполнен)*, 6) Скриншоты, 7) Выводы.
  - Подсказки-плейсхолдеры — серым курсивом в `[ … ]`; разделы «Распределение ролей»
    и «Список источников» намеренно не включены.
- **`make_report.py`** — генератор этого .docx (через `python-docx`). Чтобы изменить
  шаблон, правьте скрипт и запускайте `python make_report.py`.
