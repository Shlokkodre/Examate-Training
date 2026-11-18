# HealthLabelCheck

## Project Card

- **Product:** HealthLabelCheck — Checks a small food maker's packet label against FSSAI's Labelling and Display Regulations and lists exactly what is missing before they print.
- **Target user:** A woman running a home-based chakli and laddoo business in Kopargaon who wants to sell packed snacks in Shirdi shops and does not know what must be printed on the pouch.
- **Problem:** Small food business owners don't know what mandatory declarations, font sizes, and symbols are required by FSSAI regulations before printing their food packet labels.
- **Proposed data source:** PDF (regulation text with tables and schedules) - FSSAI Labelling and Display Regulations
  - https://fssai.gov.in/upload/uploadfiles/files/Compendium_Labelling_Display_04_01_2022.pdf
  - https://fssai.gov.in/upload/media/FSSAI_News_Packaged_FNB_04_01_2020.pdf

## Key Features

1. **Label checklist:** User ticks what is printed on their pouch and gets a green/red table of all 14 mandatory declarations with the exact regulation number for each missing item.
2. **min_font_size_checker:** Computes the panel area from length × width and returns the minimum font height for the net quantity and other declarations.

## Sample Questions

1. What things must be printed on a packed food label as per FSSAI?
2. What is the rule for the vegetarian green dot symbol?
3. Is nutrition information required on every packet?
4. My chakli pouch front is 12 cm by 8 cm, what minimum font size do I need for net weight?
5. Which labelling rules changed in the 2021 amendment compared to the original 2020 regulation?
6. What is the cheapest printing shop for food pouches in Kopargaon?

## Data Schema

Fields extracted from regulations:
- `regulation_no`: Regulation number (e.g., "5.1", "6.2")
- `requirement`: What must be displayed
- `applies_to`: Product categories this applies to
- `details`: Specific requirements and conditions
- `exemption`: Any exemptions that apply
- `source_doc`: Source document reference

## Disclaimer

Information from FSSAI regulations, not legal advice. Confirm with FSSAI or a food safety officer before printing labels.

## Deploy

### Render (Docker)
1. Push repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com) → New → Blueprint
3. Connect your repo — Render picks up `render.yaml` automatically
4. Set `GROQ_API_KEY` as a secret environment variable in the Render dashboard
5. Deploy — live at `https://healthlabelcheck.onrender.com`

### Hugging Face Spaces
1. Create a new Space → SDK: Streamlit
2. Push repo (rename `README_HF.md` to `README.md` for the Space)
3. Add `GROQ_API_KEY` in Space Settings → Repository Secrets
4. HF Spaces auto-deploys on push

## Run the scripts

### Day 1-2: Python Scripts
```bash
# Day 1 scripts
python day01_intro.py
python day01_menu.py

# Day 2 scripts
python -m app.cli  # Interactive CLI
python -m app.ingest  # Process and save records
python -m app.fetch  # Fetch FSSAI documents
```

### Day 3: Data Analysis
```bash
# Ingest data
python -m app.ingest

# Run analysis
python -m analysis.explore

# Test smart search
python -m app.smart_search
```

### Day 4: FastAPI Web Service

First, install dependencies:
```bash
pip install -r requirements.txt
```

Run the API server:
```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload

# Option 2: Using Python
python -m app.main
```

The API will be available at: `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Key Endpoints:**
- `GET /health` - Health check
- `GET /records` - List regulations (with limit)
- `GET /records/{regulation_no}` - Get specific regulation
- `GET /search?q=keyword` - Smart search with TF-IDF ranking
- `POST /questions` - Ask questions about regulations
- `POST /font-size` - Calculate minimum font size
- `GET /mandatory-checklist` - Get all mandatory requirements


## RAG Evaluation Results

Two configurations tested on 15 questions (`eval/eval_set.json`):

```
Config                           Passed   Citation    Keyword    Scope
----------------------------------------------------------------------
Config A: top_k=3, full          13/15     13/15     15/15   15/15
Config B: top_k=5, short         15/15     15/15     15/15   15/15
```

**Winner**: Config B: top_k=5, short

Metrics: citation_hit = at least one expected regulation cited;
keyword_hit = at least one expected keyword in answer;
scope_correct = out-of-scope questions answered with "I don't know".

Run: `python eval/run_eval.py`


## RAG Evaluation Results

Two configurations tested on 15 questions (`eval/eval_set.json`):

```
Config                           Passed   Citation    Keyword    Scope
----------------------------------------------------------------------
Config A: top_k=3, full          12/15     12/15     14/15   15/15
Config B: top_k=5, short         15/15     15/15     15/15   15/15
```

**Winner**: Config B: top_k=5, short

Metrics: citation_hit = at least one expected regulation cited;
keyword_hit = at least one expected keyword in answer;
scope_correct = out-of-scope questions answered with "I don't know".

Run: `python eval/run_eval.py`


## RAG Evaluation Results

Two configurations tested on 15 questions (`eval/eval_set.json`):

```
Config                           Passed   Citation    Keyword    Scope
----------------------------------------------------------------------
Config A: top_k=3, full          12/15     12/15     14/15   15/15
Config B: top_k=5, short         15/15     15/15     15/15   15/15
```

**Winner**: Config B: top_k=5, short

Metrics: citation_hit = at least one expected regulation cited;
keyword_hit = at least one expected keyword in answer;
scope_correct = out-of-scope questions answered with "I don't know".

Run: `python eval/run_eval.py`
