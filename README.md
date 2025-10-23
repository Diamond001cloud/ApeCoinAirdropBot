# ApeCoin Airdrop Bot (Render Ready)

A secure and fully automated Telegram bot for ApeCoin airdrop management-_compatible with pyroid 3 and Render
### 📦 Features
- Pure Python bot using environment variables only
- Admin verification and referral system
- Auto keep-alive ping for Render
- Withdraw date: 31st October 2025
- SQLite database (no external DB needed)
---

### ⚙️ Environment Variables

| Variable | Description |
|-----------|--------------|
| APECOIN_BOT_TOKEN | Your Telegram BotFather token |
| APECOIN_ADMIN_ID | Your Telegram numeric user ID |
| APECOIN_SUPPORT_LINK | Telegram support link |
| APECOIN_CHANNEL_LINK | Telegram channel invite link |
| APECOIN_GROUP_LINK | Telegram group invite link |
| APECOIN_BNB_WALLET | BNB wallet address |
| APECOIN_ETH_WALLET | ETH wallet address |
| APECOIN_USDT_BNB | USDT-BNB wallet address |
| APECOIN_USDT_ETH | USDT-ETH wallet address |
| RENDER_URL | Render service URL (for keep-alive) |

---

### 🚀 Deployment (Render)
1. Go to https://render.com  
2. Create a new **Web Service**
3. Upload these files (or connect a GitHub repo)
4. Add all environment variables above
5. Deploy — check logs for “✅ Bot started successfully and is now online.”
6. Test at `@apecoiairdrop_bot` on Telegram
