-- Insert sample areas
INSERT INTO areas (econ_makeup_id, zone_id, name) VALUES
  (1, 1, 'France'),
  (1, 2, 'England'),
  (2, 3, 'Germany'),
  (2, 4, 'Istanbul');

-- Insert sample area adjacency with adjacency power
INSERT INTO area_adj (src, dest, adj_power) VALUES
  (5, 6, 0.8),
  (6, 7, 0.6);

-- Insert sample pandemic stats (latest date per area for COVID-19)
INSERT INTO pandemic_stats (pandemic_id, area_id, stat_date, total_population, infected, infection_rate, cured, cure_rate, deaths, death_rate) VALUES
  (3, 5, '1700-05-01', 100000, 5000, 0.05, 4500, 0.9, 200, 0.04),
  (3, 6, '1700-05-01', 80000, 3000, 0.0375, 2800, 0.93, 100, 0.033),
  (3, 7, '1700-05-01', 120000, 7000, 0.058, 6500, 0.93, 300, 0.043),
  (3, 8, '1700-05-01', 90000, 4000, 0.044, 3700, 0.925, 150, 0.038);