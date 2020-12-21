CREATE TABLE IF NOT EXISTS source(
    src_id integer PRIMARY KEY,
    src_name varchar(255) NULL,
    src_scrapper_name varchar(255) NULL,
    src_base_url varchar(255) NULL
);