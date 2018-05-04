tbl_lus = """
    CREATE TABLE tbl_lus (
        lus_id INTEGER PRIMARY KEY AUTOINCREMENT,
        lus TEXT UNIQUE
    )
"""

tbl_field = """
    CREATE TABLE tbl_field (
        field_id INTEGER PRIMARY KEY AUTOINCREMENT,
        field TEXT UNIQUE
    )
"""

tbl_tag = """
    CREATE TABLE tbl_tag (
        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sess_id INT,
        lus_id INT,        
        field_id INT,        
        tagvalue TEXT,        
        ranges TEXT,
        FOREIGN KEY(lus_id) REFERENCES tbl_lus(lus_id),
        FOREIGN KEY(sess_id) REFERENCES tbl_lus(lus_id),
        FOREIGN KEY(field_id) REFERENCES tbl_field(field_id)
    );
"""

tbl_doc = """
    CREATE TABLE tbl_doc (
        doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_text TEXT
    )
"""

tbl_sess = """
    CREATE TABLE tbl_sess (
        sess_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        sess_key TEXT UNIQUE,
        doc_id INT,
        userName TEXT
    );
"""

tbl_seg = """
    CREATE TABLE tbl_seg (
        seg_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER,
        sess_id INTEGER,
        segments TEXT,
        FOREIGN KEY(doc_id) REFERENCES tbl_doc(doc_id),
        FOREIGN KEY(sess_id) REFERENCES tbl_sess(sess_id)
    );
"""

idx_lus_lus = "CREATE INDEX idx_lus_lus ON tbl_lus(lus);"
idx_field_field = "CREATE INDEX idx_field_field ON tbl_field(field);"
idx_tag_sess = "CREATE INDEX idx_tag_sess ON tbl_tag(sess_id);"
idx_tag_lu = "CREATE INDEX idx_tag_lu ON tbl_tag(lus_id);"
idx_tag_tag = "CREATE INDEX idx_tag_tag ON tbl_tag(field_id);"
idx_seg_sess = "CREATE INDEX idx_seg_sess ON tbl_seg(sess_id);"
idx_sess_sessKey = "CREATE INDEX idx_sess_sessKey ON tbl_sess(sess_key);"


