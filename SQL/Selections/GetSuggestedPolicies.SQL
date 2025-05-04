SELECT p.policy_id, p.p_name
FROM policies p
JOIN policy_type pt ON p.p_type = pt.p_type
WHERE pt.e_zone = ANY(ARRAY[{{ECONOMIC_ZONES_IDS}}]);