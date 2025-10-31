# Database Schema

## Tables Overview

### 1. competition
Stores competition information.

```sql
CREATE TABLE competition (
    idcompetition SERIAL PRIMARY KEY,
    nomcompetition VARCHAR(255) NOT NULL UNIQUE
);
```

**Columns:**
- `idcompetition`: Primary key
- `nomcompetition`: Competition name (e.g., "Premier League")

---

### 2. saison
Stores season information.

```sql
CREATE TABLE saison (
    id_saison SERIAL PRIMARY KEY,
    annee VARCHAR(20) NOT NULL UNIQUE
);
```

**Columns:**
- `id_saison`: Primary key
- `annee`: Season year (e.g., "2024-2025")

---

### 3. equipe
Stores team information.

```sql
CREATE TABLE equipe (
    idequipe SERIAL PRIMARY KEY,
    nomequipe VARCHAR(255) NOT NULL,
    idcompetition INT NOT NULL,
    id_saison INT NOT NULL,
    FOREIGN KEY (idcompetition) REFERENCES competition(idcompetition),
    FOREIGN KEY (id_saison) REFERENCES saison(id_saison),
    UNIQUE(nomequipe, idcompetition, id_saison)
);
```

**Columns:**
- `idequipe`: Primary key
- `nomequipe`: Team name
- `idcompetition`: FK to competition
- `id_saison`: FK to saison

---

### 4. joueur
Stores player information.

```sql
CREATE TABLE joueur (
    idjoueur SERIAL PRIMARY KEY,
    nomjoueur VARCHAR(255) NOT NULL,
    position VARCHAR(50),
    nationalite VARCHAR(100),
    id_equipe INT NOT NULL,
    FOREIGN KEY (id_equipe) REFERENCES equipe(idequipe),
    UNIQUE(nomjoueur, id_equipe)
);
```

**Columns:**
- `idjoueur`: Primary key
- `nomjoueur`: Player name
- `position`: Player position (e.g., "MF", "FW")
- `nationalite`: Player nationality
- `id_equipe`: FK to equipe

---

### 5. match
Stores match information.

```sql
CREATE TABLE match (
    idmatch SERIAL PRIMARY KEY,
    date_match DATE NOT NULL,
    heure VARCHAR(10),
    round_match VARCHAR(100),
    venue VARCHAR(20),
    idteamhome INT NOT NULL,
    id_competition INT NOT NULL,
    id_saison INT NOT NULL,
    resultat VARCHAR(20),
    FOREIGN KEY (idteamhome) REFERENCES equipe(idequipe),
    FOREIGN KEY (id_competition) REFERENCES competition(idcompetition),
    FOREIGN KEY (id_saison) REFERENCES saison(id_saison)
);
```

**Columns:**
- `idmatch`: Primary key
- `date_match`: Match date
- `heure`: Match time
- `round_match`: Competition round
- `venue`: Home/Away
- `idteamhome`: FK to equipe (home team)
- `id_competition`: FK to competition
- `id_saison`: FK to saison
- `resultat`: Match result (W/D/L)

---

## Relationships

```
competition (1) ----→ (N) equipe
    ↓
    └─→ (N) match

saison (1) ----→ (N) equipe
    ↓
    └─→ (N) match

equipe (1) ----→ (N) joueur
    ↓
    └─→ (N) match

match ← connects Home Team from equipe
```

---

## Example Queries

### Get all players from Liverpool
```sql
SELECT j.nomjoueur, j.position, j.nationalite
FROM joueur j
JOIN equipe e ON j.id_equipe = e.idequipe
WHERE e.nomequipe = 'Liverpool';
```

### Get all matches for Arsenal in 2024-2025
```sql
SELECT m.date_match, m.heure, m.resultat
FROM match m
JOIN equipe e ON m.idteamhome = e.idequipe
WHERE e.nomequipe = 'Arsenal'
AND m.id_saison = (SELECT id_saison FROM saison WHERE annee = '2024-2025');
```

### Count players per team
```sql
SELECT e.nomequipe, COUNT(j.idjoueur) as total_players
FROM equipe e
LEFT JOIN joueur j ON e.idequipe = j.id_equipe
GROUP BY e.nomequipe
ORDER BY total_players DESC;
```
