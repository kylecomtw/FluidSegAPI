
tbl_tag = """
    CREATE TABLE tbl_tag (
        tag_id INT PRIMARY KEY,
        lus TEXT,
        tag TEXT,
        sess_id TEXT,
        ranges TEXT
    );
"""

tbl_seg = """
    CREATE TABLE tbl_seg (
        seg_id INT PRIMARY KEY,
        sess_id TEXT,
        segments TEXT
    );
"""

tbl_sess = """
    CREATE TABLE tbl_sess (
        sess_id INT PRIMARY KEY,
        timestamp INT,
        doc_id INT,
        user_id INT
    );
"""

idx_tag_sess = "CREATE INDEX idx_tag_sess ON tbl_tag(sess_id);"
idx_tag_lu = "CREATE INDEX idx_tag_lu ON tbl_tag(lu);"
idx_tag_tag = "CREATE INDEX idx_tag_tag ON tbl_tag(tag);"
idx_seg_sess = "CREATE INDEX idx_seg_sess ON tbl_seg(sess_id);"
idx_sess_docid = "CREATE INDEX idx_sess_docid ON tbl_sess(doc_id);"


