import os, ssl, smtplib, html
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from db import get_conn
from app import INTERESTS

SITE_URL = os.environ.get("GINTERSHIPS_URL", "http://127.0.0.1:5000")
SENDER   = os.environ.get("GINTERSHIPS_EMAIL")
PASSWORD = os.environ.get("GINTERSHIPS_APP_PASSWORD")
MAX_LISTED = 10

def new_offers_for(conn, user_id, keys):
    """Stages qui correspondent aux intérêts ET que l'utilisateur n'a pas encore reçus."""
    kws = []
    for k in keys:
        if k in INTERESTS:
            kws += INTERESTS[k][1]
    sql = ("SELECT * FROM offers WHERE category='stage' "
           "AND id NOT IN (SELECT offer_id FROM sent WHERE user_id = ?)")
    params = [user_id]
    if kws:
        sql += " AND (" + " OR ".join(["LOWER(title) LIKE ?"] * len(kws)) + ")"
        params += [f"%{k}%" for k in kws]
    sql += " ORDER BY id DESC"
    return conn.execute(sql, params).fetchall()

def build_html(name, offers):
    shown = offers[:MAX_LISTED]
    rest = len(offers) - len(shown)
    items = ""
    for o in shown:
        place = f" · {html.escape(o['location'])}" if o["location"] else ""
        items += (
            f'<div style="background:#fff;border:1px solid #F0E3A8;border-radius:12px;'
            f'padding:12px 16px;margin:10px 0;">'
            f'<b>{html.escape(o["title"])}</b><br>'
            f'<span style="color:#8A7B4F;font-size:13px;">{html.escape(o["source"])}{place}</span><br>'
            f'<a href="{html.escape(o["url"])}" style="color:#D9A92B;font-weight:bold;">Voir l\'offre</a>'
            f'</div>'
        )
    more = (f'<p>… et <b>{rest}</b> autre(s) offre(s) t\'attendent sur Ginterships.</p>' if rest > 0 else "")
    return f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;background:#FFFBEA;padding:24px;color:#4A3F1D;">
      <h2 style="margin-top:0;">Ginterships 🌼</h2>
      <p>Bonjour <b>{html.escape(name)}</b>,</p>
      <p>Il y a <b>{len(offers)}</b> nouveau(x) stage(s) que tu n'as pas encore consulté(s) :</p>
      {items}
      {more}
      <p><a href="{SITE_URL}/my-offers" style="background:#F4C84A;color:#4A3F1D;padding:10px 20px;
         border-radius:999px;text-decoration:none;font-weight:bold;display:inline-block;">
         Consulter toutes mes offres</a></p>
      <p style="color:#8A7B4F;font-size:12px;">N'oublie pas de passer sur Ginterships pour ne rien rater !</p>
    </div>"""

def send_email(to, subject, body_html):
    if not (SENDER and PASSWORD):                       # MODE TEST
        os.makedirs("outbox", exist_ok=True)
        fname = f"outbox/{datetime.now():%Y%m%d_%H%M%S}_{to.replace('@', '_at_')}.html"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"<p><b>À :</b> {html.escape(to)}<br><b>Objet :</b> {html.escape(subject)}</p><hr>{body_html}")
        print("[TEST] email enregistré :", fname)
        return True
    msg = MIMEMultipart("alternative")                  # MODE RÉEL (Gmail)
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = SENDER
    msg["To"] = to
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
            s.login(SENDER, PASSWORD)
            s.sendmail(SENDER, to, msg.as_string())
        print("[ENVOYÉ] ->", to)
        return True
    except Exception as e:
        print("[ERREUR] envoi vers", to, ":", e)
        return False

def notify_all():
    conn = get_conn()
    users = conn.execute("SELECT * FROM users").fetchall()
    sent_count = 0
    for u in users:
        keys = [r["keyword"] for r in conn.execute(
            "SELECT keyword FROM interests WHERE user_id = ?", (u["id"],))]
        offers = new_offers_for(conn, u["id"], keys)
        if not offers:
            continue
        subject = f"🌼 Ginterships : {len(offers)} nouveau(x) stage(s) pour toi"
        if send_email(u["email"], subject, build_html(u["name"], offers)):
            conn.executemany("INSERT OR IGNORE INTO sent(user_id, offer_id) VALUES (?,?)",
                             [(u["id"], o["id"]) for o in offers])
            conn.commit()
            sent_count += 1
    conn.close()
    return sent_count

if __name__ == "__main__":
    print("Emails envoyés :", notify_all())
