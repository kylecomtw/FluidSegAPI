import logging
import sqlite3
import config
import os
import db_scheme
import pdb
import time
from datetime import datetime

logger = logging.getLogger("FluidSeg.Db")
logger.setLevel("WARNING")

class FluidDb:
    def __init__(self):
        # os.remove(config.DB_PATH)
        self.conn = sqlite3.connect(config.DB_PATH)
        if not self.check_table_exists("tbl_sess"):
            self.create_datatables()
        
    def create_datatables(self):
        self.conn.execute(db_scheme.tbl_lus)
        self.conn.execute(db_scheme.tbl_field)        
        self.conn.execute(db_scheme.tbl_tag)
        self.conn.execute(db_scheme.tbl_seg)
        self.conn.execute(db_scheme.tbl_sess)        
        self.conn.execute(db_scheme.tbl_doc)
        logger.info("Table created")
        self.conn.execute(db_scheme.idx_lus_lus)
        self.conn.execute(db_scheme.idx_field_field)
        self.conn.execute(db_scheme.idx_tag_sess)
        self.conn.execute(db_scheme.idx_tag_lu)
        self.conn.execute(db_scheme.idx_tag_tag)
        self.conn.execute(db_scheme.idx_seg_sess)
        self.conn.execute(db_scheme.idx_sess_docid)
        logger.info("Index created")
        self.conn.commit()

    def check_table_exists(self, tblname):
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM sqlite_master WHERE name=?", (tblname,))
        ret = cur.fetchone()
        return ret != None
    
    def commit_change(self):
        self.conn.commit()
    
    def get_lu_info(self, lus):
        """ Get lexical unit tagging history
        
        Parameters
        ----------
            lus: List[Str]
                 list of lu to query
        Return
        -------
        ret_data: Dict[lus, tagData]
            tagData:: Dict[tagfield, tagInstance]
            tagInstance:: Dict[tagvalue, tagLocations]
            tagLocations: List[Tuple[sess_id, ranges]]
        """

        try:
            lus_list = ["'%s'" % x for x in lus]
            lusStr = ",".join(lus_list)

            cur = self.conn.execute("SELECT lus_id, lus FROM tbl_lus WHERE lus IN (%s)" % lusStr)
            results = cur.fetchall()
            if not results:
                raise ValueError("lus not found") 

            lus_map = {lus_id: lus for lus_id, lus in results}
            lus_id = [str(x) for x in lus_map.keys()]
            lus_id_list = ",".join(lus_id)
            pdb.set_trace()
            cur = self.conn.execute(
                "SELECT lus_id, field, tagvalue, sess_id, ranges FROM tbl_tag " + 
                "LEFT JOIN tbl_field ON tbl_tag.field_id = tbl_field.field_id " + 
                "WHERE tbl_tag.lus_id IN (%s)" % lus_id_list)
            
            ret_data = {}
            for data in cur.fetchall():                
                lus = lus_map.get(data[0], "")
                tagfield = data[1]
                tagvalue = data[2]
                sess_id = data[3]
                ranges = data[4]

                lus_data = ret_data.get(lus, {})
                tag_data = lus_data.get(tagfield, {})
                tag_value_data = tag_data.get(tagvalue, [])
                if sess_id and ranges:                    
                    tag_value_data.append((sess_id, ranges))                
                tag_data[tagvalue] = tag_value_data
                lus_data[tagfield] = tag_data
                ret_data[lus] = lus_data

        except Exception as ex:
            logger.error(ex)
            ret_data = {}        
        
        return ret_data
    
    def get_session_info(self, sess_id):
        try:
            cur = self.conn.execute(
                "SELECT timestamp, doc_id, userName FROM tbl_sess " + 
                "WHERE sess_id = ?", (sess_id,))
            sess_data = cur.fetchone()
            if not sess_data:                            
                raise ValueError("invalid sess_id")            

            timestamp = sess_data[0]
            doc_id = sess_data[1]
            userName = sess_data[2]
            cur = self.conn.execute(
                "SELECT doc_text FROM tbl_doc WHERE doc_id = ?", (doc_id,)
            )

            doc_text = cur.fetchone()
            if doc_text:
                doc_text = doc_text[0]
            else:
                raise ValueError("invalid doc_id")                    
            ret_data = {
                "timestamp": timestamp,
                "doc_id": doc_id,
                "userName": userName, 
                "text": doc_text
            }
        except Exception as ex:
            logger.error(ex)
            ret_data = {}    

        return ret_data

    def get_segment_info(self, sess_id):
        try:
            cur = self.conn.execute(
                "SELECT doc_text, segments FROM tbl_seg " + 
                "LEFT JOIN tbl_doc ON tbl_seg.doc_id = tbl_doc.doc_id "
                "WHERE sess_id = ?", (sess_id,))
            seg_data = cur.fetchone()            
            if not seg_data:                
                raise ValueError("invalid sess_id")            

            doc_text = seg_data[0]
            segments = self.str2seg(seg_data[1])
                                       
            ret_data = {
                "doc_text": doc_text,
                "segments": segments,                
            }

        except Exception as ex:
            logger.error(ex)
            ret_data = {}    

        return ret_data

    def get_document_text(self, doc_id):
        cur = self.conn.execute(
            "SELECT doc_text FROM tbl_doc WHERE doc_id=?", (doc_id,))
        doctext = cur.fetchone()
        doctext = doctext[0] if doctext else ""
        return doctext    

    def save_session(self, sess_item):
        """ Save session data

        Parameters
        ----------
        sess_item: Dict
                   {
                       "doc_id": doc_id,
                       "userName": userName 
                   }
        """
        cur = self.conn.cursor()
        timestamp = time.mktime(datetime.now().timetuple())
        timestamp = int(timestamp)
        cur.execute("INSERT INTO tbl_sess VALUES (?,?,?,?)", (
            None,
            timestamp,
            sess_item["doc_id"],
            sess_item["userName"]
        ))
        self.commit_change()
        return cur.lastrowid

    def save_seg(self, seg_data):
        """ Save segmentation data
        
        Parameters
        seg_data: Dict
                  {
                      "doc_id": doc_id,
                      "sess_id": sess_id,
                      "segments": List[Ranges]
                                  Ranges: (chstart, chend)
                  }
        """
        cur = self.conn.cursor()
        segStr = self.seg2str(seg_data["segments"])
        cur.execute("INSERT INTO tbl_seg VALUES (?,?,?,?)", (
            None,
            seg_data["doc_id"],
            seg_data["sess_id"],
            segStr
        ))
        self.commit_change()
        return cur.lastrowid
    
    def save_doc(self, doc_data):
        """save document to database

        Parameters
        ----------
        doc_data: Dict
                  {"text": <doc_text>}
        """

        cur = self.conn.cursor()        
        cur.execute("INSERT INTO tbl_doc VALUES (?,?)", (
            None,
            doc_data["text"]        
        ))

        self.commit_change()
        return cur.lastrowid
        
    def save_tag(self, lex_item):
        # tag_data_list = {lu: "...", "data": [...]}
        cur = self.conn.cursor()
        if "lu" not in lex_item or "data" not in lex_item:
            logger.warning("invalid tag_data attempt to save")
        
        lus = (lex_item["lu"],)
        tags = lex_item["data"]
        fields = [(x,) for x in tags.keys()]
        
        cur.execute("INSERT OR IGNORE INTO tbl_lus (lus) VALUES (?)", lus)               
        cur.execute("SELECT lus_id FROM tbl_lus WHERE lus = ?", lus)
        lus_id = cur.fetchone()[0]

        logger.info("lu rowid: %d", lus_id)
        
        cur.executemany("INSERT OR IGNORE INTO tbl_field (field) VALUES (?)", fields)
        logger.info("tbl_field INSERT affected %d row(s)", cur.rowcount)
        
        fields_str = ",".join(["'%s'" % (x,) for x in tags.keys()])
        cmd = "SELECT * FROM tbl_field WHERE field IN (%s)" % fields_str
        cur.execute(cmd)
        field_map = {field: field_id for field_id, field in cur.fetchall()}
    
        ins_data_list = []
        for tag_field, tag_value in tags.items():
            ins_data_list.append((
                None, # tag_id
                None,   # sess_id
                lus_id, # lus_id
                field_map[tag_field], #field_id,                
                tag_value, # tagvalue
                None, # ranges
                ))
        
        # pdb.set_trace()                    
        cur.executemany("INSERT INTO tbl_tag VALUES (?,?,?,?,?,?)",
            ins_data_list)
        logger.info("tbl_tag INSERT affect %d rows", cur.rowcount)        

    def str2seg(self, segStr):
        segList = segStr.split(",")
        segList = [tuple(x.split('-')) for x in segList]
        return segList

    def seg2str(self, seg_list):
        """ seg_list: List[Tuple[chstart, chend]]
        """
        segStr = ["%d-%d" % (x[0],x[1]) for x in seg_list]
        segStr = ",".join(segStr)
        return segStr

