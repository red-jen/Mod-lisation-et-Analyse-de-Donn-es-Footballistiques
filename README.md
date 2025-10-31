# Modélisation et Analyse de Données Footballistiques

## Project Overview

This project develops a comprehensive predictive analysis solution for professional football by leveraging large-scale data from FBref. The goal is to create a data-driven ecosystem that can predict match outcomes and optimize team strategies.

## Architecture

The project follows a structured data pipeline:

1. **Web Scraping** - Collect Premier League data from FBref
2. **Data Cleaning & Transformation** - Standardize and prepare data
3. **Database Storage** - Store in PostgreSQL
4. **Analysis & Modeling** - Build predictive models

## Project Structure

```
├── selenium_functions_notes.ipynb  # Main notebook with pipeline
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── data/                          # Raw scraped data (team directories)
├── processed_data/                # Cleaned and transformed data
└── .gitignore                     # Git ignore rules
```

## Data Pipeline

### Phase 1: Web Scraping
- Target: FBref Premier League 2024-2025 season
- Data: Player stats and match records
- Method: Selenium + CSS selectors
- Output: CSV files per team

### Phase 2: Data Cleaning
- Remove duplicates
- Handle missing values
- Standardize column names and formats
- Convert data types

### Phase 3: Database Storage
Tables:
- `competition` - League information
- `saison` - Season details
- `equipe` - Teams
- `joueur` - Players
- `match` - Match records

## Database Configuration

PostgreSQL Connection:
```
Host: localhost
Database: foot_ball
User: postgres
```

## Usage

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Run the Pipeline
Execute the notebook cells in order:
- Cell 1: Web Scraping
- Cell 2: Data Cleaning
- Cell 3: Database Insertion

## Data Dictionary

### Players Table (joueur)
- nomjoueur: Player name
- position: Player position
- nationalite: Player nationality
- id_equipe: Team reference

### Matches Table (match)
- date_match: Match date (datetime)
- heure: Match time
- round_match: Competition round
- venue: Home/Away
- idteamhome: Home team reference
- resultat: Match result (W/D/L)

## Notes

- Data is collected from FBref
- Premier League 2024-2025 season
- 20 teams with player and match statistics
- CSV files stored in team-specific directories
- Cleaned data exported to processed_data folder

## Author

Red-jen

## Date

October 31, 2025