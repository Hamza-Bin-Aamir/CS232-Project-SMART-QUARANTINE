CREATE TABLE pandemics (
  id          SERIAL PRIMARY KEY,
  p_name        TEXT NOT NULL,              -- e.g., COVID-19
  date_start  DATE NOT NULL,
  date_end    DATE,                       -- NULL if ongoing
  descriptiontxt TEXT
);

CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE economic_zone(
    e_zone          INTEGER 
                    PRIMARY KEY
                    NOT NULL,

    e_zone_name     VARCHAR(20)
                    NOT NULL,

    timing_start    TIME, -- A null value means the timing_start is at the start of day
    
    timing_end      TIME, -- A null value means the timing_end is at the end of day

    -- Both null means the timing lasts the whole day

    p_impact        DECIMAL(5,2)
                    NOT NULL,
);

CREATE TABLE econ_makeup(
    ref_id              SERIAL PRIMARY KEY NOT NULL,
    zone1               INTEGER,
	FOREIGN KEY (zone1) REFERENCES economic_zone(e_zone),
    zone1_percentage    DECIMAL(5, 2),
    zone2               INTEGER,
	FOREIGN KEY (zone2) REFERENCES economic_zone(e_zone),
    zone2_percentage    DECIMAL(5, 2),
    zone3               INTEGER,
	FOREIGN KEY (zone3) REFERENCES economic_zone(e_zone),
    zone3_percentage    DECIMAL(5, 2),
    zone4               INTEGER,
	FOREIGN KEY (zone4) REFERENCES economic_zone(e_zone),
    zone4_percentage    DECIMAL(5, 2)
);

CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    econ_makeup_id INTEGER, 
	FOREIGN KEY (econ_makeup_id) REFERENCES econ_makeup(ref_id),  
    zone_id INTEGER REFERENCES zones(id),
    name TEXT
);

CREATE TABLE area_adj (
    src      INTEGER,
	FOREIGN KEY (src) REFERENCES areas(id),
    dest        INTEGER,
	FOREIGN KEY (dest) REFERENCES areas(id),
    adj_power   DECIMAL (5, 2)
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

CREATE TABLE economic_zone_adj(
    source              INTEGER
                        FOREIGN KEY REFERENCES economic_zone(e_zone)
                        NOT NULL,
    
    dest                INTEGER
                        FOREIGN KEY REFERENCES economic_zone(e_zone)
                        NOT NULL,
    
    adjacency_power     DECIMAL(5, 2)
                        NOT NULL
);

CREATE TABLE policy_type(
    p_type              SERIAL 
                        PRIMARY KEY 
                        NOT NULL,

    e_zone              INTEGER 
                        FOREIGN KEY REFERENCES economic_zone(e_zone) 
                        NOT NULL,

    time_frame_start    TIME, -- A null value means the time_frame_start is at the start of day

    time_frame_end      TIME, -- A null value means the time_frame_end is at the end of day
    
    -- Both null means the time frame lasts the whole day
);

CREATE TABLE policies(
    policy_id   SERIAL 
                PRIMARY KEY 
                NOT NULL,

    pandemic_id INTEGER
                FOREIGN KEY REFERENCES pandemics(id)
                NOT NULL, 

    p_name      VARCHAR(25) 
                NOT NULL,

    p_type      INTEGER 
                FOREIGN KEY REFERENCES policy_types(p_type) 
                NOT NULL
);

CREATE TABLE policy_history(
    policy_id       INTEGER 
                    FOREIGN KEY REFERENCES policies(policy_id)
                    NOT NULL,

    affected_area   FOREIGN KEY REFERENCES areas (area_id)
                    NOT NULL,

    date_start      DATE
                    NOT NULL,
    
    date_end        DATE, -- A null value means that the policy is ongoing
);

