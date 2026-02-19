# Wetland Soil Color Identifier (Prototype)

This repository includes a lightweight prototype for estimating from a soil photo:

- **Matrix Munsell color**
- **Relative amount of matrix (%)**
- **Secondary/redox feature colors and percentages**

> ⚠️ This is a starting point and is **not a regulatory-grade determination tool**.

## Option A (recommended first): Command-line workflow

This is the easiest path to get started because it avoids web-app setup complexity.

### 0) Make sure the project files are on your computer

If you only chatted with Codex but did not download/clone the repo to your own machine yet, do that first.

You should have a local folder named `Natural-Resources` with files such as:

- `README.md`
- `requirements.txt`
- `cli.py`

#### How to get these files onto your computer

If you used Codex in the browser, the project files are in a remote workspace until you copy them to your machine.

Choose one method:

1. **Download ZIP from your git host (easiest):**
   - Open your repository page in the browser.
   - Click **Code** → **Download ZIP**.
   - Extract it to a folder like `Documents\Natural-Resources`.

2. **Clone with Git (best for updates):**

   ```powershell
   git clone <your-repo-url> "C:\Users\<you>\Documents\Natural-Resources"
   ```

3. **If your company blocks git/zip downloads:** ask IT to provide the repo as a folder copy on your machine.

After that, open PowerShell in that extracted/cloned `Natural-Resources` folder.

#### Troubleshooting: ZIP only contains `.gitkeep`

If the ZIP has only a `.gitkeep` file, you likely downloaded from an empty repo/branch (or the wrong repository).

1. Go back to the repository page and confirm you can see files like `README.md`, `cli.py`, and `requirements.txt` in the file list before downloading.
2. If you only see `.gitkeep` on the page itself, your code was not pushed there yet. Use **Create PR** in Codex first, merge it, then download ZIP from the updated branch.
3. Make sure you are downloading the correct branch (for example `main` after merge), not a blank starter branch.

### 1) Open a terminal **in the project folder**

Your terminal must be inside the `Natural-Resources` folder before running install commands.

On **Windows (PowerShell)**:

1. Open File Explorer and browse to your `Natural-Resources` folder.
2. Click the address bar, type `powershell`, and press Enter.
3. Run `dir requirements.txt`.
4. If you see `requirements.txt`, you are in the correct folder.

Alternative in PowerShell:

```powershell
cd "C:\path\to\Natural-Resources"
dir requirements.txt
```

### 2) Install dependencies

Windows PowerShell (`py` launcher):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3) Run analysis on one image

```bash
python cli.py path/to/soil_photo.jpg --pretty
```

Windows PowerShell equivalent:

```powershell
py cli.py path\to\soil_photo.jpg --pretty
```

Example output:

```json
{
  "image": "path/to/soil_photo.jpg",
  "soil_coverage_percent": 93.4,
  "matrix": {
    "munsell": "10YR 4/2",
    "percentage": 79.8,
    "representative_hex": "#8a7459"
  },
  "secondary_features": [
    {
      "munsell": "N 5/",
      "percentage": 20.2,
      "representative_hex": "#808080"
    }
  ]
}
```

## Option B (optional): Streamlit web app

If you want upload UI, install Streamlit dependencies and run:

```bash
pip install -r requirements-streamlit.txt
streamlit run app.py
```

## What the prototype does internally

1. Loads an image.
2. Detects likely soil pixels using a broad HSV-based filter.
3. Clusters soil colors into dominant groups (matrix + secondary features).
4. Maps each cluster centroid to the nearest known Munsell chip from `data/munsell_palette.csv`.

## Suggested next improvements

- Add a **color calibration card** workflow (white balance + exposure correction).
- Train a semantic segmentation model to isolate soil sample from tray/background.
- Expand the Munsell reference table to full chips used in wetland work.
- Add confidence scoring and "needs retake" quality checks.
- Save reports (image, matrix %, redox %, and chip matches) for field records.
