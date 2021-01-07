CREATE TABLE IF NOT EXISTS volume(
    volume_id integer PRIMARY KEY,
    volume_name varchar(255) NULL,
    nv_id integer NOT NULL,
    FOREIGN KEY (nv_id) REFERENCES novel (nv_id)
);