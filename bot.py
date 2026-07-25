import os, sys, json, logging, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import httpx

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_BASE = os.environ.get("API_BASE", "https://osint.yukiapi.site/api")
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ─── START ───
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = (
        f"👋 **Hey {user.first_name}!**\n\n"
        f"🕵️ **Dev's OSINT Bot** — 40+ Legal Intelligence Tools\n\n"
        f"🔍 **OSINT:** `/ip` `/email` `/phone` `/dns` `/whois` `/subdomain` `/detect` `/breach` `/ghuser` `/wayback` `/headers`\n\n"
        f"🛠 **Utilities:** `/hash` `/base64` `/uuid` `/qr` `/currency` `/translate` `/weather` `/pincode` `/password` `/portscan` `/ifsc` `/ssl`\n\n"
        f"🇮🇳 **India:** `/pan` `/gstin` `/voter` `/aadhaar` `/ration` `/samagra` `/school` `/vehicle` `/challan`\n\n"
        f"📚 **Help:** `/help` — all commands\n"
        f"⚙️ **Tools:** `/tools` — category-wise\n\n"
        f"⚡ Powered by @hostillbot"
    )
    kb = [
        [InlineKeyboardButton("📡 API Docs", url="https://osint.yukiapi.site/docs"),
         InlineKeyboardButton("🐙 GitHub", url="https://github.com/SUDEEPBOTS/YUKI-OSINT-API")],
        [InlineKeyboardButton("📢 Channel", url="https://t.me/sudeep_1435"),
         InlineKeyboardButton("👨‍💻 Owner", url="https://t.me/hostillbot")]
    ]
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

# ─── HELP ───
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "**📚 All Commands**\n\n"
        "**🔍 OSINT**\n"
        "`/ip [ip]` — IP geolocation & ISP\n"
        "`/email <email> [deep]` — Full email OSINT\n"
        "`/phone <number>` — Phone carrier info\n"
        "`/dns <domain>` — DNS records (A, MX, NS)\n"
        "`/whois <domain>` — Domain WHOIS info\n"
        "`/subdomain <domain>` — Subdomain finder\n"
        "`/detect <domain>` — Website hosting detect\n"
        "`/breach <email>` — Breach check (HIBP)\n"
        "`/ghuser <username>` — GitHub user info\n"
        "`/wayback <domain>` — Wayback Machine history\n"
        "`/headers <url>` — HTTP headers check\n"
        "`/ssl <domain>` — SSL cert check\n"
        "`/portscan <host>` — Port scanner\n\n"
        "**🛠 Utilities**\n"
        "`/hash <text>` — Generate hashes\n"
        "`/base64 encode|decode <text>` — Base64\n"
        "`/uuid [count]` — UUID generator\n"
        "`/qr <text>` — QR code generator\n"
        "`/currency <amount> <from> <to>` — Currency convert\n"
        "`/translate <text> [to]` — Translation\n"
        "`/weather <city>` — Weather\n"
        "`/pincode <code>` — PIN code info\n"
        "`/password <pass>` — Password strength\n"
        "`/ifsc <code>` — IFSC bank lookup\n\n"
        "**🇮🇳 India**\n"
        "`/pan <pan>` — PAN card info\n"
        "`/gstin <gstin>` — GST registration\n"
        "`/voter <epic>` — Voter ID\n"
        "`/aadhaar <number>` — Aadhaar verify (format)\n"
        "`/ration <number> [state]` — Ration card\n"
        "`/samagra <mobile>` — MP Samagra\n"
        "`/school <code>` — UDISE+ school\n"
        "`/vehicle <reg>` — Vehicle RC\n"
        "`/challan <reg>` — e-Challan info\n\n"
        "**ℹ️** Use `/tools` for category-wise menu"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ─── TOOLS ───
async def tools(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🔍 OSINT", callback_data="cat_osint"),
         InlineKeyboardButton("🛠 Utilities", callback_data="cat_utils")],
        [InlineKeyboardButton("🇮🇳 India", callback_data="cat_india"),
         InlineKeyboardButton("🌐 Web Tools", callback_data="cat_web")],
        [InlineKeyboardButton("⚡ Quick Links", callback_data="cat_links")]
    ]
    await update.message.reply_text("**📂 Select Category:**", parse_mode="Markdown", 
        reply_markup=InlineKeyboardMarkup(kb))

# ─── API CALL ───
async def api_get(endpoint: str, params: dict = None) -> dict:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{API_BASE}/{endpoint}", params=params)
            if resp.status_code == 200:
                return resp.json()
            return {"status": "error", "message": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def fmt_json(data: dict, title: str = "") -> str:
    """Format API response for Telegram"""
    if not data or data.get("status") == "error":
        return f"❌ **Error:** {data.get('message', 'Unknown error')}"
    
    if "data" in data:
        d = data["data"]
    else:
        d = data
    
    parts = [f"**{title}**" if title else ""]
    
    def flatten(obj, prefix=""):
        lines = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    if v:
                        lines.append(f"\n**{k}:**")
                        lines.extend(flatten(v, prefix))
                elif v is not None and v != "" and v != []:
                    k_display = k.replace("_", " ").title()
                    lines.append(f"`{k_display}:` {str(v)[:500]}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:10]):
                if isinstance(item, dict):
                    lines.extend(flatten(item, f"{prefix}{i+1}."))
                else:
                    lines.append(f"• {str(item)[:200]}")
        return lines
    
    lines = flatten(d)
    text = "\n".join(lines)
    
    if len(text) > 4000:
        text = text[:3997] + "..."
    
    return parts[0] + "\n" + text if parts[0] else text

# ─── OSINT COMMANDS ───
async def cmd_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip = " ".join(context.args) if context.args else None
    data = await api_get("ip", {"ip": ip} if ip else {})
    await update.message.reply_text(fmt_json(data, "🌐 IP Info"), parse_mode="Markdown")

async def cmd_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/email user@example.com` or `/email user@example.com deep`", parse_mode="Markdown")
        return
    email = context.args[0]
    deep = "deep" in context.args
    data = await api_get("email", {"email": email, "deep": str(deep).lower()})
    await update.message.reply_text(fmt_json(data, f"📧 Email OSINT — {email}"), parse_mode="Markdown")

async def cmd_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/phone 9876543210`", parse_mode="Markdown")
        return
    data = await api_get("phone", {"phone": context.args[0]})
    await update.message.reply_text(fmt_json(data, "📞 Phone Info"), parse_mode="Markdown")

async def cmd_dns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/dns google.com`", parse_mode="Markdown")
        return
    data = await api_get("dns", {"domain": context.args[0]})
    await update.message.reply_text(fmt_json(data, "🌐 DNS Lookup"), parse_mode="Markdown")

async def cmd_whois(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/whois google.com`", parse_mode="Markdown")
        return
    data = await api_get("whois", {"domain": context.args[0]})
    await update.message.reply_text(fmt_json(data, "🔍 WHOIS Info"), parse_mode="Markdown")

async def cmd_subdomain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/subdomain google.com`", parse_mode="Markdown")
        return
    data = await api_get("subdomain", {"domain": context.args[0], "limit": 20})
    if data.get("status") == "success":
        d = data
        text = (
            f"**🔍 Subdomains — {d['domain']}**\n"
            f"`Checked:` {d['checked']} | `Found:` {d['found']}\n"
            f"`Real:` {d.get('alive_real_services',0)} | `CF Proxy:` {d.get('cloudflare_proxied_only',0)}\n\n"
        )
        for s in d.get("subdomains", [])[:15]:
            lbl = s.get("alive_label", "?")
            icon = "🟢" if lbl == "alive" else "🟡" if lbl == "cloudflare_proxy" else "⚫"
            text += f"{icon} `{s['domain']}` — {s.get('http_status','?')} ({s.get('response_time_ms','?')}ms)\n"
        if len(d.get("subdomains", [])) > 15:
            text += f"\n...and {len(d['subdomains'])-15} more"
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

async def cmd_detect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/detect google.com`", parse_mode="Markdown")
        return
    data = await api_get("detect", {"domain": context.args[0]})
    if data.get("status") == "success":
        d = data["data"]
        platforms = ", ".join([x["platform"] for x in d.get("detected", [])]) or "Unknown"
        text = (
            f"**🌐 Website Detect — {d['domain']}**\n"
            f"`IP:` {d.get('ip','?')}\n"
            f"`Org:` {d.get('asn_org','?')}\n"
            f"`Platform:` {d.get('platform','?')}\n"
            f"`Signals:` {platforms}\n"
            f"`Status:` HTTP {d.get('status_code','?')}"
        )
        if d.get("cname"):
            text += f"\n`CNAME:` {', '.join(d['cname'][:2])}"
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

# ─── UTILITY COMMANDS ───
async def cmd_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/hash hello`", parse_mode="Markdown")
        return
    text = " ".join(context.args)
    data = await api_get("hash", {"text": text})
    if data.get("status") == "success":
        d = data
        msg = f"**#️⃣ Hash — `{d['text'][:50]}`**\n"
        for algo, h in d.get("hashes", {}).items():
            msg += f"`{algo}:` `{h[:40]}`...\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/weather Mumbai`", parse_mode="Markdown")
        return
    data = await api_get("weather", {"city": " ".join(context.args)})
    if data.get("status") == "success":
        d = data["data"]
        text = (
            f"**🌡 Weather — {data['city']}**\n"
            f"`Temp:` {d.get('temp_c','?')}°C | Feels: {d.get('feels_like','?')}°C\n"
            f"`Humidity:` {d.get('humidity','?')}%\n"
            f"`Wind:` {d.get('wind_speed','?')} km/h\n"
            f"`Sky:` {d.get('description','?')}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

async def cmd_pincode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/pincode 110001`", parse_mode="Markdown")
        return
    data = await api_get("pin", {"pincode": context.args[0]})
    if data.get("status") == "success":
        offices = data["data"].get("PostOffice", [])
        text = f"**📮 PIN: {context.args[0]}** — {len(offices)} offices\n\n"
        for o in offices[:10]:
            text += f"• {o['Name']} ({o.get('District','?')}, {o.get('State','?')})\n"
        if len(offices) > 10:
            text += f"\n...and {len(offices)-10} more"
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

async def cmd_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: `/currency 100 USD INR`", parse_mode="Markdown")
        return
    try:
        amount = float(args[0])
        data = await api_get("currency", {"amount": amount, "from_c": args[1].upper(), "to_c": args[2].upper()})
        if data.get("status") == "success":
            d = data
            text = (
                f"**💱 Currency Convert**\n"
                f"`{d['amount']} {d['from']['code']}` = `{d['result']} {d['to']['code']}`\n"
                f"`Rate:` 1 {d['from']['code']} = {d['rate']} {d['to']['code']}"
            )
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ {data.get('message','Error')}")
    except ValueError:
        await update.message.reply_text("Invalid amount")

async def cmd_ifsc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/ifsc SBIN0000001`", parse_mode="Markdown")
        return
    data = await api_get("ifsc", {"ifsc": context.args[0].upper()})
    if data.get("status") == "success":
        d = data["data"]
        text = f"**🏦 IFSC — {context.args[0].upper()}**\n`Bank:` {d['bank']}\n`Branch:` {d['branch']}\n`City:` {d['city']}\n`State:` {d['state']}"
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

async def cmd_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/password MyP@ss123`", parse_mode="Markdown")
        return
    pw = " ".join(context.args)
    data = await api_get("password-strength", {"password": pw})
    if data.get("status") == "success":
        d = data
        text = (
            f"**🔑 Password Strength**\n"
            f"`Strength:` {d['strength']}\n"
            f"`Score:` {d['score']}/100 {d.get('level','')}\n"
            f"`Length:` {d['length']}\n"
            f"`Entropy:` {d.get('entropy_bits','?')} bits\n"
            f"`Feedback:` {', '.join(d.get('feedback',[]))[:200]}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

async def cmd_uuid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = 1
    if context.args:
        try: count = min(int(context.args[0]), 10)
        except: pass
    data = await api_get("uuid", {"count": count})
    if data.get("status") == "success":
        text = f"**🆔 UUID{'s' if count>1 else ''}**\n"
        for u in data["uuids"]:
            text += f"`{u['uuid4']}`\n"
        await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/qr https://example.com`", parse_mode="Markdown")
        return
    text = " ".join(context.args)
    data = await api_get("qr", {"text": text})
    if data.get("status") == "success":
        await update.message.reply_text(f"📱 **QR Code:**\n{data['qr_url']}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

async def cmd_base64(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: `/base64 encode hello` or `/base64 decode aGVsbG8=`", parse_mode="Markdown")
        return
    mode = context.args[0].lower()
    rest = " ".join(context.args[1:])
    data = await api_get("base64", {mode: rest} if mode == "decode" else {"text": rest, "mode": mode})
    if data.get("status") == "success":
        await update.message.reply_text(f"**🔐 Base64 {mode}**\n`Output:` `{data['output'][:500]}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

async def cmd_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/translate Hello world` or `/translate Hello world fr`", parse_mode="Markdown")
        return
    to = "en"
    text_parts = context.args
    if len(context.args) > 1 and len(context.args[-1]) == 2:
        to = context.args[-1]
        text_parts = context.args[:-1]
    text = " ".join(text_parts)
    data = await api_get("translate", {"text": text, "to": to})
    if data.get("status") == "success":
        await update.message.reply_text(
            f"**🌍 Translation**\n`Original:` {data.get('original','')[:200]}\n`Translated:` {data.get('translated','')[:200]}",
            parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

# ─── INDIA COMMANDS ───
async def cmd_pan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/pan ABCPK1234F`", parse_mode="Markdown")
        return
    data = await api_get("pan", {"pan": context.args[0].upper()})
    await update.message.reply_text(fmt_json(data, "🆔 PAN Info"), parse_mode="Markdown")

async def cmd_gstin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/gstin 27AABCU1234D1Z5`", parse_mode="Markdown")
        return
    data = await api_get("gstin", {"gstin": context.args[0].upper()})
    await update.message.reply_text(fmt_json(data, "🏦 GSTIN Info"), parse_mode="Markdown")

async def cmd_voter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/voter UKL1234567`", parse_mode="Markdown")
        return
    data = await api_get("voter", {"epic": context.args[0].upper()})
    await update.message.reply_text(fmt_json(data, "🗳 Voter ID"), parse_mode="Markdown")

async def cmd_aadhaar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/aadhaar 123456789012`", parse_mode="Markdown")
        return
    data = await api_get("aadhaar-verify", {"aadhaar": context.args[0]})
    await update.message.reply_text(fmt_json(data, "🆔 Aadhaar Verify"), parse_mode="Markdown")

async def cmd_ration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/ration <number> [state]`", parse_mode="Markdown")
        return
    params = {"ration_number": context.args[0]}
    if len(context.args) > 1: params["state"] = context.args[1]
    data = await api_get("ration", params)
    await update.message.reply_text(fmt_json(data, "🍲 Ration Info"), parse_mode="Markdown")

async def cmd_samagra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/samagra 9876543210`", parse_mode="Markdown")
        return
    data = await api_get("samagra", {"mobile": context.args[0]})
    await update.message.reply_text(fmt_json(data, "👨‍👩‍👧‍👦 Samagra Info"), parse_mode="Markdown")

async def cmd_school(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/school <code>`", parse_mode="Markdown")
        return
    data = await api_get("school", {"school_code": context.args[0]})
    await update.message.reply_text(fmt_json(data, "📖 School Info"), parse_mode="Markdown")

async def cmd_vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/vehicle UP32EA1234`", parse_mode="Markdown")
        return
    data = await api_get("vehicle-rc", {"registration": context.args[0].upper()})
    await update.message.reply_text(fmt_json(data, "🚗 Vehicle RC"), parse_mode="Markdown")

async def cmd_challan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/challan UP32EA1234`", parse_mode="Markdown")
        return
    data = await api_get("challan", {"vehicle": context.args[0].upper()})
    await update.message.reply_text(fmt_json(data, "🚦 Challan Info"), parse_mode="Markdown")

async def cmd_breach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/breach email@example.com`", parse_mode="Markdown")
        return
    data = await api_get("breach", {"email": context.args[0]})
    await update.message.reply_text(fmt_json(data, "🆘 Breach Check"), parse_mode="Markdown")

async def cmd_ghuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/ghuser sudeepbots`", parse_mode="Markdown")
        return
    data = await api_get("gh-user", {"username": context.args[0]})
    await update.message.reply_text(fmt_json(data, "🐙 GitHub User"), parse_mode="Markdown")

async def cmd_wayback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/wayback google.com`", parse_mode="Markdown")
        return
    data = await api_get("wayback", {"domain": context.args[0], "limit": 5})
    await update.message.reply_text(fmt_json(data, "⏳ Wayback Machine"), parse_mode="Markdown")

async def cmd_headers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/headers https://example.com`", parse_mode="Markdown")
        return
    data = await api_get("http-headers", {"url": context.args[0]})
    await update.message.reply_text(fmt_json(data, "📋 HTTP Headers"), parse_mode="Markdown")

async def cmd_ssl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/ssl google.com`", parse_mode="Markdown")
        return
    data = await api_get("ssl-check", {"domain": context.args[0]})
    await update.message.reply_text(fmt_json(data, "🔒 SSL Check"), parse_mode="Markdown")

async def cmd_portscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/portscan google.com`", parse_mode="Markdown")
        return
    data = await api_get("port-check", {"host": context.args[0]})
    if data.get("status") == "success":
        d = data
        text = f"**🔌 Port Scan — {d['host']}**\n`Scanned:` {d['scanned']} | `Open:` {d['open_count']}\n"
        for p in d.get("open_ports", []):
            text += f"🟢 `{p['port']}` — {p['service']}\n"
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {data.get('message','Error')}")

# ─── CALLBACK ───
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.replace("cat_", "")
    
    menus = {
        "osint": "**🔍 OSINT Tools**\n\n`/ip` — IP geolocation\n`/email` — Email OSINT\n`/phone` — Phone lookup\n`/dns` — DNS records\n`/whois` — Domain WHOIS\n`/subdomain` — Subdomains\n`/detect` — Hosting detect\n`/breach` — Breach check\n`/ghuser` — GitHub user\n`/wayback` — Wayback Machine\n`/headers` — HTTP headers\n`/ssl` — SSL check\n`/portscan` — Port scanner",
        "utils": "**🛠 Utilities**\n\n`/hash` — Hash generator\n`/base64` — Base64 encode/decode\n`/uuid` — UUID generator\n`/qr` — QR code\n`/currency` — Currency converter\n`/translate` — Translation\n`/weather` — Weather\n`/pincode` — PIN code\n`/password` — Password strength\n`/ifsc` — IFSC lookup",
        "india": "**🇮🇳 India Tools**\n\n`/pan` — PAN card\n`/gstin` — GST info\n`/voter` — Voter ID\n`/aadhaar` — Aadhaar verify\n`/ration` — Ration card\n`/samagra` — MP Samagra\n`/school` — UDISE+ school\n`/vehicle` — Vehicle RC\n`/challan` — e-Challan",
        "web": "**🌐 Web Tools**\n\n`/qr` — QR generator\n`/currency` — Currency convert\n`/translate` — Text translate\n`/headers` — HTTP headers\n`/ssl` — SSL check\n`/portscan` — Port scan\n`/wayback` — Web archive\n`/detect` — Hosting detect"
    }
    
    text = menus.get(cat, "Select a category")
    kb = [[InlineKeyboardButton("◀️ Back", callback_data="cat_back")]]
    
    if cat == "back":
        kb = [
            [InlineKeyboardButton("🔍 OSINT", callback_data="cat_osint"),
             InlineKeyboardButton("🛠 Utilities", callback_data="cat_utils")],
            [InlineKeyboardButton("🇮🇳 India", callback_data="cat_india"),
             InlineKeyboardButton("🌐 Web Tools", callback_data="cat_web")]
        ]
        text = "**📂 Select Category:**"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

# ─── MAIN ───
def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        sys.exit(1)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # OSINT
    app.add_handler(CommandHandler("ip", cmd_ip))
    app.add_handler(CommandHandler("email", cmd_email))
    app.add_handler(CommandHandler("phone", cmd_phone))
    app.add_handler(CommandHandler("dns", cmd_dns))
    app.add_handler(CommandHandler("whois", cmd_whois))
    app.add_handler(CommandHandler("subdomain", cmd_subdomain))
    app.add_handler(CommandHandler("detect", cmd_detect))
    app.add_handler(CommandHandler("breach", cmd_breach))
    app.add_handler(CommandHandler("ghuser", cmd_ghuser))
    app.add_handler(CommandHandler("wayback", cmd_wayback))
    app.add_handler(CommandHandler("headers", cmd_headers))
    app.add_handler(CommandHandler("ssl", cmd_ssl))
    app.add_handler(CommandHandler("portscan", cmd_portscan))
    
    # Utilities
    app.add_handler(CommandHandler("hash", cmd_hash))
    app.add_handler(CommandHandler("base64", cmd_base64))
    app.add_handler(CommandHandler("uuid", cmd_uuid))
    app.add_handler(CommandHandler("qr", cmd_qr))
    app.add_handler(CommandHandler("currency", cmd_currency))
    app.add_handler(CommandHandler("translate", cmd_translate))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("pincode", cmd_pincode))
    app.add_handler(CommandHandler("password", cmd_password))
    app.add_handler(CommandHandler("ifsc", cmd_ifsc))
    
    # India
    app.add_handler(CommandHandler("pan", cmd_pan))
    app.add_handler(CommandHandler("gstin", cmd_gstin))
    app.add_handler(CommandHandler("voter", cmd_voter))
    app.add_handler(CommandHandler("aadhaar", cmd_aadhaar))
    app.add_handler(CommandHandler("ration", cmd_ration))
    app.add_handler(CommandHandler("samagra", cmd_samagra))
    app.add_handler(CommandHandler("school", cmd_school))
    app.add_handler(CommandHandler("vehicle", cmd_vehicle))
    app.add_handler(CommandHandler("challan", cmd_challan))
    
    # General
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("tools", tools))
    
    # Callback
    # Callback
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Start health check server in background
    async def health_server():
        from aiohttp import web
        app_web = web.Application()
        async def health(request):
            return web.Response(text="OK")
        app_web.router.add_get("/", health)
        app_web.router.add_get("/health", health)
        runner = web.AppRunner(app_web)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        logger.info(f"Health server on :{PORT}")
        await asyncio.Event().wait()
    
    asyncio.ensure_future(health_server())
    
    logger.info("Bot starting with polling...")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
