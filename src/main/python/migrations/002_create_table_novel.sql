CREATE TABLE IF NOT EXISTS novel(
    nv_id integer PRIMARY KEY,
    nv_title varchar(255) NULL,
    nv_title_original varchar(255) NULL,
    nv_author varchar(255) NULL,
    nv_artist varchar(255) NULL,
    nv_url varchar(255) NULL,
    nv_url_original varchar(255) NULL,
    nv_desc text NULL,
    nv_image_url varchar(255) NULL,
    nv_image_url_original varchar(255) NULL,
    nv_total_chapter varchar(255) NULL,
    nv_last_chapter varchar(255) NULL,
    nv_last_update datetime NULL,
    nv_last_check datetime NULL,
    nv_read integer NULL DEFAULT 0,
    nv_new_chapter integer NULL DEFAULT 0
);