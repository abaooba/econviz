# Phase 5 — Polish & Deploy

**Objective:** Write the README, add docstrings, deploy to Streamlit Cloud, and do a final QA pass so EconViz is fully portfolio-ready with a public URL.

**Estimated duration:** 2 days

---

## Tasks

1. **Write README.md**
   - Place at project root: `~/Documents/Claude/Projects/econviz/README.md`
   - Sections:
     - Project description (2-3 sentences)
     - Live demo link (Streamlit Cloud URL — fill in after deploy)
     - Screenshots (add 1-2 after deploy)
     - Tech stack table
     - How to run locally (step-by-step: clone, create venv, set `.env`, `streamlit run src/app.py`)
     - How to get a FRED API key
     - Project structure (file tree)
     - License (MIT)

2. **Add docstrings and type hints**
   - Add Google-style docstrings to all public functions in `src/fetch.py`, `src/transform.py`, `src/charts.py`
   - Add type hints to all function signatures
   - Run `python -m py_compile src/*.py` to confirm no syntax errors

3. **Create Streamlit secrets config**
   - Create `.streamlit/secrets.toml` with the structure (do NOT put real key here — it's for reference only):
     ```toml
     FRED_API_KEY = "your_key_here"
     ```
   - Update `src/config.py` to fall back to `st.secrets` when `os.getenv` returns None (Streamlit Cloud pattern)
   - Add `.streamlit/secrets.toml` to `.gitignore`

4. **Deploy to Streamlit Cloud** ⚠️ *Requires Ares's input*
   - Push the project to a public GitHub repo (Ares does this)
   - Log into https://share.streamlit.io and connect the repo
   - In App Settings → Secrets, paste `FRED_API_KEY = "<real_key>"`
   - Verify the deployed app loads and all charts render
   - Copy the public URL and paste it into README.md

5. **Final QA checklist**
   - [ ] All 5 indicators load and chart correctly
   - [ ] Recession bands visible on each chart
   - [ ] Compare tab works for all indicator pairs
   - [ ] CSV download produces valid files
   - [ ] Error banner shows when API key is absent (test by temporarily clearing secrets)
   - [ ] App loads in under 5 seconds on first visit (cold cache)
   - [ ] No unhandled Python exceptions in Streamlit logs

---

## Dependencies

- Phases 1–4 complete
- GitHub account (Ares already has one)
- FRED API key in hand

## Items Requiring Ares's Input

- **GitHub repo creation**: Create a new public repo (e.g. `econviz`) and push the project. Claude Code can generate the git commands.
- **Streamlit Cloud account**: Sign up at https://share.streamlit.io (free, uses GitHub login)
- **Deploy step**: Log into Streamlit Cloud, connect the GitHub repo, and paste the FRED API key into secrets. Claude Code cannot do this step — it requires browser interaction.
- **Public URL**: After deploy, paste the Streamlit URL into the README live demo link.

---

## Definition of Done

- README.md complete with live demo link and local run instructions
- All public functions have docstrings and type hints
- App deployed and accessible at a public Streamlit Cloud URL
- Final QA checklist fully checked off
- Project folder is self-contained and portfolio-ready
