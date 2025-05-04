SELECT a.id, a.name, em.zone1, em.zone1_percentage, em.zone2, em.zone2_percentage,
       em.zone3, em.zone3_percentage, em.zone4, em.zone4_percentage
FROM areas a
JOIN econ_makeup em ON a.econ_makeup_id = em.ref_id
ORDER BY a.name;