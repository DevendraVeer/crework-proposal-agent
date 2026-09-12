# Crework Proposal Agent — Setup & Run Guide

## 0. Prerequisites (10 min)

- **Python 3.11+** installed. Check with `python3 --version`.
- **A Groq API key** — free. Go to https://console.groq.com → API Keys →
  Create key. Copy it somewhere safe.
- **A Telegram account** on your phone (you probably already have one).
- **ngrok** — free. Go to https://ngrok.com/download, sign up, install,
  and run `ngrok config add-authtoken <your-token>` (token is on your
  ngrok dashboard). You only need this for Step 5 (the approval-loop
  demo) — Steps 1-4 don't need it.

---

## 1. Get the project onto your machine

Unzip the project folder you received, `cd` into it:

```bash
cd crework-proposal-agent
```

## 2. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

This will take a few minutes the first time — `sentence-transformers`
pulls in a small ML model.

## 3. Set up your secrets

```bash
cp .env.example .env
```

Open `.env` and paste in your Groq key:

```
GROQ_API_KEY=gsk_your_real_key_here
TELEGRAM_BOT_TOKEN=leave_blank_for_now
TELEGRAM_CHAT_ID=leave_blank_for_now
```

(Telegram values come in Step 4 — you can run Steps 1-3 below without them.)

## 4. Build the retrieval index

This reads everything in `data/past_proposals/` and embeds it.

```bash
python scripts/build_index.py
```

You should see: `Indexed 5 past proposals -> data/proposal_index.faiss`

**📸 Screenshot #1 here** — this terminal output.

## 5. Run the core pipeline on a sample call (no Telegram needed yet)

```bash
python scripts/run_pipeline.py data/transcripts/call_1_marketing_agency.txt
```

This prints, in order: the transcript being loaded, the extracted JSON,
which past proposal it matched against, and the final drafted proposal.

**📸 Screenshot #2** — the extracted JSON block.
**📸 Screenshot #3** — the "Matched: ..." line showing which past proposal
it picked and the similarity score.
**📸 Screenshot #4** — the full drafted proposal output.

Repeat for the other two transcripts to have three worked examples:

```bash
python scripts/run_pipeline.py data/transcripts/call_2_it_services.txt
python scripts/run_pipeline.py data/transcripts/call_3_ecommerce_ops.txt
```

If any of the three produces a noticeably weaker draft, keep that one —
it's honest material for the Limitations section of the write-up.

---

## 6. Set up Telegram (for the phone-approval part)

1. Open Telegram, search **@BotFather**, send `/newbot`, name it something
   like `Crework Proposal Bot`. It gives you a token that looks like
   `123456:ABC-def...` — that's your `TELEGRAM_BOT_TOKEN`.
2. Search **@userinfobot**, send it any message, it replies with your
   numeric ID — that's your `TELEGRAM_CHAT_ID`.
3. Paste both into `.env`.
4. Open a chat with your new bot and send it any message (bots can't
   message you first until you've messaged them once).

**📸 Screenshot #5** — the BotFather conversation showing your bot created.

## 7. Run the full server and expose it

Terminal 1:
```bash
uvicorn app.main:app --reload --port 8000
```

Terminal 2:
```bash
ngrok http 8000
```

ngrok prints a public URL like `https://abcd1234.ngrok-free.app`. Copy it.

## 8. Register the Telegram webhook

Replace both placeholders and run this once (any terminal):

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_NGROK_URL>/telegram-webhook"
```

You should get back `{"ok":true,"result":true,...}`.

## 9. Trigger a real end-to-end run

Easiest way: open `http://localhost:8000/docs` in your browser (FastAPI's
built-in Swagger UI), expand **POST /process-call**, click **Try it out**,
and paste this into the request body (swap in the actual transcript text
from `data/transcripts/call_1_marketing_agency.txt`):

```json
{
  "transcript": "paste the full contents of the .txt file here"
}
```

Click **Execute**. This is a genuinely good screenshot — it shows the
request and response in one frame.

Prefer the terminal? This one-liner builds the JSON body from the file
for you:

```bash
python3 -c "import json,sys; print(json.dumps({'transcript': open('data/transcripts/call_1_marketing_agency.txt').read()}))" \
  | curl -X POST http://localhost:8000/process-call -H "Content-Type: application/json" -d @-
```

**📸 Screenshot #6** — the Swagger `/docs` page mid-request, or the curl
response showing the returned draft JSON.

Check your phone — you should have a Telegram message with the draft and
three buttons.

**📸 Screenshot #7** — the Telegram approval card on your phone.

Tap **Approve & Send**.

**📸 Screenshot #8** — the confirmation toast, and the new file that
appears in `output/proposal_<id>.md`.

---

## 🎥 This entire Step 9 (from hitting the endpoint to tapping Approve on
your phone) is your GIF. See `SCREENSHOT_GUIDE.md` for the exact shot
list and recording tips.

---

## 10. Finalize and submit (the step it's easy to forget)

Everything above gets you a working system and 8 screenshots + a GIF sitting
on your machine. This step turns that into the thing you actually send.

1. **Drop your screenshots into WRITEUP.md.** Open it, find each
   `[SCREENSHOT N — ...]` line, delete it, paste the image in its place
   (drag-and-drop works in most markdown editors, or use standard
   markdown image syntax `![](01-index-build.png)` if you're hosting them
   in the repo). Drop the GIF in at the `[GIF HERE — ...]` line the same
   way.

2. **Push the code to GitHub** so there's a real, checkable link — every
   project you listed in your original email to Shikshita (Relvio, Whispr,
   SCM Assistant) had one, this should too:
   ```bash
   git init
   git add .
   git commit -m "Crework buildathon: sales-call proposal agent"
   ```
   Then create an empty repo on github.com (don't initialize it with a
   README), and:
   ```bash
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git branch -M main
   git push -u origin main
   ```
   **Double check `.env` did NOT get committed** — `git status` should
   not show it (it's in `.gitignore`, but verify before pushing anywhere
   public).

3. **Paste the repo URL** into the `[GITHUB REPO LINK HERE]` placeholder
   near the top of WRITEUP.md.

4. **Send it back.** Reply to the email that gave you the assignment
   with: the topic you chose (WRITEUP.md already states this up top),
   WRITEUP.md itself — either paste it into a Notion doc / Google Doc and
   share that, or export it to PDF, or just link the GitHub repo where
   it's readable as `WRITEUP.md` — plus the GIF, either attached directly
   or linked if it's too large to attach.

That's the whole thing, done.

---

## Troubleshooting

- **`ModuleNotFoundError`** — you forgot to activate the venv
  (`source .venv/bin/activate`) or forgot `pip install -r requirements.txt`.
- **Groq errors about the model name** — models get deprecated
  occasionally (this happened to you before with a different project).
  If `llama-3.3-70b-versatile` errors as unavailable, check
  https://console.groq.com/docs/models for the current recommended model
  and swap the `MODEL_NAME` value in `app/config.py`.
- **Telegram webhook not firing** — the ngrok URL changes every time you
  restart ngrok on the free tier. If you restart it, redo Step 8 with the
  new URL.
- **Extraction JSON fails to parse** — this means Groq returned something
  that isn't valid JSON despite `response_format={"type": "json_object"}`.
  Rare, but if it happens, just rerun — paste me the raw output if it
  keeps happening and I'll tighten the prompt.
- **Anything else breaks** — paste me the exact error and which step you
  were on, I'll fix it fast.
