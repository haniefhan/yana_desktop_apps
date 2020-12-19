from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

import sys
import os
import natsort
from operator import itemgetter
from datetime import datetime

# sys.path.append(".")


class BaseDB():
    def __init__(self, db_name):
        self.checkConnection(db_name)

    @classmethod
    def checkConnection(self, db_name):
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('yana.db')
        if not self.db.open():
            QMessageBox.critical(
                None, 'DB Connection Error',
                'Could not open database file: '
                f'{self.db.lastError().text()}')
            sys.exit(1)

    @classmethod
    def createTableIfNotExists(self):
        pass

    def _buildWhere(params):
        pass

    # VIEW / GET DATA

    @classmethod
    def checkIfDataExist(self, table, params):
        do = QSqlQuery()
        query = "SELECT * FROM {}".format(table)
        for i, key in enumerate(params, start=0):
            if i == 0:
                query += " WHERE "
            else:
                query += " AND "
            query += "{} = :{}".format(key, key)
        query += ";"

        do.prepare(query)
        for key in params:
            do.bindValue(':{}'.format(key), params[key])
        do.exec()

        if do.first() is False:
            # not exist
            return False
        else:
            # exist
            return True

    # parse DB result to one dict
    def parseResult(do):
        ret = {}
        while do.next():
            for i in range(0, do.record().count()):
                index = do.record().field(i).name()
                value = do.value(i)
                ret[index] = value
        return ret

    # parse DB result to list of dict
    def parseResults(do):
        ret = []
        while do.next():
            dt = {}
            for i in range(0, do.record().count()):
                index = do.record().field(i).name()
                value = do.value(i)
                dt[index] = value
            ret.append(dt)

        return ret

    @classmethod
    def getAll(self, table, orders):
        do = QSqlQuery()
        query = "SELECT * FROM {}".format(table)
        if len(orders) > 0:
            for i, key in enumerate(orders, start=0):
                if i == 0:
                    query += " ORDER BY "
                query += "{} {}".format(key, orders[key])
        query += ";"

        do.prepare(query)
        do.exec()

        return self.parseResults(do)

    @classmethod
    def getBy(self, table, params):
        do = QSqlQuery()
        query = "SELECT * FROM {}".format(table)
        for i, key in enumerate(params, start=0):
            if i == 0:
                query += " WHERE "
            else:
                query += " AND "
            query += "{} = :{}".format(key, key)
        query += " LIMIT 1;"

        do.prepare(query)
        for key in params:
            do.bindValue(':{}'.format(key), params[key])
        do.exec()

        return self.parseResult(do)

    @classmethod
    def getManyBy(self, table, params, orders):
        do = QSqlQuery()
        query = "SELECT * FROM {}".format(table)
        if len(params) > 0:
            for i, key in enumerate(params, start=0):
                if i == 0:
                    query += " WHERE "
                else:
                    query += " AND "
                query += "{} = :{}".format(key, key)
        query += ";"

    @classmethod
    def insert(self, table, params):
        do = QSqlQuery()
        fields = ""
        values = ""
        for i, key in enumerate(params, start=0):
            if i > 0:
                fields += ","
                values += ","
            fields += key
            values += f":{key}"

        query = "INSERT INTO {}".format(table)
        query += "("+fields+") VALUES "
        query += "("+values+");"

        do.prepare(query)
        for key in params:
            do.bindValue(f':{key}', params[key])
        do.exec()

        return do.lastInsertId()


class YanaDB(BaseDB):
    def __init__(self):
        super().__init__('yana.db')
        # self.checkConnection()

    def startUpInitialization(self):
        self.tableSource()
        self.tableNovel()
        self.tableNovelSource()
        self.tableVolume()
        self.tableChapter()

        self.insertSourceQuery()
        print(self.db.tables())

    def tableSource(self):
        query = """
        CREATE TABLE IF NOT EXISTS source(
            src_id integer PRIMARY KEY,
            src_name varchar(255) NULL,
            src_scrapper_name varchar(255) NULL,
            src_base_url varchar(255) NULL
        );
        """
        do = QSqlQuery()
        do.prepare(query)
        do.exec()

    def tableNovel(self):
        query = """
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
            nv_last_check datetime NULL
        );
        """
        do = QSqlQuery()
        do.prepare(query)
        do.exec()

    def tableNovelSource(self):
        query = """
        CREATE TABLE IF NOT EXISTS novel_source(
            nv_src_id integer PRIMARY KEY,
            nv_id integer,
            src_id integer,
            FOREIGN KEY (nv_id) REFERENCES novel (nv_id),
            FOREIGN KEY (src_id) REFERENCES source (src_id)
        );
        """
        do = QSqlQuery()
        do.prepare(query)
        do.exec()

    def tableVolume(self):
        query = """
        CREATE TABLE IF NOT EXISTS volume(
            volume_id integer PRIMARY KEY,
            volume_name varchar(255) NULL,
            nv_id integer NOT NULL,
            FOREIGN KEY (nv_id) REFERENCES novel (nv_id)
        );
        """
        do = QSqlQuery()
        do.prepare(query)
        do.exec()

    def tableChapter(self):
        query = """
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
            FOREIGN KEY (src_id) REFERENCES source (src_id),
            FOREIGN KEY (nv_id) REFERENCES novel (nv_id),
            FOREIGN KEY (volume_id) REFERENCES volume (volume_id)
        );
        """
        do = QSqlQuery()
        do.prepare(query)
        do.exec()

    # def insertSourceQuery(self):
    #     listdir = os.listdir("src/main/python/scrapper")
    #     for li in listdir:
    #         if ".py" in li:
    #             import scrapper.stabbingwithasyringe

    _sourceList = [
        {
            'src_name': 'Stabbing With Syringe',
            'src_scrapper_name': 'Stabbingwithasyringe',
            'src_base_url': 'https://stabbingwithasyringe.home.blog/'
        },
        {
            'src_name': 'Moonruneworks',
            'src_scrapper_name': 'Moonruneworks',
            'src_base_url': 'https://moonruneworks.com/'
        },
        {
            'src_name': 'Ero Light Novel Translations',
            'src_scrapper_name': 'Erolns',
            'src_base_url': 'http://erolns.blogspot.com/'
        },
    ]

    def insertSourceQuery(self):
        do = QSqlQuery()
        for source in self._sourceList:
            if not self.checkIfDataExist(
                "source", {"src_scrapper_name": source['src_scrapper_name']}
            ):
                self.insert(
                    "source",
                    {
                        "src_name": source['src_name'],
                        "src_scrapper_name": source['src_scrapper_name'],
                        "src_base_url": source['src_base_url'],
                    }
                )

    # SOURCE
    @classmethod
    def getSourceList(self):
        return self.getAll("source", {"src_name": "ASC"})

    @classmethod
    def getSourceId(self, src_name):
        query = """
        SELECT src_id FROM source
        WHERE src_name = :src_name
        """
        do = QSqlQuery()
        do.prepare(query)
        do.bindValue(':src_name', src_name)
        do.exec()

        if do.first() is True:
            return do.value(0)
        else:
            return 0

    @classmethod
    def getSource(self, src_id):
        # get data
        return self.getBy(
            "source", {"src_id": src_id}
        )

    # NOVEL
    @classmethod
    def getNovelInfo(self, nv_id):
        # get data
        return self.getBy(
            "novel", {"nv_id": nv_id}
        )

    @classmethod
    def getNovelList(self, src_id):
        query = """
        SELECT novel.nv_id, nv_title FROM novel
        LEFT JOIN novel_source ON novel.nv_id = novel_source.nv_id
        WHERE novel_source.src_id = :src_id
        ORDER BY nv_title ASC
        """
        do = QSqlQuery()
        do.prepare(query)
        do.bindValue(':src_id', src_id)
        do.exec()

        return self.parseResults(do)

    def setDefaultNovelData(data):
        arr = [
            'title', 'title_original', 'author', 'artist',
            'url', 'url_original', 'desc', 'image', 'image_original'
        ]
        for a in arr:
            if a not in data:
                data[a] = ''

        return data

    @classmethod
    def getChapterExistList(self, nv_id):
        query = """
        SELECT chp_no FROM chapter
        WHERE nv_id = :nv_id
        ORDER BY chp_no ASC
        """
        do = QSqlQuery()
        do.prepare(query)
        do.bindValue(':nv_id', nv_id)
        do.exec()

        ret = []
        while do.next():
            ret.append(do.value(0))
        return ret

    @classmethod
    def updateNovelList(self, data, src_id):
        # check if title exist
        exist = self.getBy(
            "novel", {"nv_title": data['title']}
        )

        if len(exist) > 0:
            nv_id = exist["nv_id"]
        else:
            # insert novel
            data = self.setDefaultNovelData(data)
            nv_id = self.insert(
                "novel",
                {
                    "nv_title": data['title'],
                    "nv_title_original": data['title_original'],
                    "nv_author": data['author'],
                    "nv_artist": data['artist'],
                    "nv_url": data['url'],
                    "nv_url_original": data['url_original'],
                    "nv_desc": data['desc'],
                    "nv_image_url_original": data['image'],
                    "nv_total_chapter": len(data['chapters']),
                    "nv_last_chapter": data['chapters'][-1]['title'],
                    "nv_last_update": datetime.now().strftime(
                        "%Y-%m-%d %H:%I:%S"),
                    "nv_last_check": datetime.now().strftime(
                        "%Y-%m-%d %H:%I:%S"),
                }
            )

        # check if in novel_source
        if not self.checkIfDataExist(
            "novel_source", {"src_id": src_id, "nv_id": nv_id}
        ):
            # insert novel_source
            self.insert(
                "novel_source",
                {
                    "src_id": src_id,
                    "nv_id": nv_id,
                }
            )

        chapter_exist = self.getChapterExistList(nv_id)

        # insert chapter
        for chapter in data['chapters']:
            # check first if chapter exist
            # if not self.checkIfDataExist(
            #     "chapter", {"chp_no": chapter['no'], "nv_id": nv_id}
            # ):
            if str(chapter['no']) not in chapter_exist:
                # check if volume exist
                exist = self.getBy(
                    "volume",
                    {
                        "volume_name": chapter['volume'],
                        "nv_id": nv_id,
                    }
                )

                if len(exist) > 0:
                    volume_id = exist["volume_id"]
                else:
                    # insert volume
                    volume_id = self.insert(
                        "volume",
                        {
                            "volume_name": chapter['volume'],
                            "nv_id": nv_id,
                        }
                    )

                if 'date' not in chapter:
                    chapter['date'] = datetime.now().strftime(
                        "%Y-%m-%d %H:%I:%S")

                # insert chapter
                self.insert(
                    "chapter",
                    {
                        "chp_title": chapter['title'],
                        "chp_no": chapter['no'],
                        "chp_url": chapter['url'],
                        "chp_date": chapter['date'],
                        "src_id": src_id,
                        "nv_id": nv_id,
                        "volume_id": volume_id,
                    }
                )

    @classmethod
    def getChapter(self, chp_id):
        return self.getBy(
            "chapter", {"chp_id": chp_id}
        )

    @classmethod
    def getChapterList(self, nv_id):
        # info = self.getNovelInfo(nv_title)

        do = QSqlQuery()
        query = """
        SELECT * FROM chapter
        LEFT JOIN volume ON chapter.volume_id = volume.volume_id
        WHERE chapter.nv_id = :nv_id
        ORDER BY chapter.chp_no ASC
        """

        do = QSqlQuery()
        do.prepare(query)
        do.bindValue(':nv_id', nv_id)
        do.exec()
        result = self.parseResults(do)

        result = natsort.natsorted(result, key=itemgetter(*['chp_no']))
        return result

    @classmethod
    def getUrlChapter(self, chp_id):
        do = QSqlQuery()
        query = """
        SELECT * FROM chapter
        WHERE chp_id = :chp_id
        """

        do = QSqlQuery()
        do.prepare(query)
        do.bindValue(':chp_id', chp_id)
        do.exec()

        data = self.parseResult(do)
        return data['chp_url']
