# Dev's Tools Bot

🤖 A Telegram OSINT bot with 40+ legal intelligence tools powered by [YUKI OSINT API](https://osint.yukiapi.site).

## 🚀 Features

### 🔍 OSINT
| Command | Description |
|:--------|:------------|
| `/ip [ip]` | IP geolocation & ISP |
| `/email <email>` | Full email OSINT (breach, gravatar, provider) |
| `/phone <number>` | Phone carrier info |
| `/dns <domain>` | DNS records (A, AAAA, MX, NS) |
| `/whois <domain>` | Domain WHOIS info |
| `/subdomain <domain>` | Subdomain finder with alive check |
| `/detect <domain>` | Website hosting platform detection |
| `/breach <email>` | Breach check via HIBP |
| `/ghuser <username>` | GitHub user public info |
| `/wayback <domain>` | Wayback Machine history |
| `/headers <url>` | HTTP security headers check |
| `/ssl <domain>` | SSL certificate expiry check |
| `/portscan <host>` | Common port scanner |

### 🛠 Utilities
| Command | Description |
|:--------|:------------|
| `/hash <text>` | MD5, SHA1, SHA256, SHA512 generator |
| `/base64 encode/decode` | Base64 encode/decode |
| `/uuid [count]` | UUID generator |
| `/qr <text>` | QR code generator |
| `/currency <amt> <from> <to>` | Currency converter |
| `/translate <text> [to]` | Text translation |
| `/weather <city>` | Current weather |
| `/pincode <code>` | India PIN code lookup |
| `/password <pass>` | Password strength checker |
| `/ifsc <code>` | IFSC bank details |

### 🇮🇳 India
| Command | Description |
|:--------|:------------|
| `/pan <pan>` | PAN card info |
| `/gstin <gstin>` | GST registration details |
| `/voter <epic>` | Voter ID / EPIC details |
| `/aadhaar <number>` | Aadhaar format validation |
| `/ration <number>` | Ration card info |
| `/samagra <mobile>` | MP Samagra family details |
| `/school <code>` | UDISE+ school directory |
| `/vehicle <reg>` | Vehicle RC details |
| `/challan <reg>` | e-Challan info |

## 🛠 Tech Stack

- **Python 3.12** — Runtime
- **python-telegram-bot 21** — Bot framework
- **httpx** — Async HTTP client
- **YUKI OSINT API** — Backend engine
- **Railway** — Hosting

## ⚡ Deploy on Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/xxxxx)

```bash
# Clone
git clone https://github.com/SUDEEPBOTS/DevsToolsBot.git
cd DevsToolsBot

# Install
pip install -r requirements.txt

# Set env
export BOT_TOKEN=your_bot_token
export API_BASE=https://osint.yukiapi.site/api

# Run
python3 bot.py
```

## 📝 Environment Variables

| Variable | Description | Required |
|:---------|:------------|:--------:|
| `BOT_TOKEN` | Telegram Bot Token | ✅ |
| `API_BASE` | OSINT API base URL | ❌ (default: https://osint.yukiapi.site/api) |

## 📄 License

MIT License

---

⚡ Powered by @hostillbot
