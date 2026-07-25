import os, sys, json, re, logging, asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn, httpx

# PTB
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_BASE = os.environ.get("API_BASE", "https://osint.yukiapi.site/api")
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", f"https://devstoolsbot-production.up.railway.app")

# FastAPI
app = FastAPI(title="DevsToolsBot")

# PTB Application
ptb_app = Application.builder().token(BOT_TOKEN).concurrent_updates(True).build()

# ─── API ───
async def api_get(endpoint: str, params: dict = None) -> dict:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{API_BASE}/{endpoint}", params=params)
            return resp.json() if resp.status_code == 200 else {"status":"error","message":f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"status":"error","message":str(e)}

def fmt_json(data: dict, title: str = "") -> str:
    if not data or data.get("status") == "error":
        return f"❌ {data.get('message','Error')}"
    d = data.get("data", data)
    lines = [f"**{title}**"] if title else []
    def flatten(obj):
        res = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if v is None or v == "" or v == []: continue
                kd = k.replace("_"," ").title()
                if isinstance(v, (dict,list)) and v:
                    res.append(f"\n**{kd}:**")
                    res.extend(flatten(v))
                else:
                    res.append(f"`{kd}:` {str(v)[:300]}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:10]):
                res.append(f"• {str(item)[:200]}")
        return res
    body = "\n".join(flatten(d))
    text = lines[0] + "\n" + body if lines else body
    return text[:4000]

# ─── COMMANDS ───
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 OSINT", callback_data="cat_osint"),
         InlineKeyboardButton("🛠 Utilities", callback_data="cat_utils")],
        [InlineKeyboardButton("🇮🇳 India", callback_data="cat_india"),
         InlineKeyboardButton("🌐 Web", callback_data="cat_web")],
        [InlineKeyboardButton("📡 API Docs", url="https://osint.yukiapi.site/docs"),
         InlineKeyboardButton("🐙 GitHub", url="https://github.com/SUDEEPBOTS/YUKI-OSINT-API")]
    ])
    msg = (f"👋 **Hey {user.first_name}!**\n\n🕵️ **Dev's OSINT Bot** — 40+ Legal Intelligence Tools\n\n"
           f"🔍 `/ip` `/email` `/phone` `/dns` `/whois` `/subdomain` `/detect`\n"
           f"🛠 `/hash` `/base64` `/uuid` `/currency` `/translate` `/weather`\n"
           f"🇮🇳 `/pan` `/gstin` `/voter` `/aadhaar` `/vehicle` `/pincode`\n\n"
           f"📚 `/help` — All commands\n⚙️ `/tools` — Category menu\n\n⚡ Powered by @hostillbot")
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**📚 All Commands**\n\n**🔍 OSINT**\n`/ip [ip]` `/email <e>` `/phone <n>` `/dns <d>` `/whois <d>` `/subdomain <d>` `/detect <d>`\n`/breach <e>` `/ghuser <u>` `/wayback <d>` `/headers <u>` `/ssl <d>` `/portscan <h>`\n\n"
        "**🛠 Utilities**\n`/hash <t>` `/base64 e/d <t>` `/uuid [n]` `/qr <t>` `/currency <a> <f> <t>` `/translate <t> [l]`\n`/weather <c>` `/pincode <c>` `/password <p>` `/ifsc <c>`\n\n"
        "**🇮🇳 India**\n`/pan <p>` `/gstin <g>` `/voter <v>` `/aadhaar <n>` `/ration <n>` `/vehicle <r>` `/school <c>`",
        parse_mode="Markdown")

async def tools(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 OSINT", callback_data="cat_osint"),
         InlineKeyboardButton("🛠 Utilities", callback_data="cat_utils")],
        [InlineKeyboardButton("🇮🇳 India", callback_data="cat_india"),
         InlineKeyboardButton("🌐 Web Tools", callback_data="cat_web")]
    ])
    await update.message.reply_text("**📂 Select Category:**", parse_mode="Markdown", reply_markup=kb)

# Generic command handler
async def cmd_generic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.split()[0][1:].split("@")[0]
    args = update.message.text.split()[1:] if len(update.message.text.split()) > 1 else []
    text = " ".join(args) if args else None
    
    endpoints = {
        "ip": ("ip", {"ip": text} if text else {}),
        "phone": ("phone", {"phone": text}),
        "dns": ("dns", {"domain": text}),
        "whois": ("whois", {"domain": text}),
        "detect": ("detect", {"domain": text}),
        "breach": ("breach", {"email": text}),
        "ghuser": ("gh-user", {"username": text}),
        "wayback": ("wayback", {"domain": text, "limit": 5}),
        "headers": ("http-headers", {"url": text}),
        "ssl": ("ssl-check", {"domain": text}),
        "pan": ("pan", {"pan": (text or "").upper()}),
        "gstin": ("gstin", {"gstin": (text or "").upper()}),
        "voter": ("voter", {"epic": (text or "").upper()}),
        "aadhaar": ("aadhaar-verify", {"aadhaar": text}),
        "ration": ("ration", {"ration_number": text}),
        "vehicle": ("vehicle-rc", {"registration": (text or "").upper()}),
        "school": ("school", {"school_code": text}),
        "weather": ("weather", {"city": text}),
        "pincode": ("pin", {"pincode": text}),
        "ifsc": ("ifsc", {"ifsc": (text or "").upper()}),
        "uuid": ("uuid", {"count": int(text) if text and text.isdigit() else 1}),
    }
    
    if cmd in endpoints:
        ep, params = endpoints[cmd]
        if cmd == "uuid": params = {"count": max(1, min(10, int(text))) if text and text.isdigit() else 1}
        if cmd == "ip" and not text: params = {}
        if not text and cmd not in ("ip", "uuid"):
            return await update.message.reply_text(f"Usage: /{cmd} <params>")
        data = await api_get(ep, params)
        titles = {"ip":"🌐 IP","phone":"📞 Phone","dns":"🌐 DNS","whois":"🔍 WHOIS","detect":"🌐 Hosting",
                  "breach":"🆘 Breach","ghuser":"🐙 GitHub","wayback":"⏳ Wayback","headers":"📋 Headers",
                  "ssl":"🔒 SSL","pan":"🆔 PAN","gstin":"🏦 GSTIN","voter":"🗳 Voter","aadhaar":"🆔 Aadhaar",
                  "ration":"🍲 Ration","vehicle":"🚗 Vehicle","school":"📖 School","weather":"🌡 Weather",
                  "pincode":"📮 PIN","ifsc":"🏦 IFSC","uuid":"🆔 UUID"}
        await update.message.reply_text(fmt_json(data, titles.get(cmd,"")), parse_mode="Markdown")
    
    elif cmd == "hash":
        if not text: return await update.message.reply_text("Usage: `/hash hello`", parse_mode="Markdown")
        data = await api_get("hash", {"text": text})
        if data.get("status") == "success":
            msg = f"**#️⃣ Hash — `{text[:30]}`**\n"
            for a, h in data.get("hashes",{}).items(): msg += f"`{a}:` `{h[:35]}...`\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
    
    elif cmd == "subdomain":
        if not text: return await update.message.reply_text("Usage: `/subdomain google.com`")
        data = await api_get("subdomain", {"domain": text, "limit": 15})
        if data.get("status") == "success":
            d = data
            msg = f"**🔍 Subdomains — {d['domain']}**\n`Real:` {d.get('alive_real_services',0)} | `CF Proxy:` {d.get('cloudflare_proxied_only',0)}\n\n"
            for s in d.get("subdomains", [])[:12]:
                icon = "🟢" if s.get("alive_label")=="alive" else "🟡" if s.get("alive_label")=="cloudflare_proxy" else "⚫"
                msg += f"{icon} `{s['domain']}` — {s.get('http_status','?')} ({s.get('response_time_ms','?')}ms)\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
    
    elif cmd == "portscan":
        if not text: return await update.message.reply_text("Usage: `/portscan google.com`")
        data = await api_get("port-check", {"host": text})
        if data.get("status") == "success":
            d = data
            msg = f"**🔌 Port Scan — {d['host']}**\n`Open:` {d['open_count']}/{d['scanned']}\n"
            for p in d.get("open_ports",[]): msg += f"🟢 `{p['port']}` — {p['service']}\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
    
    elif cmd == "password":
        if not text: return await update.message.reply_text("Usage: `/password MyP@ss123`")
        data = await api_get("password-strength", {"password": text})
        if data.get("status") == "success":
            d = data
            await update.message.reply_text(
                f"**🔑 Password**\n`Strength:` {d['strength']}\n`Score:` {d['score']}/100\n`Entropy:` {d.get('entropy_bits','?')} bits",
                parse_mode="Markdown")
    
    elif cmd == "currency":
        parts = text.split() if text else []
        if len(parts) < 3: return await update.message.reply_text("Usage: `/currency 100 USD INR`")
        try:
            data = await api_get("currency", {"amount": float(parts[0]), "from_c": parts[1].upper(), "to_c": parts[2].upper()})
            if data.get("status") == "success":
                d = data
                await update.message.reply_text(f"**💱 {d['amount']} {d['from']['code']} = {d['result']} {d['to']['code']}**\n`Rate:` 1 {d['from']['code']} = {d['rate']} {d['to']['code']}", parse_mode="Markdown")
        except: await update.message.reply_text("Invalid amount")
    
    elif cmd == "email":
        parts = text.split() if text else []
        if not parts: return await update.message.reply_text("Usage: `/email user@example.com`")
        email = parts[0]
        deep = "deep" in parts
        data = await api_get("email", {"email": email, "deep": str(deep).lower()})
        await update.message.reply_text(fmt_json(data, f"📧 Email — {email}"), parse_mode="Markdown")
    
    elif cmd == "translate":
        if not text: return await update.message.reply_text("Usage: `/translate Hello world` or `/translate Hello world fr`")
        parts = text.split()
        to_lang = "en"
        txt_parts = parts
        if len(parts) > 1 and len(parts[-1]) == 2:
            to_lang = parts[-1]; txt_parts = parts[:-1]
        txt = " ".join(txt_parts)
        data = await api_get("translate", {"text": txt, "to": to_lang})
        if data.get("status") == "success":
            await update.message.reply_text(f"**🌍 Translation**\n`{data.get('original','')[:200]}` → `{data.get('translated','')[:200]}`", parse_mode="Markdown")
    
    elif cmd == "base64":
        parts = text.split(maxsplit=1) if text else []
        if len(parts) < 2: return await update.message.reply_text("Usage: `/base64 encode hello` or `/base64 decode aGVsbG8=`")
        import base64
        try:
            if parts[0] == "encode":
                out = base64.b64encode(parts[1].encode()).decode()
                await update.message.reply_text(f"**🔐 Encoded:** `{out[:400]}`", parse_mode="Markdown")
            elif parts[0] == "decode":
                out = base64.b64decode(parts[1]).decode()
                await update.message.reply_text(f"**🔓 Decoded:** `{out[:400]}`", parse_mode="Markdown")
        except: await update.message.reply_text("❌ Invalid base64")
    
    elif cmd == "qr":
        if not text: return await update.message.reply_text("Usage: `/qr https://example.com`")
        data = await api_get("qr", {"text": text})
        if data.get("status") == "success":
            await update.message.reply_text(f"📱 **QR:** {data['qr_url']}", parse_mode="Markdown")

# ─── CALLBACK ───
CAT_MENUS = {
    "osint": "**🔍 OSINT Tools**\n`/ip` `/email` `/phone` `/dns` `/whois` `/subdomain` `/detect`\n`/breach` `/ghuser` `/wayback` `/headers` `/ssl` `/portscan`",
    "utils": "**🛠 Utilities**\n`/hash` `/base64` `/uuid` `/qr` `/currency` `/translate`\n`/weather` `/pincode` `/password` `/ifsc`",
    "india": "**🇮🇳 India**\n`/pan` `/gstin` `/voter` `/aadhaar` `/ration` `/vehicle` `/school`",
    "web": "**🌐 Web Tools**\n`/qr` `/currency` `/translate` `/headers` `/ssl` `/portscan` `/wayback` `/detect`"
}

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("cat_", "")
    if cat == "back":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 OSINT", callback_data="cat_osint"), InlineKeyboardButton("🛠 Utilities", callback_data="cat_utils")],
            [InlineKeyboardButton("🇮🇳 India", callback_data="cat_india"), InlineKeyboardButton("🌐 Web", callback_data="cat_web")]
        ])
        await query.edit_message_text("**📂 Select Category:**", parse_mode="Markdown", reply_markup=kb)
    else:
        back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="cat_back")]])
        await query.edit_message_text(CAT_MENUS.get(cat, "Unknown"), parse_mode="Markdown", reply_markup=back_kb)

# ─── REGISTER HANDLERS ───
CMDS = ["start","help","tools","ip","email","phone","dns","whois","subdomain","detect","breach",
        "ghuser","wayback","headers","ssl","portscan","hash","base64","uuid","qr","currency",
        "translate","weather","pincode","password","ifsc","pan","gstin","voter","aadhaar",
        "ration","vehicle","school"]
for c in CMDS:
    ptb_app.add_handler(CommandHandler(c, start if c=="start" else help_cmd if c=="help" else tools if c=="tools" else cmd_generic))
ptb_app.add_handler(CallbackQueryHandler(button_callback))

# ─── FASTAPI WEBHOOK ───
@app.post(f"/{BOT_TOKEN}")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, ptb_app.bot)
        # Process in background to avoid blocking
        asyncio.ensure_future(ptb_app.process_update(update))
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse({"ok": False}, status_code=200)

@app.get("/")
@app.get("/health")
async def health():
    return {"status":"ok","bot":"DevsToolsBot","version":"2.0.0-Telethon"}

# ─── STARTUP ───
@app.on_event("startup")
async def startup():
    logger.info("Starting bot...")
    await ptb_app.initialize()
    await ptb_app.start()
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    await ptb_app.bot.set_webhook(url=webhook_url)
    wh = await ptb_app.bot.get_webhook_info()
    logger.info(f"Webhook set: {wh.url} | Pending: {wh.pending_update_count}")

@app.on_event("shutdown")
async def shutdown():
    await ptb_app.stop()
    await ptb_app.shutdown()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
