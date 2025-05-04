SELECT ph.policy_id, p.p_name, p.pandemic_id, a.name AS area_name, 
       ps.infection_rate, ps.cure_rate, ps.death_rate, ph.date_start, ph.date_end
FROM policy_history ph
JOIN policies p ON ph.policy_id = p.policy_id
JOIN areas a ON ph.affected_area = a.id
JOIN pandemic_stats ps ON p.pandemic_id = ps.pandemic_id AND ps.area_id = a.id
ORDER BY ph.policy_id, ph.date_start;