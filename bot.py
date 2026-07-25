import os, sys, json, re, logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn, httpx

# ─── Telethon ───
from telethon import TelegramClient, events
from telethon.tl.types import Message as TeleMessage

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ─── Config ───
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", 38674666))
API_HASH = os.environ.get("API_HASH", "b4f0fbf8fb560c4bc9e7b9f3698e474c")
API_BASE = os.environ.get("API_BASE", "https://osint.yukiapi.site/api")
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://devstoolsbot.up.railway.app")

# ─── FastAPI ───
app = FastAPI(title="DevsToolsBot")

# ─── Telethon Client ───
bot = TelegramClient("bot_session", API_ID, API_HASH)

# ─── API Helper ───
async def api_get(endpoint: str, params: dict = None) -> dict:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{API_BASE}/{endpoint}", params=params)
            return resp.json() if resp.status_code == 200 else {"status":"error","message":f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"status":"error","message":str(e)}

def fmt_response(data: dict, title: str = "") -> str:
    if not data or data.get("status") == "error":
        return f"❌ {data.get('message','Error')}"
    d = data.get("data", data)
    lines = [f"**{title}**"] if title else []
    def flatten(obj, prefix=""):
        res = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if v is None or v == "" or v == []: continue
                kd = k.replace("_"," ").title()
                if isinstance(v, (dict,list)) and v:
                    res.append(f"\n**{kd}:**")
                    res.extend(flatten(v, prefix))
                else:
                    res.append(f"`{kd}:` {str(v)[:300]}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:10]):
                res.append(f"• {str(item)[:200]}" if not isinstance(item,dict) else "")
        return res
    body = "\n".join(flatten(d))
    text = lines[0] + "\n" + body if lines else body
    return text[:4000] if len(text) > 4000 else text

# ─── BOT COMMANDS ───
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    kb = {
        "inline_keyboard": [
            [{"text": "🔍 OSINT", "callback_data": "cat_osint"},
             {"text": "🛠 Utilities", "callback_data": "cat_utils"}],
            [{"text": "🇮🇳 India", "callback_data": "cat_india"},
             {"text": "🌐 Web", "callback_data": "cat_web"}],
            [{"text": "📡 API Docs", "url": "https://osint.yukiapi.site/docs"},
             {"text": "🐙 GitHub", "url": "https://github.com/SUDEEPBOTS/YUKI-OSINT-API"}]
        ]
    }
    msg = (
        f"👋 **Hey {event.sender.first_name}!**\n\n"
        f"🕵️ **Dev's OSINT Bot** — 40+ Legal Intelligence Tools\n\n"
        f"🔍 `/ip` `/email` `/phone` `/dns` `/whois` `/subdomain` `/detect`\n"
        f"🛠 `/hash` `/base64` `/uuid` `/currency` `/translate` `/weather`\n"
        f"🇮🇳 `/pan` `/gstin` `/voter` `/aadhaar` `/vehicle` `/pincode`\n\n"
        f"📚 `/help` — All commands\n⚙️ `/tools` — Category menu\n\n"
        f"⚡ Powered by @hostillbot"
    )
    await event.reply(msg, parse_mode="md", buttons=kb)

@bot.on(events.NewMessage(pattern="/help"))
async def help(event):
    text = (
        "**📚 All Commands**\n\n"
        "**🔍 OSINT**\n"
        "`/ip [ip]` — IP geolocation\n"
        "`/email <email>` — Full email OSINT\n"
        "`/phone <num>` — Phone carrier\n"
        "`/dns <domain>` — DNS records\n"
        "`/whois <domain>` — WHOIS lookup\n"
        "`/subdomain <domain>` — Subdomain finder\n"
        "`/detect <domain>` — Hosting detect\n"
        "`/breach <email>` — Breach check\n"
        "`/ghuser <user>` — GitHub user info\n"
        "`/wayback <domain>` — Wayback history\n"
        "`/headers <url>` — HTTP headers\n"
        "`/ssl <domain>` — SSL check\n"
        "`/portscan <host>` — Port scanner\n\n"
        "**🛠 Utilities**\n"
        "`/hash <text>` — Hash generator\n"
        "`/base64 e/d <text>` — Base64\n"
        "`/uuid [n]` — UUID generator\n"
        "`/qr <text>` — QR code\n"
        "`/currency <amt> <from> <to>` — Convert\n"
        "`/translate <text> [lang]` — Translate\n"
        "`/weather <city>` — Weather\n"
        "`/pincode <code>` — PIN lookup\n"
        "`/password <pass>` — Password strength\n"
        "`/ifsc <code>` — IFSC details\n\n"
        "**🇮🇳 India**\n"
        "`/pan <pan>` — PAN info\n"
        "`/gstin <gstin>` — GST details\n"
        "`/voter <epic>` — Voter ID\n"
        "`/aadhaar <num>` — Aadhaar verify\n"
        "`/ration <num>` — Ration card\n"
        "`/vehicle <reg>` — Vehicle RC\n"
        "`/school <code>` — School info"
    )
    await event.reply(text, parse_mode="md")

@bot.on(events.NewMessage(pattern="/tools"))
async def tools(event):
    kb = {
        "inline_keyboard": [
            [{"text": "🔍 OSINT", "callback_data": "cat_osint"},
             {"text": "🛠 Utilities", "callback_data": "cat_utils"}],
            [{"text": "🇮🇳 India", "callback_data": "cat_india"},
             {"text": "🌐 Web Tools", "callback_data": "cat_web"}]
        ]
    }
    await event.reply("**📂 Select Category:**", parse_mode="md", buttons=kb)

# ─── OSINT Commands ───
@bot.on(events.NewMessage(pattern=r"/ip ?(.*)"))
async def cmd_ip(event):
    ip = event.pattern_match.group(1).strip() or None
    data = await api_get("ip", {"ip": ip} if ip else {})
    await event.reply(fmt_response(data, "🌐 IP Info"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/email ?(.*)"))
async def cmd_email(event):
    args = event.pattern_match.group(1).strip()
    if not args:
        await event.reply("Usage: `/email user@example.com`")
        return
    parts = args.split()
    email = parts[0]
    deep = "deep" in parts
    data = await api_get("email", {"email": email, "deep": str(deep).lower()})
    await event.reply(fmt_response(data, f"📧 Email — {email}"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/phone ?(.*)"))
async def cmd_phone(event):
    num = event.pattern_match.group(1).strip()
    if not num: return await event.reply("Usage: `/phone 9876543210`")
    data = await api_get("phone", {"phone": num})
    await event.reply(fmt_response(data, "📞 Phone"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/dns ?(.*)"))
async def cmd_dns(event):
    d = event.pattern_match.group(1).strip()
    if not d: return await event.reply("Usage: `/dns google.com`")
    data = await api_get("dns", {"domain": d})
    await event.reply(fmt_response(data, "🌐 DNS"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/whois ?(.*)"))
async def cmd_whois(event):
    d = event.pattern_match.group(1).strip()
    if not d: return await event.reply("Usage: `/whois google.com`")
    data = await api_get("whois", {"domain": d})
    await event.reply(fmt_response(data, "🔍 WHOIS"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/subdomain ?(.*)"))
async def cmd_subdomain(event):
    d = event.pattern_match.group(1).strip()
    if not d: return await event.reply("Usage: `/subdomain google.com`")
    data = await api_get("subdomain", {"domain": d, "limit": 15})
    if data.get("status") == "success":
        dd = data
        text = f"**🔍 Subdomains — {dd['domain']}**\n`Real:` {dd.get('alive_real_services',0)} | `CF Proxy:` {dd.get('cloudflare_proxied_only',0)} | `Dead:` {dd.get('dead',0)}\n\n"
        for s in dd.get("subdomains", [])[:12]:
            lbl = s.get("alive_label","?")
            icon = "🟢" if lbl=="alive" else "🟡" if lbl=="cloudflare_proxy" else "⚫"
            text += f"{icon} `{s['domain']}` — {s.get('http_status','?')} ({s.get('response_time_ms','?')}ms)\n"
        await event.reply(text, parse_mode="md")
    else:
        await event.reply(f"❌ {data.get('message','Error')}")

@bot.on(events.NewMessage(pattern=r"/detect ?(.*)"))
async def cmd_detect(event):
    d = event.pattern_match.group(1).strip()
    if not d: return await event.reply("Usage: `/detect google.com`")
    data = await api_get("detect", {"domain": d})
    if data.get("status") == "success":
        dd = data["data"]
        text = (
            f"**🌐 Hosting — {dd['domain']}**\n"
            f"`IP:` {dd.get('ip','?')}\n`Org:` {dd.get('asn_org','?')}\n"
            f"`Platform:` {dd.get('platform','?')}\n`Status:` HTTP {dd.get('status_code','?')}"
        )
        await event.reply(text, parse_mode="md")
    else:
        await event.reply(f"❌ {data.get('message','Error')}")

@bot.on(events.NewMessage(pattern=r"/hash ?(.*)"))
async def cmd_hash(event):
    text = event.pattern_match.group(1).strip()
    if not text: return await event.reply("Usage: `/hash hello`")
    data = await api_get("hash", {"text": text})
    if data.get("status") == "success":
        msg = f"**#️⃣ Hash — `{text[:30]}`**\n"
        for algo, h in data.get("hashes",{}).items():
            msg += f"`{algo}:` `{h[:35]}...`\n"
        await event.reply(msg, parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/weather ?(.*)"))
async def cmd_weather(event):
    city = event.pattern_match.group(1).strip()
    if not city: return await event.reply("Usage: `/weather Mumbai`")
    data = await api_get("weather", {"city": city})
    if data.get("status") == "success":
        d = data["data"]
        await event.reply(f"**🌡 {data['city']}**\n`Temp:` {d.get('temp_c','?')}°C | `Feels:` {d.get('feels_like','?')}°C\n`Humidity:` {d.get('humidity','?')}%\n`Wind:` {d.get('wind_speed','?')} km/h\n`Sky:` {d.get('description','?')}", parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/pincode ?(.*)"))
async def cmd_pincode(event):
    pin = event.pattern_match.group(1).strip()
    if not pin: return await event.reply("Usage: `/pincode 110001`")
    data = await api_get("pin", {"pincode": pin})
    if data.get("status") == "success":
        offices = data["data"].get("PostOffice",[])
        text = f"**📮 PIN: {pin}** — {len(offices)} offices\n"
        for o in offices[:8]:
            text += f"• {o['Name']} ({o.get('District','?')})\n"
        await event.reply(text, parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/ifsc ?(.*)"))
async def cmd_ifsc(event):
    code = event.pattern_match.group(1).strip().upper()
    if not code: return await event.reply("Usage: `/ifsc SBIN0000001`")
    data = await api_get("ifsc", {"ifsc": code})
    if data.get("status") == "success":
        d = data["data"]
        await event.reply(f"**🏦 IFSC — {code}**\n`Bank:` {d['bank']}\n`Branch:` {d['branch']}\n`City:` {d['city']}\n`State:` {d['state']}", parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/currency ?(.*)"))
async def cmd_currency(event):
    args = event.pattern_match.group(1).strip().split()
    if len(args) < 3: return await event.reply("Usage: `/currency 100 USD INR`")
    try:
        amt = float(args[0])
        data = await api_get("currency", {"amount": amt, "from_c": args[1].upper(), "to_c": args[2].upper()})
        if data.get("status") == "success":
            d = data
            await event.reply(f"**💱 {d['amount']} {d['from']['code']} = {d['result']} {d['to']['code']}**\n`Rate:` 1 {d['from']['code']} = {d['rate']} {d['to']['code']}", parse_mode="md")
    except: await event.reply("Invalid amount")

@bot.on(events.NewMessage(pattern=r"/password ?(.*)"))
async def cmd_password(event):
    pw = event.pattern_match.group(1).strip()
    if not pw: return await event.reply("Usage: `/password MyP@ss123`")
    data = await api_get("password-strength", {"password": pw})
    if data.get("status") == "success":
        d = data
        await event.reply(f"**🔑 Password**\n`Strength:` {d['strength']}\n`Score:` {d['score']}/100 {d.get('level','')}\n`Entropy:` {d.get('entropy_bits','?')} bits", parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/uuid ?(.*)"))
async def cmd_uuid(event):
    c = 1
    try: c = min(int(event.pattern_match.group(1).strip()), 10)
    except: pass
    data = await api_get("uuid", {"count": c})
    if data.get("status") == "success":
        text = f"**🆔 UUID{'s' if c>1 else ''}**\n"
        for u in data["uuids"]: text += f"`{u['uuid4']}`\n"
        await event.reply(text, parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/pan ?(.*)"))
async def cmd_pan(event):
    p = event.pattern_match.group(1).strip().upper()
    if not p: return await event.reply("Usage: `/pan ABCPK1234F`")
    data = await api_get("pan", {"pan": p})
    await event.reply(fmt_response(data, "🆔 PAN"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/gstin ?(.*)"))
async def cmd_gstin(event):
    g = event.pattern_match.group(1).strip().upper()
    if not g: return await event.reply("Usage: `/gstin 27AABCU1234D1Z5`")
    data = await api_get("gstin", {"gstin": g})
    await event.reply(fmt_response(data, "🏦 GSTIN"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/voter ?(.*)"))
async def cmd_voter(event):
    v = event.pattern_match.group(1).strip().upper()
    if not v: return await event.reply("Usage: `/voter UKL1234567`")
    data = await api_get("voter", {"epic": v})
    await event.reply(fmt_response(data, "🗳 Voter"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/aadhaar ?(.*)"))
async def cmd_aadhaar(event):
    a = event.pattern_match.group(1).strip()
    if not a: return await event.reply("Usage: `/aadhaar 123456789012`")
    data = await api_get("aadhaar-verify", {"aadhaar": a})
    await event.reply(fmt_response(data, "🆔 Aadhaar"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/vehicle ?(.*)"))
async def cmd_vehicle(event):
    r = event.pattern_match.group(1).strip().upper()
    if not r: return await event.reply("Usage: `/vehicle UP32EA1234`")
    data = await api_get("vehicle-rc", {"registration": r})
    await event.reply(fmt_response(data, "🚗 Vehicle"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/school ?(.*)"))
async def cmd_school(event):
    c = event.pattern_match.group(1).strip()
    if not c: return await event.reply("Usage: `/school 123456`")
    data = await api_get("school", {"school_code": c})
    await event.reply(fmt_response(data, "📖 School"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/ration ?(.*)"))
async def cmd_ration(event):
    a = event.pattern_match.group(1).strip()
    if not a: return await event.reply("Usage: `/ration <number>`")
    data = await api_get("ration", {"ration_number": a})
    await event.reply(fmt_response(data, "🍲 Ration"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/breach ?(.*)"))
async def cmd_breach(event):
    e = event.pattern_match.group(1).strip()
    if not e: return await event.reply("Usage: `/breach email@example.com`")
    data = await api_get("breach", {"email": e})
    await event.reply(fmt_response(data, "🆘 Breach"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/ghuser ?(.*)"))
async def cmd_ghuser(event):
    u = event.pattern_match.group(1).strip()
    if not u: return await event.reply("Usage: `/ghuser sudeepbots`")
    data = await api_get("gh-user", {"username": u})
    await event.reply(fmt_response(data, "🐙 GitHub"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/wayback ?(.*)"))
async def cmd_wayback(event):
    d = event.pattern_match.group(1).strip()
    if not d: return await event.reply("Usage: `/wayback google.com`")
    data = await api_get("wayback", {"domain": d, "limit": 5})
    await event.reply(fmt_response(data, "⏳ Wayback"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/headers ?(.*)"))
async def cmd_headers(event):
    u = event.pattern_match.group(1).strip()
    if not u: return await event.reply("Usage: `/headers https://example.com`")
    data = await api_get("http-headers", {"url": u})
    await event.reply(fmt_response(data, "📋 Headers"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/ssl ?(.*)"))
async def cmd_ssl(event):
    d = event.pattern_match.group(1).strip()
    if not d: return await event.reply("Usage: `/ssl google.com`")
    data = await api_get("ssl-check", {"domain": d})
    await event.reply(fmt_response(data, "🔒 SSL"), parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/portscan ?(.*)"))
async def cmd_portscan(event):
    h = event.pattern_match.group(1).strip()
    if not h: return await event.reply("Usage: `/portscan google.com`")
    data = await api_get("port-check", {"host": h})
    if data.get("status") == "success":
        d = data
        text = f"**🔌 Port Scan — {d['host']}**\n`Open:` {d['open_count']}/{d['scanned']}\n"
        for p in d.get("open_ports",[]):
            text += f"🟢 `{p['port']}` — {p['service']}\n"
        await event.reply(text, parse_mode="md")
    else:
        await event.reply(f"❌ {data.get('message','Error')}")

@bot.on(events.NewMessage(pattern=r"/base64 ?(.*)"))
async def cmd_base64(event):
    args = event.pattern_match.group(1).strip().split(maxsplit=1)
    if len(args) < 2: return await event.reply("Usage: `/base64 encode hello` or `/base64 decode aGVsbG8=`")
    mode, text = args[0], args[1]
    import base64
    try:
        if mode == "encode":
            out = base64.b64encode(text.encode()).decode()
            await event.reply(f"**🔐 Encoded:** `{out[:400]}`", parse_mode="md")
        elif mode == "decode":
            out = base64.b64decode(text).decode()
            await event.reply(f"**🔓 Decoded:** `{out[:400]}`", parse_mode="md")
    except: await event.reply("❌ Invalid base64")

@bot.on(events.NewMessage(pattern=r"/translate ?(.*)"))
async def cmd_translate(event):
    args = event.pattern_match.group(1).strip()
    if not args: return await event.reply("Usage: `/translate Hello world` or `/translate Hello world fr`")
    parts = args.split()
    to_lang = "en"
    text_parts = parts
    if len(parts) > 1 and len(parts[-1]) == 2:
        to_lang = parts[-1]
        text_parts = parts[:-1]
    text = " ".join(text_parts)
    data = await api_get("translate", {"text": text, "to": to_lang})
    if data.get("status") == "success":
        await event.reply(f"**🌍 Translation**\n`{data.get('original','')[:200]}` → `{data.get('translated','')[:200]}`", parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/qr ?(.*)"))
async def cmd_qr(event):
    text = event.pattern_match.group(1).strip()
    if not text: return await event.reply("Usage: `/qr https://example.com`")
    data = await api_get("qr", {"text": text})
    if data.get("status") == "success":
        await event.reply(f"📱 **QR:** [Click here]({data['qr_url']})", parse_mode="md")

# ─── CALLBACK HANDLER ───
menus = {
    "osint": "**🔍 OSINT Tools**\n`/ip` `/email` `/phone` `/dns` `/whois` `/subdomain` `/detect` `/breach` `/ghuser` `/wayback` `/headers` `/ssl` `/portscan`",
    "utils": "**🛠 Utilities**\n`/hash` `/base64` `/uuid` `/qr` `/currency` `/translate` `/weather` `/pincode` `/password` `/ifsc`",
    "india": "**🇮🇳 India**\n`/pan` `/gstin` `/voter` `/aadhaar` `/ration` `/vehicle` `/school`",
    "web": "**🌐 Web Tools**\n`/qr` `/currency` `/translate` `/headers` `/ssl` `/portscan` `/wayback` `/detect`"
}

@bot.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode()
    cat = data.replace("cat_","")
    if cat == "back":
        kb = {"inline_keyboard": [
            [{"text":"🔍 OSINT","callback_data":"cat_osint"},{"text":"🛠 Utilities","callback_data":"cat_utils"}],
            [{"text":"🇮🇳 India","callback_data":"cat_india"},{"text":"🌐 Web","callback_data":"cat_web"}]
        ]}
        await event.edit("**📂 Select Category:**", buttons=kb)
    else:
        back_kb = {"inline_keyboard": [[{"text":"◀️ Back","callback_data":"cat_back"}]]}
        text = menus.get(cat, "Unknown")
        await event.edit(text, buttons=back_kb)

# ─── WEBHOOK ENDPOINT ───
@app.post(f"/{BOT_TOKEN}")
async def webhook(request: Request):
    update_data = await request.json()
    await bot.process_update(update_data)
    return {"ok": True}

@app.get("/")
@app.get("/health")
async def health():
    return {"status": "ok", "bot": "DevsToolsBot", "framework": "Telethon+FastAPI"}

# ─── STARTUP ───
@app.on_event("startup")
async def startup():
    logger.info("Starting bot...")
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    logger.info(f"Bot running: @{me.username}")
    
    # Set webhook via Bot API directly
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", params={"url": webhook_url})
        logger.info(f"Webhook set: {resp.json()}")

@app.on_event("shutdown")
async def shutdown():
    await bot.disconnect()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
