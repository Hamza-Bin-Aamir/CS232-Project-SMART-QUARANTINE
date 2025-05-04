-- ALWAYS ADD NEW AREAS ONE BY ONE

INSERT INTO econ_makeup
    (zone1, zone1_percentage, zone2, zone2_percentage, zone3, zone3_percentage, zone4, zone4_percentage)
VALUES
    ({{ZONE1, ZONE1P, ZONE2, ZONE2P, ZONE3, ZONE3P, ZONE4, ZONE4P}});

INSERT INTO areas
    (econ_makeup_id, zone_id, name)
VALUES
    (SELECT MAX(ref_id) FROM econ_makeup, {{ZONE_ID}}, {{NAME}})