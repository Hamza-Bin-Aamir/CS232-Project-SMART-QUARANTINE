CREATE TABLE economic_zone(
    e_zone          INTEGER 
                    PRIMARY KEY
                    NOT NULL,

    timing_start    TIME, -- A null value means the timing_start is at the start of day
    
    timing_end      TIME, -- A null value means the timing_end is at the end of day

    -- Both null means the timing lasts the whole day

    p_impact        DECIMAL(5,2)
                    NOT NULL,
);

CREATE TABLE economic_zone_adj(
    source              INTEGER
                        FOREIGN KEY REFERENCES economic_zone(e_zone)
                        NOT NULL,
    
    dest                INTEGER
                        FOREIGN KEY REFERENCES economic_zone(e_zone)
                        NOT NULL,
    
    adjacency_power     DECIMAL(5, 2)
                        NOT NULL
);

CREATE TABLE policy_type(
    p_type              SERIAL 
                        PRIMARY KEY 
                        NOT NULL,

    e_zone              INTEGER 
                        FOREIGN KEY REFERENCES economic_zone(e_zone) 
                        NOT NULL,

    time_frame_start    TIME, -- A null value means the time_frame_start is at the start of day

    time_frame_end      TIME, -- A null value means the time_frame_end is at the end of day
    
    -- Both null means the time frame lasts the whole day
);

CREATE TABLE policies(
    policy_id   SERIAL 
                PRIMARY KEY 
                NOT NULL,

    p_name      VARCHAR(25) 
                NOT NULL,

    p_type      INTEGER 
                FOREIGN KEY REFERENCES policy_types(p_type) 
                NOT NULL
);

CREATE TABLE policy_history(
    policy_id       INTEGER 
                    FOREIGN KEY REFERENCES policies(policy_id)
                    NOT NULL,

    affected_area   FOREIGN KEY REFERENCES locations(loc_id)
                    NOT NULL,

    date_start      DATE
                    NOT NULL,
    
    date_end        DATE, -- A null value means that the policy is ongoing
);