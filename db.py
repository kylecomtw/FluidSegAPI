import sqlite3
import config
import os

class FluidDb:
    def __init__(self):
        if os.path.exists(config.DB_PATH):
            os.remove(config.DB_PATH)
        self.conn = sqlite3.connect(config.DB_PATH)
        self.check_table_exists("table")
        self.create_datatables()
        
    def create_datatables(self):
        tbl_scheme = """
            CREATE TABLE tbl_tag (
                serial INT PRIMARY KEY,
                lu TEXT,
                tag TEXT,
                sess_id TEXT,
                range_start INT,
                range_end INT
            );
        """
        idx_scheme = """
            CREATE INDEX idx_tag_sess ON tbl_tag(sess_id);
        """
        self.conn.execute(tbl_scheme)
        self.conn.execute(idx_scheme)
        self.conn.commit()

    def check_table_exists(self, tbname):
        pass
