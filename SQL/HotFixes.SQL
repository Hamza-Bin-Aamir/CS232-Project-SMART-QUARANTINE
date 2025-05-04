-- Make the ezone a SERIAL 
CREATE SEQUENCE ezone_seq;

ALTER TABLE economic_zone
ALTER COLUMN e_zone SET DEFAULT nextval('ezone_seq');