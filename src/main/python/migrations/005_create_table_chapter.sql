CREATE TABLE IF NOT EXISTS chapter(
    chp_id integer PRIMARY KEY,
    chp_title varchar(255) NULL,
    chp_no varchar(255) NULL,
    chp_url varchar(255) NULL,
    chp_date datetime NULL,
    -- chp_volume varchar(255) NULL,
    src_id integer NOT NULL,
    nv_id integer NOT NULL,
    volume_id integer NULL,
    chp_read integer NULL DEFAULT 0,
    chp_new integer NULL DEFAULT 0,
    FOREIGN KEY (src_id) REFERENCES source (src_id),
    FOREIGN KEY (nv_id) REFERENCES novel (nv_id),
    FOREIGN KEY (volume_id) REFERENCES volume (volume_id)
);