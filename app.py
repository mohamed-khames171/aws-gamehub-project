import psycopg2
from flask import Flask, render_template_string, request

app = Flask(__name__)

DB_CONFIG = {
    "host": "database-1.c6re2gqeyhhy.us-east-1.rds.amazonaws.com",
    "database": "game_hub",
    "user": "mohamed",
    "password": "YOUR_PASSWORD_HERE",
    "port": "5432",
    "sslmode": "require",
}

# قائمة كروت الشاشة الشائعة ومُعامل قوتها مقارنة بـ (Base Tier)
GPU_TIERS = {
    "NVIDIA T1200 Laptop (4GB)": 1.0,
    "NVIDIA GTX 1650 (4GB)": 0.95,
    "NVIDIA RTX 3050 Laptop / Desktop (4GB/6GB)": 1.45,
    "NVIDIA RTX 2060 (6GB)": 1.6,
    "NVIDIA RTX 3060 (12GB / Laptop)": 2.1,
    "NVIDIA RTX 4060 (8GB)": 2.7,
    "AMD Radeon RX 6600 (8GB)": 2.0,
    "Intel Iris Xe Graphics (Integrated)": 0.35,
}

# قائمة الألعاب ومعدل الفريمات الأساسي عند دقة 1080p على كارت Baseline (T1200 / GTX 1650)
GAMES_DATABASE = [
    {
        "name": "Elden Ring",
        "category": "Souls-like",
        "base_fps_low": 42,
        "base_fps_high": 30,
        "rec_settings": "1080p Medium",
    },
    {
        "name": "Dark Souls III",
        "category": "Souls-like",
        "base_fps_low": 60,
        "base_fps_high": 55,
        "rec_settings": "1080p High",
    },
    {
        "name": "Sekiro: Shadows Die Twice",
        "category": "Souls-like",
        "base_fps_low": 60,
        "base_fps_high": 50,
        "rec_settings": "1080p High",
    },
    {
        "name": "PUBG: BATTLEGROUNDS",
        "category": "Competitive Shooter",
        "base_fps_low": 75,
        "base_fps_high": 50,
        "rec_settings": "1080p Low/Comp",
    },
    {
        "name": "eFootball (PES 2024/2025)",
        "category": "Sports",
        "base_fps_low": 60,
        "base_fps_high": 55,
        "rec_settings": "1080p High",
    },
    {
        "name": "EA Sports FC 24 / 25",
        "category": "Sports",
        "base_fps_low": 60,
        "base_fps_high": 48,
        "rec_settings": "1080p Medium (60 FPS Cap)",
    },
    {
        "name": "God of War (2018)",
        "category": "Action RPG",
        "base_fps_low": 48,
        "base_fps_high": 35,
        "rec_settings": "1080p Original / FSR Quality",
    },
    {
        "name": "Ghost of Tsushima",
        "category": "Open World Action",
        "base_fps_low": 52,
        "base_fps_high": 38,
        "rec_settings": "1080p Medium + FSR 3",
    },
    {
        "name": "Resident Evil 7: Biohazard",
        "category": "Survival Horror",
        "base_fps_low": 85,
        "base_fps_high": 60,
        "rec_settings": "1080p High",
    },
    {
        "name": "Resident Evil Village",
        "category": "Survival Horror",
        "base_fps_low": 65,
        "base_fps_high": 45,
        "rec_settings": "1080p Prioritize Graphics",
    },
    {
        "name": "Silent Hill 2 Remake",
        "category": "Psychological Horror",
        "base_fps_low": 35,
        "base_fps_high": 25,
        "rec_settings": "1080p Low + TSR / FSR Perf",
    },
    {
        "name": "The Last of Us Part I / II",
        "category": "Narrative Survival",
        "base_fps_low": 38,
        "base_fps_high": 28,
        "rec_settings": "1080p Low/Medium + FSR",
    },
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Benchmark & GPU Performance Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        body { background-color: #0b0e14; color: #e1e7ec; font-family: 'Cairo', sans-serif; }
        .hero { background: linear-gradient(135deg, #161b22 0%, #0d1117 100%); border-bottom: 2px solid #00f0ff; padding: 30px 0; margin-bottom: 30px; }
        .card-custom { background: #161b22; border: 1px solid #30363d; border-radius: 12px; transition: transform 0.2s, border-color 0.2s; }
        .card-custom:hover { transform: translateY(-4px); border-color: #00f0ff; }
        .badge-cat { background-color: #21262d; color: #58a6ff; border: 1px solid #30363d; font-size: 0.85rem; }
        .fps-badge { font-size: 1.4rem; font-weight: 700; color: #00f0ff; }
        .btn-check-gpu { background-color: #00f0ff; color: #0b0e14; font-weight: 700; border: none; }
        .btn-check-gpu:hover { background-color: #38bdf8; color: #0b0e14; }
        .select-gpu { background-color: #0d1117; color: #fff; border: 1px solid #30363d; padding: 12px; font-weight: 600; }
        .select-gpu:focus { background-color: #0d1117; color: #fff; border-color: #00f0ff; box-shadow: 0 0 8px rgba(0,240,255,0.4); }
        .status-smooth { color: #3fb950; font-weight: bold; }
        .status-playable { color: #d29922; font-weight: bold; }
        .status-low { color: #f85149; font-weight: bold; }
    </style>
</head>
<body>
    <div class="hero text-center">
        <h1 class="fw-bold mb-2">⚡ Game Benchmark & GPU Performance Hub ⚡</h1>
        <p class="text-secondary mb-0">اختر كارت الشاشة واكتشف أداء الألعاب، الفريمات المتوقعة (FPS)، وأفضل الإعدادات المقترحة</p>
    </div>

    <div class="container mb-5">
        <!-- GPU Selector Form -->
        <div class="row justify-content-center mb-5">
            <div class="col-md-8">
                <div class="card-custom p-4 shadow">
                    <form method="GET" action="/">
                        <label for="gpu" class="form-label fw-bold mb-2">🎮 اختر كارت الشاشة الخاص بجهازك:</label>
                        <div class="input-group">
                            <select name="gpu" id="gpu" class="form-select select-gpu">
                                {% for g in gpu_list %}
                                    <option value="{{ g }}" {% if g == selected_gpu %}selected{% endif %}>{{ g }}</option>
                                {% endfor %}
                            </select>
                            <button type="submit" class="btn btn-check-gpu px-4">اختبار الأداء الآن</button>
                        </div>
                    </form>
                    <div class="mt-3 text-secondary small">
                        كارت الشاشة النشط حالياً: <span class="text-info fw-bold">{{ selected_gpu }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Games Grid -->
        <div class="row g-4">
            {% for game in games %}
            <div class="col-md-6 col-lg-4">
                <div class="card card-custom h-100 p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="fw-bold mb-0 text-white">{{ game.name }}</h5>
                        <span class="badge badge-cat">{{ game.category }}</span>
                    </div>

                    <div class="my-3 p-3 text-center rounded" style="background-color: #0d1117;">
                        <span class="text-secondary d-block small mb-1">معدل الفريمات المتوقع (1080p)</span>
                        <span class="fps-badge">{{ game.estimated_fps }} FPS</span>
                        <div class="mt-1 {{ game.status_class }}">{{ game.status_text }}</div>
                    </div>

                    <div class="mt-auto">
                        <div class="d-flex justify-content-between text-secondary small border-top border-secondary pt-2 mt-2">
                            <span>الإعداد الموصى به:</span>
                            <span class="text-white">{{ game.rec_settings }}</span>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    selected_gpu = request.args.get("gpu", "NVIDIA T1200 Laptop (4GB)")
    multiplier = GPU_TIERS.get(selected_gpu, 1.0)

    calculated_games = []
    for g in GAMES_DATABASE:
        fps = int(g["base_fps_low"] * multiplier)
        if fps >= 60:
            status = "سلس وممتاز (Smooth 60+)"
            s_class = "status-smooth"
        elif fps >= 35:
            status = "قابل للعب بسلاسة (Playable)"
            s_class = "status-playable"
        else:
            status = "قد يواجه تقطيع (Needs Low/FSR)"
            s_class = "status-low"

        calculated_games.append(
            {
                "name": g["name"],
                "category": g["category"],
                "estimated_fps": fps,
                "rec_settings": g["rec_settings"],
                "status_text": status,
                "status_class": s_class,
            }
        )

    # تسجيل الزيارة في قاعدة البيانات كالمعتاد
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS visitor_logs (
                id SERIAL PRIMARY KEY,
                gpu_selected VARCHAR(100),
                visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        cur.execute(
            "INSERT INTO visitor_logs (gpu_selected) VALUES (%s);",
            (selected_gpu,),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Logging Error: {e}")

    return render_template_string(
        HTML_TEMPLATE,
        gpu_list=list(GPU_TIERS.keys()),
        selected_gpu=selected_gpu,
        games=calculated_games,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
