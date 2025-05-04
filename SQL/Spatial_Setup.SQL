-- Spatial tables
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    name TEXT,
);
CREATE TABLE econ_makeup(
    ref_id              SERIAL PRIMARY KEY NOT NULL,
    zone1               INTEGER FOREIGN KEY REFERENCES economic_zone(e_zone),
    zone1_percentage    DECIMAL(5, 2),
    zone2               INTEGER FOREIGN KEY REFERENCES economic_zone(e_zone),
    zone2_percentage    DECIMAL(5, 2),
    zone3               INTEGER FOREIGN KEY REFERENCES economic_zone(e_zone),
    zone3_percentage    DECIMAL(5, 2),
    zone4               INTEGER FOREIGN KEY REFERENCES economic_zone(e_zone),
    zone4_percentage    DECIMAL(5, 2)
);
CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    econ_makeup_id INTEGER FOREIGN KEY REFERENCES econ_makeup(ref_id),  
    zone_id INTEGER REFERENCES zones(id),
    name TEXT,
);
CREATE TABLE area_adj (
    source      INTEGER FOREIGN KEY REFERENCES areas(id),
    dest        INTEGER FOREIGN KEY REFERENCES areas(id),
    adj_power   DECIMAL (5, 2)
);