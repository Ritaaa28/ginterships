from db import get_conn, init_db

DEMO = [
    ("Stage développeur web", "Demo Corp", "Fès", "https://example.com/demo-1"),
    ("Stage Data Analyst", "Demo Data", "Casablanca", "https://example.com/demo-2"),
    ("Stage cybersécurité", "Demo Secure", "Rabat", "https://example.com/demo-3"),
    ("Stage marketing digital", "Demo Studio", "Tanger", "https://example.com/demo-4"),
]

init_db()
conn = get_conn()
for title, company, location, url in DEMO:
    conn.execute(
        "INSERT OR IGNORE INTO offers(title, company, location, url, source, category) VALUES (?,?,?,?,?,'stage')",
        (title, company, location, url, "demo"),
    )
conn.commit()
conn.close()
print("Base de démonstration prête.")
