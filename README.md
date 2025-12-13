# Kvit.ok

Коротко: простий Flask‑додаток для керування квитками/реєстраціями (інтерфейси: сторінки входу, реєстрації, дашборд). Проєкт містить серверну частину в `app.py`, шаблони у `templates/` та статичні файли у `static/`.

## Основні можливості

- Реєстрація та вхід користувача
- Адмінська панель та дашборд
- Завантаження файлів у `static/uploads/`
- Динамічний сидинг даних через `seed_dynamic.py`

## Швидкий старт (Windows)

1. Встановіть Python 3.10+ (якщо ще не встановлено).
2. Створіть та активуйте віртуальне середовище:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# або: .\.venv\Scripts\activate.bat  для cmd
```

3. Встановіть залежності:

```powershell
pip install -r requirements.txt
```

5. Ініціалізація даних (опційно):

```powershell
python seed_dynamic.py
```

6. Запуск додатку:

```powershell
python app.py
```

Відкрийте http://127.0.0.1:5000 у браузері.

## Структура проекту

- `app.py` — точка входу сервера Flask
- `requirements.txt` — перелік залежностей
- `seed_dynamic.py` — скрипт для наповнення/сидування даних
- `templates/` — HTML шаблони (`index.html`, `login.html`, `register.html`, `dashboard.html`, `admin.html`)
- `static/` — CSS, JS, завантаження і т.д. (`register.css`, `style.css`, `script.js`, `uploads/`)

Автор/Власник: MarianOseredchuk
