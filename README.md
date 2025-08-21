# IUTCessa Bot — Telegram Bot for IUT Computer Engineering Student Scientific Association 🛠🤖

**IUTCessa Bot** is a Telegram bot specifically designed for the Computer Engineering Department at Isfahan University of Technology (IUT), under the supervision of the IUT Computer Engineering Student Scientific Association (IUTCessa).

---

## 🚀 Goal

Its primary goal is to establish a management and automation system for various association initiatives, such as:

- **Kmkyar** — a program to help with volunteer assistance program 🤝
- **Tech-Stack Mentoring Courses** — Tech Stack mentoring courses 📚

---

## 🧩 Main Parts

- **Tech Stack (`techstack`)** — handles key tasks including launching registration panels, sending general or targeted notifications, managing priority selection panels, database administration, and overseeing payment receipts. (Both user and admin panels)
- **Volunteer Program (`kmkyar`)** — apply to help, and get links for the selected group.

---

## 🤖 AI Helper (v1.3.0+)

A new AI part (run by the Gemma model) was added and is still being worked on. It can now:

- **TL;DR / sum up** — make long texts short and easy to get.
- **Ask / chat mode** — ask the bot things and talk to it in simple words.

> Note: the AI helper is still being tested and changed — look for more and better parts.

---

## ⚙️ Configuration

Configuration is provided via environment variables loaded from a local `.env` file (not committed).
Use `.env.sample` as a template.

Key modules you may edit:

- `src/core/tokens.py` *(deprecated — use `.env` instead)*  
- `src/core/command_functions.py`
- Other helpers in `src/core/`

---

## 🛠 How to Run (with Docker — preferred)

**Requirements**

* Docker & Docker Compose (v2)

**What’s included**

* Image built from `src/Dockerfile`
* Compose service `iutcessa-bot`
* Non-root user inside the container
* Code bind-mounted for easy iteration

### 1) Clone the repo

```bash
git clone https://github.com/Nec-ro/IUTCessa_Bot.git
cd IUTCessa_Bot
```

### 2) Create your env file (at the repo root)

```bash
cp .env.sample .env
```

Open `.env` and fill in required values (bot token, admin IDs, group IDs, AI keys, etc.).

> If you see `No .env found` in logs, ensure the file is named exactly `.env` and is placed **at the repository root**, not inside `src/`.

### 3) Build and start with Docker Compose

```bash
docker compose up --build
```

---

## 🧪 Local (non-Docker) — alternative

If you’d rather run it locally:

1. **Clone the repo**

   ```bash
   git clone https://github.com/Nec-ro/IUTCessa_Bot.git
   cd IUTCessa_Bot
   ```

2. **Create & activate a virtual environment**

   *macOS/Linux*

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   *Windows (PowerShell)*

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create your env file**

   ```bash
   cp .env.sample .env
   ```

   Fill in tokens/IDs.

5. **Run the bot**

   ```bash
   cd src
   python main.py
   ```

---

## 🧾 Issues & Contributions

This project is **free to use** — we like help, bug reports, and ideas for new stuff!
If you face any issues, please open an **Issue** on the GitHub page.
We welcome pull requests — from small fixes to big new things. 🙌

---

## 📎 Project Layout (key parts)

```
src/
  core/
    command_functions.py
    # tokens.py (legacy; use .env instead)
  kmkyar/
  techstack/
  interface/
  main.py
```

---

## ❤️ Ending Words

This bot was made (with love 💖) to help the IUT Computer Engineering group work better and cut down on admin work.
If you need help fitting it to your server, adding stuff, or using the new AI part, we’re happy to help — and we’d love your contributions! 👨‍💻👩‍💻
