INSERT INTO pandemics 
    (p_name, date_start, descriptiontxt) -- We assume the pandemic is ongoing
VALUES
    ({{PANDEMIC_NAME}}, {{DATE_START}}, {{DESCRIPTION}})