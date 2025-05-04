CREATE TABLE pandemics (
  id          SERIAL PRIMARY KEY,
  p_name        TEXT NOT NULL,              -- e.g., COVID-19
  date_start  DATE NOT NULL,
  date_end    DATE,                       -- NULL if ongoing
  descriptiontxt TEXT
);
