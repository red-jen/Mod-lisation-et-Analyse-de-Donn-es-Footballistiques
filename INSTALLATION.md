# Installation Guide

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Step 1: Clone Repository

```bash
git clone https://github.com/red-jen/Mod-lisation-et-Analyse-de-Donn-es-Footballistiques.git
cd Mod-lisation-et-Analyse-de-Donn-es-Footballistiques
```

## Step 2: Create Virtual Environment

### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

## Step 4: Configure Database

1. Create PostgreSQL database:
```sql
CREATE DATABASE foot_ball;
```

2. Create tables (using provided SQL schema):
```sql
-- See database schema in project documentation
```

3. Update credentials in `config.json` if needed

## Step 5: Run Jupyter Notebook

```bash
jupyter notebook selenium_functions_notes.ipynb
```

## Troubleshooting

### pip not found
Use `python -m pip` instead of `pip`

### PostgreSQL connection error
- Check host, port, and credentials in config.json
- Ensure PostgreSQL is running
- Verify database exists

### Selenium timeout
- Check internet connection
- Verify FBref website is accessible
- Increase timeout in config.json

## Next Steps

1. Run web scraping cell
2. Run data cleaning cell
3. Run database insertion cell
4. Verify data in PostgreSQL
