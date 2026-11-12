# Task 4 Submission Guide

Everything is ready. You just need to push to GitHub and post on LinkedIn.

---

## Step 1 — Push to GitHub

Open **Git Bash** (or any terminal) in the `SWYNEX-Final-AI-Application` folder:

```bash
cd "D:\SWYNEX-Internship\SWYNEX-Final-AI-Application"
```

Then run these once to initialise and push:

```bash
git init -b main
git config user.name "SaiKarun-28"
git config user.email "your@email.com"       # use your GitHub email
git add .
git commit -m "SWYNEX Final AI Application: Smart Task Parser"
git remote add origin https://github.com/SaiKarun-28/SWYNEX-Final-AI-Application.git
git push -u origin main
```

**If the repo doesn't exist yet on GitHub:**
1. Go to https://github.com/new
2. Name it exactly: `SWYNEX-Final-AI-Application`
3. Leave it empty (no README, no .gitignore)
4. Run the push command above

**Authentication tip:** If GitHub asks for a password, use a Personal Access Token (PAT), not your actual password. Generate one at: https://github.com/settings/tokens (select `repo` scope).

---

## Step 2 — Submit to SWYNEX Dashboard

1. Go to https://swynex.com/dashboard → Task 4
2. **Task submission link:** `https://github.com/SaiKarun-28/SWYNEX-Final-AI-Application`
3. **LinkedIn explanation post link:** (paste your LinkedIn post URL after posting in Step 3)

---

## Step 3 — Post on LinkedIn

See `LINKEDIN_POST.md` for the draft. Post it, then copy the URL back into the dashboard form.

**Checklist before you submit:**
- [ ] GitHub repo is public and named `SWYNEX-Final-AI-Application`
- [ ] README, all `.py` files, `requirements.txt`, `.env.example` are in the repo
- [ ] `.env` is NOT in the repo (confirmed — it's in `.gitignore`)
- [ ] LinkedIn post mentions @SWYNEX Technologies, has a screenshot or demo, uses #SWYNEX #Internship
- [ ] Both links pasted into the SWYNEX dashboard form
- [ ] Click "Submit task"
