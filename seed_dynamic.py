import random
import urllib.parse
from datetime import datetime, timedelta, date
from app import app, db, Event, User
from werkzeug.security import generate_password_hash

# --- НАЛАШТУВАННЯ ---
DAYS_TO_GENERATE = 30
LOCATIONS = [
    "Atlas", "Stereo Plaza", "Палац Спорту", 
    "ВДНГ", "Malevich", "Оперний театр", "Caribbean Club", "Підвал Культури", 
    "October Hall", "Osocor Residence", "Бочка-ПАБ", "Лофт"
]   


# --- БАЗА ДАНИХ (КОНСТРУКТОР) ---

# 1. СТЕНДАП (Реальні коміки)
STANDUP_COMEDIANS = [
    {"name": "Антон Тимошенко", "style": "Політичний стендап", "programs": ["Жартую", "На часі", "Пропаганда здорового глузду", "Підпільний виступ"]},
    {"name": "Василь Байдак", "style": "Абсурд та імпровізація", "programs": ["Довільне", "Комедія спостережень", "Сольний тур", "Історії з життя"]},
    {"name": "Настя Зухвала", "style": "Рафінована лють", "programs": ["Суто жіноче", "Про наболіле", "Новий матеріал", "Відверта розмова"]},
    {"name": "Фелікс Редька", "style": "Народний гумор", "programs": ["Золоті хіти", "Стендап в укритті", "Бамбарбія", "Стендап без кордонів"]},
    {"name": "Слава Бу", "style": "Експериментальний", "programs": ["Без цензури", "Чорний гумор", "Про стосунки", "Відкритий мікрофон"]},
    {"name": "Підпільний Стендап", "style": "Збірна вечірка", "programs": ["Найкраще", "Вечір перевірки матеріалу", "Improv Show", "Money Mic"]}
]
# Промпт для стендапу
STANDUP_PROMPT = "stand up comedy comedian on stage microphone spotlight brick wall dark club atmosphere laughing crowd"

# 2. МУЗИКА (Різні жанри)
MUSIC_GENRES = [
    {"name": "Jazz", "artists": ["Frank Sinatra Tribute", "Dennis Adu Quintet", "Smooth Operator Band", "Midnight Sax"], "adj": ["Вечірній", "Романтичний", "Джазовий", "Атмосферний"], "prompt": "jazz band saxophone smoky club warm lights elegant"},
    {"name": "Rock", "artists": ["O.Torvald", "Без Обмежень", "AC/DC Tribute", "Жадан і Собаки", "White Stripes Legacy"], "adj": ["Драйвовий", "Вибуховий", "Легендарний", "Гучний"], "prompt": "rock concert guitarist stage energetic crowd lights smoke electric guitar"},
    {"name": "Indie/Pop", "artists": ["Latexfauna", "Kola", "Blooms Corda", "Monatik", "Tember Blanche"], "adj": ["Чуттєвий", "Благодійний", "Акустичний", "Великий"], "prompt": "indie pop singer stage microphone soft lights aesthetic confetti"},
    {"name": "Electronic", "artists": ["DJ Tapolsky", "Techno Rave", "Artbat Sound", "Kolo Yolo"], "adj": ["Нічний", "Неоновий", "Футуристичний", "Безсонний"], "prompt": "techno party dj club neon lasers futuristic crowd dancing"}
]

# 3. ДІТЯМ ТА СІМ'Ї (Нова категорія)
KIDS_EVENTS = [
    {"title": "Цирк на льоду", "desc": "Неймовірне шоу для всієї родини! Акробати, жонглери та фігуристи у казкових костюмах.", "prompt": "circus ice skating magic show colorful lights kids happy"},
    {"title": "Наукове шоу 'Магія Хімії'", "desc": "Вибухові експерименти, рідкий азот та тесла-шоу. Пізнавально та весело для дітей від 6 років.", "prompt": "science show chemistry experiments laboratory kids amazed colorful smoke"},
    {"title": "Ляльковий театр: Котигорошко", "desc": "Класична українська казка у новому форматі. Інтерактивна вистава, де діти допомагають героям.", "prompt": "puppet theater stage fairy tale colorful dolls kids watching"},
    {"title": "Парк Динозаврів", "desc": "Виставка роботів-динозаврів у реальний розмір. Вони рухаються та гарчать! Фотозона включена.", "prompt": "dinosaur park realistic t-rex exhibition jungle kids adventure"}
]

# 4. АРТ ТА ВИСТАВКИ
EXHIBITIONS = [
    {"title": "Імерсивна виставка: Ван Гог", "desc": "Пориньте всередину картин генія. Проєкції на 360 градусів, класична музика та аромат кави.", "prompt": "van gogh starry night immersive exhibition digital art projections museum"},
    {"title": "Сучасне мистецтво: Ukraine Now", "desc": "Виставка молодих українських художників. Живопис, скульптура та digital-art.", "prompt": "modern art gallery abstract painting sculpture white room exhibition"},
    {"title": "Фотовиставка: Світ очима мандрівника", "desc": "Найкращі роботи National Geographic. Пейзажі, від яких перехоплює подих.", "prompt": "photo exhibition gallery framed photos nature travel museum visitors"}
]

# 5. ТЕАТР ТА КІНО (Залишили найкраще)
THEATER_AND_MOVIES = [
    {"type": "Театр", "title": "Конотопська відьма", "desc": "Містична драма за повістю Квітки-Основ'яненка. Аншлаг гарантовано.", "prompt": "theater stage mystic drama witch ukrainian folklore dark lighting"},
    {"type": "Театр", "title": "1984", "desc": "Антиутопія. Великий Брат стежить за тобою. Вистава, що змушує думати.", "prompt": "theater drama 1984 orwell dark spotlight actor"},
    {"type": "Кіно", "title": "Кінопоказ: Гаррі Поттер", "desc": "Марафон фільмів про магію. Попкорн та атмосфера Гоґвортсу.", "prompt": "cinema harry potter hogwarts magic movie screen cozy"},
    {"type": "Кіно", "title": "Дюна. Частина 2", "desc": "Епічна фантастика на найбільшому екрані міста (IMAX).", "prompt": "dune movie desert cinematic sci-fi screen cinema"}
]


# --- ГЕНЕРАТОР КАРТИНОК ---
def get_image(prompt):
    seed = random.randint(1, 1000000)
    # Додаємо стиль "Афіша", щоб виглядало професійно
    full_prompt = f"{prompt}, event poster style, high quality, 4k, artistic lighting --seed {seed}"
    encoded = urllib.parse.quote(full_prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=600&nologo=true"

# --- ФУНКЦІЇ-ГЕНЕРАТОРИ ---

def generate_standup():
    comedian = random.choice(STANDUP_COMEDIANS)
    program = random.choice(comedian["programs"])
    
    title = f"Стендап: {comedian['name']}"
    # Формуємо опис
    desc = f"Запрошуємо на вечір гумору! {comedian['name']} представляє програму «{program}». Стиль: {comedian['style']}. Гострий гумор, імпровізація та спілкування із залом. Частина коштів передається на ЗСУ."
    
    return {
        "title": title,
        "type": "Стендап", # Новий тип!
        "desc": desc,
        "image": get_image(STANDUP_PROMPT + " " + comedian['name']), # Додаємо ім'я в промпт для різноманіття
        "price": random.choice([300, 400, 500, 700])
    }

def generate_concert():
    genre = random.choice(MUSIC_GENRES)
    artist = random.choice(genre["artists"])
    adj = random.choice(genre["adj"])
    
    return {
        "title": f"{adj} концерт: {artist}",
        "type": "Концерт",
        "desc": f"Живий виступ у стилі {genre['name']}. {adj} атмосфера, якісний звук та улюблені хіти у виконанні {artist}. Не пропустіть головну музичну подію тижня!",
        "image": get_image(genre["prompt"]),
        "price": random.choice([350, 500, 800, 1200])
    }

def generate_kids():
    event = random.choice(KIDS_EVENTS)
    return {
        "title": event['title'],
        "type": "Дітям", # Новий тип
        "desc": event['desc'],
        "image": get_image(event['prompt']),
        "price": random.choice([150, 200, 300])
    }

def generate_exhibition():
    event = random.choice(EXHIBITIONS)
    return {
        "title": event['title'],
        "type": "Виставка",
        "desc": f"{event['desc']} Відкрийте для себе світ мистецтва. Працює гід та аудіогід.",
        "image": get_image(event['prompt']),
        "price": random.choice([100, 150, 250])
    }

def generate_mix():
    item = random.choice(THEATER_AND_MOVIES)
    return {
        "title": item['title'],
        "type": item['type'],
        "desc": item['desc'],
        "image": get_image(item['prompt']),
        "price": random.choice([200, 300, 600])
    }

# --- ГОЛОВНА ФУНКЦІЯ ---

def seed_dynamic():
    print(f"🎲 Генерую події на {DAYS_TO_GENERATE} днів (з Стендапами та дитячими подіями)...")
    
    # Видалення старих подій (розкоментуйте, якщо треба очистити базу)
    # try:
    #     db.session.query(Event).delete()
    #     db.session.commit()
    # except:
    #     db.session.rollback()

    current_date = date.today()
    total = 0

    # Список функцій-генераторів (ваги визначають частоту)
    # Стендапів і концертів буде більше, виставок менше
    generators = [
        generate_standup, generate_standup, # Подвійна ймовірність стендапу
        generate_concert, generate_concert, 
        generate_kids, 
        generate_exhibition, 
        generate_mix
    ]

    for _ in range(DAYS_TO_GENERATE):
        # Від 2 до 5 подій на день
        events_count = random.randint(2, 5)
        
        # Вибираємо випадкові типи подій на сьогодні
        todays_funcs = random.sample(generators, k=min(events_count, len(generators))) # Щоб не брати більше ніж є функцій

        for gen_func in todays_funcs:
            event_data = gen_func()
            
            # Рандомний вечірній час
            hour = random.choice([17, 18, 19, 20])
            minutes = random.choice(["00", "30"])

            event = Event(
                title=event_data["title"],
                date=current_date.strftime("%Y-%m-%d"),
                time=f"{hour}:{minutes}",
                location=random.choice(LOCATIONS),
                type=event_data["type"],
                price=event_data["price"],
                description=event_data["desc"],
                image_url=event_data["image"],
                total_seats=random.choice([100, 300, 500, 800]),
                remaining_seats=random.choice([100, 150, 200, 250, 300, 350, 400, 450, 500,])
            )
            db.session.add(event)
            total += 1
            print(f" [+] {event_data['title']}")

        current_date += timedelta(days=1)

    # Перевірка адміна
    if not User.query.filter_by(name="admin").first():
        hashed_pw = generate_password_hash("admin", method='pbkdf2:sha256')
        admin = User(name="admin", email="admin@kvitok.com", password=hashed_pw, role="admin")
        db.session.add(admin)
        print("👤 Адмін створений.")

    try:
        db.session.commit()
        print(f"\n✅ ГОТОВО! Створено {total} різноманітних подій.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Помилка: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_dynamic()