CREATE TABLE IF NOT EXISTS novel_source(
    nv_src_id integer PRIMARY KEY,
    nv_id integer,
    src_id integer,
    FOREIGN KEY (nv_id) REFERENCES novel (nv_id),
    FOREIGN KEY (src_id) REFERENCES source (src_id)
);