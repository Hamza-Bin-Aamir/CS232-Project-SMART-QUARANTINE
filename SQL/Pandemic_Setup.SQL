CREATE TABLE pandemics (
  id          SERIAL PRIMARY KEY,
  p_name        TEXT NOT NULL,              -- e.g., COVID-19
  date_start  DATE NOT NULL,
  date_end    DATE,                       -- NULL if ongoing
  descriptiontxt TEXT
);

CREATE TABLE pandemic_stats (
  id              SERIAL PRIMARY KEY,
  pandemic_id     INT REFERENCES pandemics(id),
  area_id         INT REFERENCES areas(id),           -- Link to GIS area
  stat_date       DATE NOT NULL,
  total_population INT,
  infected        INT,
  infection_rate  FLOAT,    -- infected / total_population or per 1000 people
  cured           INT,
  cure_rate       FLOAT,    -- cured / infected
  deaths          INT,
  death_rate      FLOAT     -- deaths / infected
);