import sys
import os, os.path
import datetime
from PySide2 import QtUiTools, QtGui, QtCore
from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem

selectedDay_detail = 0 # dataType: Str, form: "2021-02-02"
selectedDay_day = 0 # dataType: Int, form: 5
selectedDay_month = 0 # dataType:Int, form: 12
selectedDay_year = 0 # dataType: Int, form : 2021

periodStartDay_detail = 0
periodStartDay_day = 0
periodStartDay_month = 0
periodStartDay_year = 0
# 위와 동일

periodEndDay_detail = 0
periodEndDay_day = 0
periodEndDay_month = 0
periodEndDay_year = 0
# 위와 동일

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        global UI_set
        UI_set = QtUiTools.QUiLoader().load(resource_path("./dku_accounts_project.ui"))

        # TW(TableWidget)의 열_헤더부분 활성화
        UI_set.TW_displayAllAccounts.horizontalHeader().setVisible(True)
        UI_set.TW_displayExpenditure.horizontalHeader().setVisible(True)
        UI_set.TW_displayIncome.horizontalHeader().setVisible(True)

        # TW(TableWidget)의 행_헤더부분 활성화
        UI_set.TW_displayAllAccounts.verticalHeader().setVisible(True)
        UI_set.TW_displayExpenditure.verticalHeader().setVisible(True)
        UI_set.TW_displayIncome.verticalHeader().setVisible(True)

        # 조회방법 RB(RadioButton) 선택 상황에 따른 활성화, 비활성화
        UI_set.RB_viewByPeriod.clicked.connect(self.EnableViewPeriod)
        UI_set.RB_viewByDay.clicked.connect(self.EnableViewDay)

        # 조회방법: "일별 조회"에서 사용자가 조회하고자 하는 특정한 날의 정보를 받아서 전역변수에 저장
        UI_set.CW_selectDay.clicked.connect(self.getSelectedDay)

        # 조회방법: "기간별 조회"에서 "조회 시작일", "조회 종료일" 정보를 받아서 전역변수에 저장
        UI_set.DE_periodStartDay.dateChanged.connect(self.getPeriodStartDay)
        UI_set.DE_periodEndDay.dateChanged.connect(self.getPeriodEndDay)

        self.setCentralWidget(UI_set)
        self.setWindowTitle("UI TEST")
        self.setWindowIcon(QtGui.QPixmap(resource_path("./image/icon_accounts.png")))
        self.resize(1300, 800)
        self.show()

    '''
        #. Name: EnableViewDay()
        #. Feature
            (1) 켈린더 위젯 활성화, 기간설정 DateEdit 위젯 비활성화
    '''
    def EnableViewDay(self):
        UI_set.CW_selectDay.setEnabled(1)
        UI_set.DE_periodStartDay.setEnabled(0)
        UI_set.DE_periodEndDay.setEnabled(0)

    '''
        #. Name: EnableViewPeriod()
        #. Feature
            (1) 켈린더 위젯 비활성화, 기간설정 DateEdit 위젯 활성화
    '''
    def EnableViewPeriod(self):
        UI_set.CW_selectDay.setEnabled(0)
        UI_set.DE_periodStartDay.setEnabled(1)
        UI_set.DE_periodEndDay.setEnabled(1)

    '''
        #. Name: getSelectedDay()
        #. Feature
            (1) 실행조건 : CalendarWidget에서 사용자가 특정 날짜를 선택했을 때
            (2) QDate 형식의 사용자가 선택한 특정 날짜 정보가 담긴 객체 받아옴.
            (3) 전역변수 selectedDay_detail, selectedDay_day, selectedDay_month, selectedDay_year 에 해당 정보 저장
    '''
    def getSelectedDay(self):
        global selectedDay_detail, selectedDay_day, selectedDay_month, selectedDay_year
        selectedDate = UI_set.CW_selectDay.selectedDate()
        selectedDay_detail = str(selectedDate.year()) + "-" + str(selectedDate.month()) + "-" + str(selectedDate.day())
        selectedDay_day = selectedDate.day()
        selectedDay_month = selectedDate.month()
        selectedDay_year = selectedDate.year()

    def getPeriodStartDay(self):
        global periodStartDay_detail, periodStartDay_day, periodStartDay_month, periodStartDay_year
        periodStartDay = UI_set.DE_periodStartDay.date()
        periodStartDay_detail = str(periodStartDay.year()) + "-" + str(periodStartDay.month()) + "-" + str(periodStartDay.day())
        periodStartDay_day = periodStartDay.day()
        periodStartDay_month = periodStartDay.month()
        periodStartDay_year = periodStartDay.year()
        print(periodStartDay_detail)

    def getPeriodEndDay(self):
        global periodEndDay_detail, periodEndDay_day, periodEndDay_month, periodEndDay_year
        periodEndDay = UI_set.DE_periodEndDay.date()
        periodEndDay_detail = str(periodEndDay.year()) + "-" + str(periodEndDay.month()) + "-" + str(periodEndDay.day())
        periodEndDay_day = periodEndDay.day()
        periodEndDay_month = periodEndDay.month()
        periodEndDay_year = periodEndDay.year()
        print(periodEndDay_detail)

def resource_path(relative_path): #안녕
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainView()
    # main.show()
    sys.exit(app.exec_())

''' in dku_accounts.project.ui
<Table Object> 
    UI_set.TW_displayAllAccounts  <- 전체 출납목록 Tab에 존재하는 QTableWidget
    UI_set.TW_displayExpenditure  <- 지출 Tab에 존재하는 QTableWidget
    UI_set.TW_displayIncome  <- 수입 Tab에 존재하는 QTableWidget

<CheckBox>
    UI_set.CH_fixEPCategory  <- 전체 출납목록 Tab에 존재하는 QCheckBox
    UI_set.CH_fixIncomCategory  <- 전체 출납목록 Tab에 존재하는 QCheckBox
    UI_set.CH_fixEPCategory_2  <- 지출 Tab에 존재하는 QCheckBox

<ComboBox>
    UI_set.CB_fixEPCategory  <- 전체 출납목록 Tab에 존재하는 QComboBox
    UI_set.CB_fixIncomeCategory  <- 전체 출납목록 Tab에 존재하는 QComboBox
    UI_set.CB_fixEPCategory_2  <- 지출 Tab에 존재하는 QComboBox
    UI_set.CB_typeOfMoney  <- 항목추가 Group에 존재하는 QComboBox
    UI_set.CB_categoryItem <- 항목추가 Group에 존재하는 QComboBox

<RadioButton>
    UI_set.RB_viewByPeriod  <- 조회방법에 존재하는 QRadioBox
    UI_set.RB_viewByDay  <- 조회방법에 존재하는 QRadioBox

<Calendar>
    UI_set.CW_selectDay  <- 일별 조회방식으로 특정한 날(Day)를 선택하는 켈린더 QCalendarWidget

<DateEdit>
    UI_set.DE_periodStartDay  <- 기간 조회방식으로 특정 기간(Period)의 시작일을 선택하는 QDateEdit
    UI_set.DE_periodEndDay  <- 기간 조회방식으로 특정 기간(Period)의 종료일을 선택하는 QDateEdit
    UI_set.DE_flowDate  <- 항목추가 Group에 존재하는 QDateEdit

<TextBrowser>
    UI_set.TB_displayTips  <- 사용자 지출, 수입 내역을 기반으로한 재무관리 TIP 제공하는 QTextBrowser

<PushButton>
    UI_set.BT_compareByStatic  <- 통계자료로 사용자 데이터 기반 비교를 위한 UI표시 이벤트 발생 QPushButton
    BT_addItem  <- 항목추가 Group에 존재하는 QPushButton

<LineEdit>
    UI_set.LE_usePlace  <- 항목추가 Group에 존재하는 QLineEdit
    UI_set.LE_amountOfMoeny  <- 항목추가 Group에 존재하는 QLineEdit
    UI_set.LE_comment  <- 항목추가 Group에 존재하는 QLineEdit
    UI_set.LE_moneyState  <- 한달 재무현황 표시 QLineEdit
    UI_set.LE_dayState  <- 하루 재무현황 표시 QLineEdit
'''