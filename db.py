import logging
import sqlite3
import config
import os
import db_scheme
import pdb
import time
from datetime import datetime

logger = logging.getLogger("FluidSegAPI.Db")
logger.setLevel("WARNING")

class FluidDb:
    def __init__(self):
        try:
            # os.remove(config.DB_PATH)
            pass
        except:
            pass
            
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
        self.conn.execute(db_scheme.idx_sess_sessKey)
        logger.info("Index created")
        self.conn.commit()

    def check_table_exists(self, tblname):
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM sqlite_master WHERE name=?", (tblname,))
        ret = cur.fetchone()
        return ret != None
    
    def commit_change(self):
        self.conn.commit()
    
    def get_statistics(self):        
        try:
            cur = self.conn.execute("SELECT COUNT(*) FROM tbl_field")
            field_count = cur.fetchone()[0]
            cur = self.conn.execute("SELECT COUNT(*) FROM tbl_tag")
            tag_count = cur.fetchone()[0]
            cur = self.conn.execute("SELECT COUNT(*) FROM tbl_lus")
            lu_count = cur.fetchone()[0]
        except Exception as ex:
            logger.error(ex)
            field_count = -1
            tag_count = -1
            lu_count = -1

        return {"nLU": lu_count, "nField": field_count, "nTag": tag_count}
        
        
    def get_lus(self):
        cur = self.conn.execute("SELECT lus FROM tbl_lus")        
        lus_list = [x[0] for x in cur.fetchall()]
        return lus_list

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

            cur = self.conn.execute(
                "SELECT lus_id, lus FROM tbl_lus WHERE lus IN (%s)" % lusStr)
            results = cur.fetchall()
            if not results:
                raise ValueError("lus not found") 

            lus_map = {lus_id: lus for lus_id, lus in results}
            lus_id = [str(x) for x in lus_map.keys()]
            lus_id_list = ",".join(lus_id)
            
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
    
    def get_session_info(self, sess_key):
        """ get Session info

            Parameters
            ----------
            sess_key: Session Key

            Return
            ------
            ret_data = {
                "sess_id": sess_id,
                "timestamp": timestamp,
                "doc_id": doc_id,
                "userName": userName, 
                "text": doc_text
            } or {} when error
        """
        try:
            cur = self.conn.execute(
                "SELECT sess_id, timestamp, doc_id, userName FROM tbl_sess " + 
                "WHERE sess_key = ?", (sess_key,))
            sess_data = cur.fetchone()
            if not sess_data:                            
                raise ValueError("invalid sess_id")            

            sess_id = sess_data[0]
            timestamp = sess_data[1]
            doc_id = sess_data[2]
            userName = sess_data[3]
            cur = self.conn.execute(
                "SELECT doc_text FROM tbl_doc WHERE doc_id = ?", (doc_id,)
            )

            doc_text = cur.fetchone()
            if doc_text:
                doc_text = doc_text[0]
            else:
                raise ValueError("invalid doc_id")

            ret_data = {
                "sess_id": sess_id,
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

    def get_annotation(self, sess_id):
        try:            
            cur = self.conn.execute(
                "SELECT segments FROM tbl_seg " + 
                "WHERE sess_id = ?" + 
                "ORDER BY seg_id DESC LIMIT 1", (sess_id,))
            segs = cur.fetchone()
            if not segs:
                segs = []
            else:                
                segs = self.str2seg(segs[0])

            cur = self.conn.execute(
                "SELECT lus, field, tagvalue, ranges FROM tbl_tag " + 
                "LEFT JOIN tbl_field ON tbl_tag.field_id = tbl_field.field_id " + 
                "LEFT JOIN tbl_lus ON tbl_tag.lus_id = tbl_lus.lus_id "
                "WHERE sess_id = ?", (sess_id,))
            tag_data = []
            for tag_rec in cur.fetchall():
                lus = tag_rec[0]
                field = tag_rec[1]
                tagvalue = tag_rec[2]
                ranges = tag_rec[3]
                tag_inst = {
                    "lus": lus.split("/"),
                    "ranges": self.str2seg(ranges),
                    "tagField": field,
                    "tagValue": tagvalue
                }
                tag_data.append(tag_inst)
            return { "segments": segs, "tags": tag_data }

        except Exception as ex:
            logger.error(ex)
            return []
        
    def save_session(self, sess_item):
        """ Save session data

        Parameters
        ----------
        sess_item: Dict
                   {
                       "doc_id": doc_id,
                       "sess_key": session key
                       "userName": userName 
                   }
        """
        cur = self.conn.cursor()
        timestamp = time.mktime(datetime.now().timetuple())
        timestamp = int(timestamp)
        cur.execute("INSERT OR IGNORE INTO tbl_sess VALUES (?,?,?,?,?)", (
            None,
            timestamp,
            sess_item["sess_key"],
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
        
    def save_tag(self, lex_item, sess_id=None):
        """ Save tag data into databse
        This method does not auto commit, call db.commit_change manually!!

        Parameters
        ----------
        lex_item: LexDataItem
            LexDataItem:: {
                "lu": "<lu>"
                "data": Dict[TagField, TagValue]
            } or
            LexRangedDataItem:: {
                lu: "<lu>"
                range: [chstart, chend],
                tagField: "<tagField>",
                tagValue: "<tagValue>"                
            }
        """

        # tag_data_list = {lu: "...", "data": [...]}
        cur = self.conn.cursor()

        
        # accommodate lex_item format        
        lus = (lex_item["lus"],)

        if "ranges" in lex_item:            
            # lex_item is a LexRangedDataItem
            tagField_x = lex_item.get("tagField", "unknown")
            tagValue_x = lex_item.get("tagValue", "")
            tags = {tagField_x: tagValue_x}
            fields = [(tagField_x,)]            
            rangesStr = self.seg2str([lex_item["ranges"]])            
        else:
            if "lus" not in lex_item or "data" not in lex_item:
                logger.warning("invalid tag_data attempt to save")
            # lex_item is a LexDataItem    
            tags = lex_item["data"]
            fields = [(x,) for x in tags.keys()]
            rangesStr = ""
                
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
                sess_id,   # sess_id
                lus_id, # lus_id
                field_map[tag_field], #field_id,                
                tag_value, # tagvalue
                rangesStr, # ranges
                ))
        
        # pdb.set_trace()                    
        cur.executemany("INSERT INTO tbl_tag VALUES (?,?,?,?,?,?)",
            ins_data_list)
        logger.info("tbl_tag INSERT affect %d rows", cur.rowcount)        

    def str2seg(self, segStr):
        segList = []
        segTokens = segStr.split(",")
        # pdb.set_trace()
        for seg_tok in segTokens:
            segments = seg_tok.split("/")
            seg_tok = [x.split("-") for x in segments]
            segList.append(seg_tok)
        return segList

    def seg2str(self, seg_list):              
        strbuf = []
        for seg_x in seg_list:            
            str_x = ["%d-%d" % (x[0],x[1]) for x in seg_x]
            str_x = "/".join(str_x)            
            strbuf.append(str_x)
        segStr = ",".join(strbuf)        
        return segStr

