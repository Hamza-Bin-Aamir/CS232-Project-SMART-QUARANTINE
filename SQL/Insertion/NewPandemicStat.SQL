INSERT INTO pandemic_stats
(pandemic_id, area_id, stat_date, total_population, infected, infection_rate, cured, cure_rate, deaths, death_rate)
VALUES
({{PID}}, {{AID}}, {{SDATE}}, {{TPOP}}, {{INF}}, {{INF_RATE}}, {{CURED}}, {{CURE_RATE}}, {{DEATHS}}, {{DEATH_RATE}})