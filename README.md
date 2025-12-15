# Callum Dashboard

Callum Dashboard is a local-first Flask app for tracking cannabis strains, PC details, games, and media lists. Data stays on disk in a SQLite database (`data/app.db`).

## Features
- Dark, high-contrast dashboard with responsive tabs for Weed, PC, Games, and Media.
- Weed tab: CRUD for strain entries (date, strain, THC %, type, terpenes, notes, rating), current strains snapshot, most-bought chart + counts, and editable recommendations list for MedBud shortlists.
- PC tab: editable fields for CPU, GPU, monitors, PSU, and storage (seeded with your 7800X3D/RTX 3070 triple-monitor build).
- Games tab: Finish / Dip in & out / Done columns with add/remove controls.
- Media tab: docs, music, and shows lists with add/remove controls.
- Uses a SQLite file in `data/` for local storage; no external services.

## Prerequisites (Windows 11)
- [Python 3.10+ for Windows](https://www.python.org/downloads/windows/) installed and added to PATH (tick "Add python.exe to PATH" during setup).
- Optional but recommended: [Git for Windows](https://git-scm.com/download/win) to clone the repo.

## Setup
1. Open **Windows Terminal** or **Command Prompt**.
2. Clone or download this repository.
3. (Recommended) Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

When you run the app for the first time it will create `data/app.db` and seed initial data if the database is empty.

## Running the dashboard
### Option A: Double-click launcher
- Use `run_dashboard.bat` in the project root. Double-clicking it will:
  1. Ensure the virtual environment is activated if present.
  2. Launch the Flask server on `http://127.0.0.1:5000`.
  3. Open your default browser to the dashboard.

### Option B: Manual command
From the project directory:
```
python app.py
```
Then open `http://127.0.0.1:5000` in your browser.

## Data storage
- All data is stored locally in `data/app.db` (SQLite). Feel free to back it up or move it with the project folder.

## Seeding
- On startup the app checks whether the database is empty; if so it imports the starter data from `seed/seed_data.json` (weed history + PC setup) and shows a one-time banner in the UI.
- To reset and trigger seeding again, close the app and delete `data/app.db` (or the entire `data/` folder), then restart the app.

## Editing entries
- **Weed tab**: double-click a row to select it for editing or deleting. Use the Add/Edit/Delete buttons for CRUD. Recommendations are a simple editable list with delete buttons.
- **PC tab**: click **Edit** to update your specs.
- **Games/Media tabs**: use the input + add buttons to append entries; remove with the corresponding remove button.

## Troubleshooting
- If `python` is not recognized, reopen your terminal after installing Python and ensure it is on PATH.
- If port 5000 is taken, edit `app.py` at the bottom to change the port number (and update the browser URL accordingly).
