# JAGARAN Crossword - Top 3 Leaderboard

This version adds a public Top 3 leaderboard using Supabase.

## Files
- app.py
- requirements.txt
- supabase_setup.sql

## Supabase setup
1. Create a Supabase project.
2. Open SQL Editor.
3. Run all SQL from `supabase_setup.sql`.
4. Copy your Project URL and public/anon key.

## Streamlit secrets
In Streamlit Community Cloud, open your app Settings -> Secrets and add:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_KEY = "YOUR-SUPABASE-ANON-KEY"
```

Use the public/anon key, NOT the service-role key.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Leaderboard
When a player completes all 8 clues, their username, score, completion time and hint count are stored. The Top 3 are shown to every visitor. Ranking is highest score first; ties use fastest time.
