from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QMessageBox, QComboBox,
    QListWidget, QListWidgetItem, QTextEdit, QProgressBar,
    QLineEdit
)
# from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtGui import (
    QPixmap, QImage, QStandardItemModel, QStandardItem, QTextCursor,
    QTextDocument
)

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

import sys
import requests
import math

sys.path.append(".")
from yanadb import YanaDB

YanaDB = YanaDB()

# import all source from DB and folder "scrapper"
mods = []
sources = YanaDB.getAll("source", {"src_name": "ASC"})
for src in sources:
    try:
        exec(
            "from scrapper."
            + src['src_scrapper_name'].lower()
            + " import "
            + src['src_scrapper_name'])
    except ModuleNotFoundError:
        print("scrapper module not found!")
        print(src)
        pass
    # ex :
    # from shintranslations import Shintranslations


def NovelSwitcher(src_name):
    try:
        item = next(item for item in sources if item["src_name"] == src_name)
        try:
            return eval(item['src_scrapper_name'])
        except NameError:
            return None
    except StopIteration:
        return None

    # top same as below
    # if src_name == "Stabbing With Syringe":
    #     return Stabbingwithasyringe()
    # elif src_name == "Moonruneworks":
    #     return Moonruneworks()
    # elif src_name == "Ero Light Novel Translations":
    #     return Erolns()
    # elif src_name == "Shin Translations":
    #     return Shintranslations()
    # else:
    #     return None


class YanaRead(QMainWindow):
    def __init__(self, yana=None):
        super(YanaRead, self).__init__(yana)
        self.resize(870, 600)
        self.yana = yana
        self.setReadArea()

    def setReadArea(self):
        self.labelnovel = QLabel(self)
        self.labelnovel.setText("Chapter List (Double Click to show chapter)")
        self.labelnovel.adjustSize()
        self.labelnovel.move(10, 10)

        self.chapterList = QListWidget(self)
        self.chapterList.move(10, 30)
        self.chapterList.resize(200, self.height() - 40)
        self.chapterList.itemDoubleClicked.connect(self.setContent)

        self.readArea = QWebEngineView(self)
        self.readArea.move(220, 30)
        self.readArea.resize(self.width() - 225, self.height() - 70)
        self.readArea.setAttribute(Qt.WA_StyledBackground)
        self.readArea.setStyleSheet("border: 1px solid #999;")
        self.readArea.setContentsMargins(1, 1, 1, 1)

        self.chapterLabel = QLabel(self)
        self.chapterLabel.move(220, self.height() - 35)
        self.chapterLabel.resize(220, 25)

        self.prevButton = QPushButton(self)
        self.prevButton.setText("< Prev Chapter")
        self.prevButton.move(450, self.height() - 35)
        self.prevButton.resize(100, 25)
        self.prevButton.clicked.connect(self.prevChapter)

        self.nextButton = QPushButton(self)
        self.nextButton.setText("Next Chapter >")
        self.nextButton.move(557, self.height() - 35)
        self.nextButton.resize(100, 25)
        self.nextButton.clicked.connect(self.nextChapter)

    def read(self, src_id, chp_id):
        src = YanaDB.getSource(src_id)

        self.novel = NovelSwitcher(src['src_name'])

        if self.novel is not None:
            chp = YanaDB.getChapter(chp_id)
            nv_id = chp['nv_id']

            self.setChapterList(nv_id, chp_id)

            self.setContent()

            return True
        else:
            QMessageBox.critical(
                None, 'Scrapper Error',
                'Novel Scrapper did not exist!')
            return False

    def setChapterList(self, nv_id, chp_id=None):
        self.chapterList.clear()
        groupName = ""
        for chp in YanaDB.getChapterList(nv_id):
            if chp['volume_name'] != groupName:
                # self.chapterList.addItem(chp['volume_name'])
                item = QListWidgetItem(chp['volume_name'])
                item.setData(3, chp['volume_name'])
                item.setData(33, 'chapter_header')
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                self.chapterList.addItem(item)
                groupName = chp['volume_name']
            # self.chapterList.addItem(" - " + chp['chp_title'])
            item = QListWidgetItem(" - " + chp['chp_title'])
            item.setData(3, chp['chp_title'])
            item.setData(33, 'chapter')
            item.setData(34, chp['chp_id'])
            item.setData(35, chp['src_id'])
            self.chapterList.addItem(item)

            if chp['chp_id'] == chp_id:
                self.chapterList.setCurrentItem(item)

    def setContent(self):
        if self.chapterList.currentItem().data(33) == "chapter":
            chp_id = self.chapterList.currentItem().data(34)

            # url = YanaDB.getUrlChapter(chp_id)
            chp = YanaDB.getChapter(chp_id)
            url = chp["chp_url"]
            content = self.novel.getContent(url)

            self.chapterLabel.setText(chp["chp_title"])
            self.readArea.setHtml(content)

    def prevChapter(self):
        current = self.chapterList.currentRow()
        pr = current - 1
        if pr > 0:
            self.chapterList.setCurrentRow(pr)
            self.setContent()
        else:
            QMessageBox.information(
                None, 'Previous Chapter',
                'This is first chapter!')

    def nextChapter(self):
        current = self.chapterList.currentRow()
        nx = current + 1
        if nx < self.chapterList.count():
            self.chapterList.setCurrentRow(nx)
            self.setContent()
        else:
            QMessageBox.information(
                None, 'Next Chapter',
                'This is last chapter!')



class UpdateThread(QThread):
    _max_progress = 100
    update_progress = pyqtSignal(int)
    update_progress_label = pyqtSignal(str)
    update_novel = pyqtSignal(dict)
    update_complete = pyqtSignal(int)
    update_failed = pyqtSignal(str)

    def __init__(self, src_text):
        super(UpdateThread, self).__init__()
        self.src_text = src_text

    def run(self):
        progress = 0
        self.update_progress.emit(progress)

        novel = NovelSwitcher(self.src_text)

        if novel is not None:
            self.update_progress_label.emit('Get novel data in source...')

            ls = novel.getList()
            div = len(ls)
            if div == 0:
                div = 1

            progress_add = math.ceil(100 / div)

            for nv in ls:
                # get chapters
                self.update_progress_label.emit(
                    'Get novel "' + nv['title'] + '" data...')

                nv['chapters'] = novel.getChapters(nv['url'])

                self.update_progress_label.emit(
                    'Update novel "' + nv['title'] + '" data...')

                self.update_novel.emit(nv)

                # set the progress bar
                progress += progress_add
                if(progress > self._max_progress):
                    progress = self._max_progress
                self.update_progress.emit(progress)

            self.update_progress_label.emit(
                'Update Novel List finished!')
            self.update_complete.emit(len(ls))
        else:
            self.update_failed.emit('Novel Scrapper did not exist!')


class Yana(QMainWindow):

    _book_cover_def = "assets/image/book-default.png"

    def __init__(self):
        super(Yana, self).__init__()
        self.resize(870, 600)
        # self.yanadb = YanaDB()
        YanaDB.startUpInitialization()
        self.initUI()

    # START: USER INTERFACE
    # LEFT MENU
    def filterNovelList(self):
        text = self.searchBox.text()

        filtered = []
        for te in self.novelList.findItems(text, Qt.MatchContains):
            filtered.append(te.text())

        lst = self.novelList
        for i in range(lst.count()):
            if lst.item(i).text() not in filtered:
                lst.item(i).setHidden(True)
            else:
                lst.item(i).setHidden(False)

    def leftMenuUI(self):
        src_list = YanaDB.getSourceList()

        self.sourceList = QComboBox(self)

        self.sourceModel = QStandardItemModel()
        for src in src_list:
            item = QStandardItem(src['src_name'])
            item.setData(src['src_id'])
            self.sourceModel.appendRow(item)

        self.sourceList.setModel(self.sourceModel)
        self.sourceList.resize(200, 22)
        self.sourceList.move(10, 30)
        self.sourceList.currentIndexChanged.connect(self.updateNovelList)

        self.btnUpdateList = QPushButton(self)
        self.btnUpdateList.setText("Update Novel List")
        # self.btnUpdateList.resize(100, 30)
        self.btnUpdateList.adjustSize()
        self.btnUpdateList.move(220, 30)
        self.btnUpdateList.clicked.connect(self.scrappingNovelList)

        self.labelnovel = QLabel(self)
        self.labelnovel.setText("Novel List (Double Click to show novel Info)")
        self.labelnovel.adjustSize()
        self.labelnovel.move(10, 58)

        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("Search Novel here...")
        self.searchBox.move(10, 75)
        self.searchBox.resize(200, 20)
        self.searchBox.setStyleSheet("border: 1px solid #999;")
        self.searchBox.textChanged.connect(self.filterNovelList)

        self.novelList = QListWidget(self)
        self.novelList.move(10, 100)
        self.novelList.resize(200, self.height() - 140)
        self.novelList.itemDoubleClicked.connect(self.showNovelInfo)

        self.updateNovelList()

    # NOVEL INFO
    def novelInfoUI(self):
        self.cover_width = 121
        self.cover_height = 169
        book_cover = QPixmap(self._book_cover_def).scaled(
            self.cover_width, self.cover_height)

        self.bookCover = QLabel(self)
        self.bookCover.move(230, 75)
        self.bookCover.setPixmap(book_cover)
        self.bookCover.resize(self.cover_width, self.cover_height)
        self.bookCover.setStyleSheet("border: 1px solid #999;")

        x = 371
        y = 75
        y_height = 20

        self.titleLabel = QLabel(self)
        self.titleLabel.setText("Title")
        self.titleLabel.move(x, y)
        self.titleLabel.setStyleSheet("font-weight: bold")
        self.titleLabel.adjustSize()

        y = y + y_height

        self.titleAnotherLabel = QLabel(self)
        self.titleAnotherLabel.setText("Title (Another)")
        self.titleAnotherLabel.move(x, y)
        self.titleAnotherLabel.setStyleSheet("font-weight: bold")
        self.titleAnotherLabel.adjustSize()

        y = y + y_height

        self.authorLabel = QLabel(self)
        self.authorLabel.setText("Author")
        self.authorLabel.move(x, y)
        self.authorLabel.setStyleSheet("font-weight: bold")
        self.authorLabel.adjustSize()

        y = y + y_height

        self.artistLabel = QLabel(self)
        self.artistLabel.setText("Artist")
        self.artistLabel.move(x, y)
        self.artistLabel.setStyleSheet("font-weight: bold")
        self.artistLabel.adjustSize()

        y = y + y_height

        self.descLabel = QLabel(self)
        self.descLabel.setText("Desc")
        self.descLabel.move(x, y)
        self.descLabel.setStyleSheet("font-weight: bold")
        self.descLabel.adjustSize()

        y = y + 70

        self.lastUpdateLabel = QLabel(self)
        self.lastUpdateLabel.setText("Last Update")
        self.lastUpdateLabel.move(x, y)
        self.lastUpdateLabel.setStyleSheet("font-weight: bold")
        self.lastUpdateLabel.adjustSize()

        x = 470
        y = 75

        self.dot = QLabel(self)
        self.dot.setText(":")
        self.dot.move(x, y)
        self.dot.setStyleSheet("font-weight: bold")
        self.dot.adjustSize()

        y = y + y_height

        self.dot = QLabel(self)
        self.dot.setText(":")
        self.dot.move(x, y)
        self.dot.setStyleSheet("font-weight: bold")
        self.dot.adjustSize()

        y = y + y_height

        self.dot = QLabel(self)
        self.dot.setText(":")
        self.dot.move(x, y)
        self.dot.setStyleSheet("font-weight: bold")
        self.dot.adjustSize()

        y = y + y_height

        self.dot = QLabel(self)
        self.dot.setText(":")
        self.dot.move(x, y)
        self.dot.setStyleSheet("font-weight: bold")
        self.dot.adjustSize()

        y = y + y_height

        self.dot = QLabel(self)
        self.dot.setText(":")
        self.dot.move(x, y)
        self.dot.setStyleSheet("font-weight: bold")
        self.dot.adjustSize()

        y = y + 70

        self.dot = QLabel(self)
        self.dot.setText(":")
        self.dot.move(x, y)
        self.dot.setStyleSheet("font-weight: bold")
        self.dot.adjustSize()

        x = 480
        y = 75

        self.novelTitle = QLabel(self)
        self.novelTitle.move(x, y)

        y = y + y_height

        self.novelAnotherTitle = QLabel(self)
        self.novelAnotherTitle.move(x, y)

        y = y + y_height

        self.novelAuthor = QLabel(self)
        self.novelAuthor.move(x, y)

        y = y + y_height

        self.novelArtist = QLabel(self)
        self.novelArtist.move(x, y)

        y = y + y_height + 70

        self.novelLastUpdate = QLabel(self)
        self.novelLastUpdate.move(x, y)

        self.chapterList = QListWidget(self)
        self.chapterList.move(230, y + (y_height + 10))
        self.chapterList.resize(self.width() - 240, self.height() - (y + (y_height + 10 + 10)) - 30)
        self.chapterList.itemDoubleClicked.connect(self.readChapter)

    # FOOTER
    def footerUI(self):
        self.progress = QProgressBar(self)
        self.progress.move(10, self.height() - 20)
        self.progress.resize(self.width() - 10, 10)
        self.progress.setMaximum(100)

        self.progress_label = QLabel(self)
        # self.progress_label.setText("Progress Label")
        self.progress_label.move(10, self.height() - 35)
        self.progress_label.adjustSize()

    # INIT UI
    def initUI(self):
        # HEADER
        self.welcome = QLabel(self)
        self.welcome.setText("From Novel lovers for Novel Lover by @haniefhan")
        # self.welcome.resize(300, 20)
        self.welcome.adjustSize()
        self.welcome.move(10, 10)
        # welcome.setStyleSheet("border:1px solid black;")

        self.leftMenuUI()
        self.novelInfoUI()
        self.footerUI()
    # END: USER INTERFACE

    # START: SCRAPPING NOVEL LIST
    def changeProgressLabel(self, text):
        self.progress_label.setText(text)
        self.progress_label.adjustSize()

    def updateProgress(self, progress):
        self.progress.setValue(progress)

    def updateNovel(self, nv):
        YanaDB.updateNovelList(nv, self.src_id)

    def updateComplete(self, jml):
        self.updateNovelList()
        QMessageBox.information(
            None, 'Update Novel List',
            '%s novel found!' % jml)

    def updateFailed(self, text):
        QMessageBox.information(
            None, 'Update Novel List',
            text)

    def scrappingNovelList(self):
        # set src_id
        self.src_id = YanaDB.getSourceId(self.sourceList.currentText())
        src_text = self.sourceList.currentText()

        # do it in another thread
        self.worker = UpdateThread(src_text)
        self.worker.start()
        self.worker.update_progress.connect(self.updateProgress)
        self.worker.update_progress_label.connect(self.changeProgressLabel)
        self.worker.update_novel.connect(self.updateNovel)
        self.worker.update_complete.connect(self.updateComplete)
        self.worker.update_failed.connect(self.updateFailed)
    # END: SCRAPPING NOVEL LIST

    def updateNovelList(self):
        # get item data (id and text) current index
        # show data with : print(item.data(), item.text())
        item = self.sourceModel.item(self.sourceList.currentIndex())

        # clear all data
        self.novelList.clear()

        for nv in YanaDB.getNovelList(item.data()):
            item = QListWidgetItem(nv['nv_title'])
            item.setData(33, nv['nv_id'])
            item.setData(3, nv['nv_title'])  # 3 is Qt.TooltipRole
            self.novelList.addItem(item)

    def showNovelInfo(self):
        nv_id = self.novelList.currentItem().data(33)
        info = YanaDB.getNovelInfo(nv_id)

        self.novelTitle.setText(info['nv_title'])
        self.novelTitle.adjustSize()

        self.novelAnotherTitle.setText(info['nv_title_original'])
        self.novelAnotherTitle.adjustSize()

        self.novelAuthor.setText(info['nv_author'])
        self.novelAuthor.adjustSize()

        self.novelArtist.setText(info['nv_artist'])
        self.novelArtist.adjustSize()

        self.novelLastUpdate.setText(info['nv_last_update'])
        self.novelLastUpdate.adjustSize()

        if info['nv_image_url_original'] != '':
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
            }

            data = requests.get(info['nv_image_url_original'], headers=headers)

            image = QImage()
            image.loadFromData(data.content)

            book_cover = QPixmap(image).scaled(
                self.cover_width, self.cover_height)
            self.bookCover.setPixmap(book_cover)
        else:
            book_cover = QPixmap(self._book_cover_def).scaled(
                self.cover_width, self.cover_height)
            self.bookCover.setPixmap(book_cover)

        groupName = ""
        self.chapterList.clear()
        for chp in YanaDB.getChapterList(info['nv_id']):
            if chp['volume_name'] != groupName:
                # self.chapterList.addItem(chp['volume_name'])
                item = QListWidgetItem(chp['volume_name'])
                item.setData(33, 'chapter_header')
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                self.chapterList.addItem(item)
                groupName = chp['volume_name']
            # self.chapterList.addItem(" - " + chp['chp_title'])
            item = QListWidgetItem(" - " + chp['chp_title'])
            item.setData(33, 'chapter')
            item.setData(34, chp['chp_id'])
            item.setData(35, chp['src_id'])
            self.chapterList.addItem(item)

    def readChapter(self):
        # check if header
        if self.chapterList.currentItem().data(33) == "chapter":
            chp_id = self.chapterList.currentItem().data(34)
            src_id = self.chapterList.currentItem().data(35)

            yanaread = YanaRead(self)
            yanaread.show()
            yanaread.read(src_id, chp_id)


def window():
    appctxt = ApplicationContext()
    # appctxt.get_resource("../resources/yana.db")
    appctxt.app.setStyle("windowsvista")  # windowsvista, Windows, Fusion
    window = Yana()

    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)


window()

# if __name__ == '__main__':
#     appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
#     window = QMainWindow()
#     window.resize(870, 600)
#     window.show()
#     exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
#     sys.exit(exit_code)
