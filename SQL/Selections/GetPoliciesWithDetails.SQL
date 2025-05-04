SELECT p.policy_id, p.p_name, p.pandemic_id, pt.e_zone, pt.time_frame_start, pt.time_frame_end
FROM policies p
JOIN policy_type pt ON p.p_type = pt.p_type
ORDER BY p.policy_id;