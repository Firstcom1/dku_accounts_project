import sys
import os, os.path
import datetime
from PySide2 import QtUiTools, QtGui
from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem

todayFile_obj = None # 파일접근 제어

class ItemAbstract:
    '''
        num(Int), type(Str), date(Str), category(Str), usePlace(Str), amountMoney(Int), comment(Str)
    '''
    def __init__(self, index, date, category, usePlace, amountMoney, comment):
        self.index = index
        self.date = date
        self.category = category
        self.usePlace = usePlace
        self.amountMoney = amountMoney
        self.comment = comment
'''
    Expenditure, Income, Asset -> ItemAbstract (맴버변수 초기화 코드 중복 최소화)
'''
class Expenditure(ItemAbstract):
    def __init__(self, index, type, date, category, usePlace, amountMoney, comment):
        super().__init__(index, type, date, category, usePlace, amountMoney, comment)
        self.type = type

class Income(ItemAbstract):
    def __init__(self, index, type, date, category, usePlace, amountMoney, comment):
        super().__init__(index, type, date, category, usePlace, amountMoney, comment)
        self.type = type

class Asset(ItemAbstract):
    def __init__(self, index, type, date, category, usePlace, amountMoney, comment):
        super().__init__(index, type, date, category, usePlace, amountMoney, comment)
        self.type = type

class MainView(QMainWindow):
    # QMainWindow 는 cetralwidget, menubar, statusbar 클래스를 포함하는 프로그램의 MainUI 역할을 한다.
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        global UI_set
        UI_set = QtUiTools.QUiLoader().load(resource_path("./dku_accounts_project.ui"))

        runtime_date = datetime.datetime.now()
        todayFilename = str(runtime_date.year) + "-" + str(runtime_date.month) + "-" + str(runtime_date.day) + ".txt"
        # todayFilename(str) : (ex) 2021-12-3
        self.openFileData(todayFilename) # 지출, 수입, 자산 데이터를 담고 있는 파일 오픈


        UI_set.TW_test.horizontalHeader().setVisible(True)
        UI_set.TW_test_2.horizontalHeader().setVisible(True)
        UI_set.TW_test_3.horizontalHeader().setVisible(True)

        UI_set.TW_test.verticalHeader().setVisible(True)
        UI_set.TW_test_2.verticalHeader().setVisible(True)
        UI_set.TW_test_3.verticalHeader().setVisible(True)

        UI_set.TAB_displayType.currentChanged.connect(self.displayFiledata)

        self.setCentralWidget(UI_set)
        self.setWindowTitle("UI TEST")
        # self.setWindowIcon(QtGui.QPixmap(resource_path("./images/communication.jpg")))
        self.resize(1300, 800)
        self.show()

    def openFileData(self, todayFilename):
        global todayFile_obj
        print(todayFilename)
        if os.path.isfile(resource_path("./date/" + todayFilename)):
            # '오늘' 실행했던 적이 있던 경우 데이터 보존을 위해 읽기모드(r)를 통해 파일개방
            todayFile_obj = open("./date/" + todayFilename, "rt+", encoding="UTF8")
        else: # '오늘' 최초 실행에 해당 -> 최초 실행 시 파일이 없으므로 쓰기모드(w)를 통해 파일생성 및 개방
            todayFile_obj = open("./date/" + todayFilename, "wt+", encoding="UTF8")

    def displayFiledata(self):
        displayType = UI_set.TAB_displayType.currentIndex()

        if displayType == 0: # 현재 탭페이지가 '전체 출납목록[0]'인 경우
            listForDisplay = todayFile_obj.readlines()
            for infoForDisplay in listForDisplay:
                temp = infoForDisplay.split(",")
                for i in range(len(temp)):
                    real = temp[i].split()
                    print(real)


def resource_path(relative_path): #안녕
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainView()
    # main.show()
    sys.exit(app.exec_())