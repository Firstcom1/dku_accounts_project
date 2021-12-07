import sys, random
import os, os.path
import pandas as pd
import matplotlib as plt
import datetime
from PySide2.QtCharts import *
from PySide2.QtGui import QPainter, QPen
from PySide2 import QtUiTools, QtGui, QtCore, QtWidgets
from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QGraphicsView, QGraphicsScene

categoryExp = ['기타', '음식', '공부', '취미', '생활'] # dataType: List
categoryIncome = ['경상소득', '비경상소득'] # dataType: List

selectedDay_detail = 0 # dataType: Str, form: "2021-02-02"
selectedDay_day = 0 # dataType: Int, form: 5
selectedDay_month = 0 # dataType:Int, form: 12
selectedDay_year = 0 # dataType: Int, form : 2021

periodStartDay_detail = 0 # dataType: Str
periodStartDay_day = 0 # dataType: Int
periodStartDay_month = 0 # dataType: Int
periodStartDay_year = 0 # dataType: Int

periodEndDay_detail = 0 # dataType: Str
periodEndDay_day = 0 # dataType: Int
periodEndDay_month = 0 # dataType: Int
periodEndDay_year = 0 # dataType: Int

addItem_typeMoney = 0 # dataType: Str
addItem_dateMoney = 0 # dataType: Str
addItem_categoryMoney = 0 # dataType: Str
addItem_placeMoney = 0 # dataType: Str
addItem_amountMoney = 0 # dataType: Str
addItem_commentMoney = 0 # dataType: Str
addItem_fixedMoney = 0 # dataType: Bool

#데이터 처리용 변수
mtype = 0 # dataType: Str
date = 0 # dataType: Str
category = 0 # dataType: Str
place = 0 # dataType: Str
balance = 0 # dataType: Int
comment = 0 # dataType: Str

# "항목추가"에 필요한 정보들
# 잠재적으로 데이터파일에 insert

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        global UI_set, ErrorUI, ComparisonSTUI
        global addItem_typeMoney, addItem_dateMoney, addItem_categoryMoney
        global file_path; file_path="./accounts_data.csv"
        UI_set = QtUiTools.QUiLoader().load(resource_path("./dku_accounts_project.ui"))
        ErrorUI = QtUiTools.QUiLoader().load(resource_path("./addError.ui"))
        ComparisonSTUI = QtUiTools.QUiLoader().load(resource_path("./ComparisonST.ui"))

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

        # 항목추가 中 "현금흐름 유형"에 대한 정보를 받아 전역변수에 저장
        addItem_typeMoney = UI_set.CB_typeMoney.currentText() # Default값: "지출"
        UI_set.CB_typeMoney.currentTextChanged.connect(self.getAddItem_typeMoney) # 변경되면 갱신, "고정지출" 라벨(LB) <-> "고정수입" 라벨(LB)

        # 항목추가 中 "날짜"에 대한 정보를 받아 전역변수에 저장
        addItem_date = UI_set.DE_dateMoney.date()
        addItem_dateMoney = str(addItem_date.year()) + "-" + str(addItem_date.month()) + "-" + str(addItem_date.day()) # Default값: "2021-12-01"
        UI_set.DE_dateMoney.dateChanged.connect(self.getAddItem_dateMoney) # 변경되면 갱신

        # 항목추가 中 "카테고리"에 대한 정보를 받아 전역변수에 저장
        addItem_categoryMoney = UI_set.CB_categoryMoney.currentText()  # Default값: "카테고리"
        UI_set.CB_categoryMoney.currentTextChanged.connect(self.getAddItem_categoryMoney) # 변경되면 갱신

        # 항목추가 中 "항목추가" 버튼을 클릭했을 때 addItem_typeMoney, addItem_date, addItem_categoryMoney 이외에 나머지
        # addItem_placeMoney, addItem_amountMoney, addItem_commentMoney와 함께 데이터를 취합저장
        # 단, addItem_placeMoney, addItem_amountMoney의 항목이 채워져 있지 않으면 항목추가 거부
        UI_set.BT_addItem.clicked.connect(self.getAddItem_remainValues)

        ErrorUI.BT_close.clicked.connect(self.closeError)

        self.setCentralWidget(UI_set)
        self.setWindowTitle("가계부")
        self.setWindowIcon(QtGui.QPixmap(resource_path("./image/icon.png")))
        self.resize(1300, 800)
        self.show()

        ErrorUI.setWindowTitle("Error")
        ErrorUI.setWindowIcon(QtGui.QPixmap(resource_path("./image/icon.png")))
        ErrorUI.resize(450, 200)

        self.ComparisonST_UIOperation();

    def ComparisonST_UIOperation(self):
        global ComparisonSTUI

        series = QtCharts.QPieSeries()
        series.append("Python", 80)
        series.append("C++", 70)
        series.append("Java", 50)
        series.append("C#", 90)
        series.append("PHP", 30)

        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        chart.setTitle("Test")

        set0 = QtCharts.QBarSet('X0')
        # set1 = QtCharts.QBarSet('X1')
        # set2 = QtCharts.QBarSet('X2')
        # set3 = QtCharts.QBarSet('X3')
        # set4 = QtCharts.QBarSet('X4')

        set0.append([random.randint(0, 10) for x in range(6)])
        # set1.append([random.randint(0, 10) for x in range(6)])
        # set2.append([random.randint(0, 10) for x in range(6)])
        # set3.append([random.randint(0, 10) for x in range(6)])
        # set4.append([random.randint(0, 10) for x in range(6)])

        series1 = QtCharts.QBarSeries()
        series1.append(set0)
        # series1.append(set1)
        # series1.append(set2)
        # series1.append(set3)
        # series1.append(set4)

        chart1 = QtCharts.QChart()
        chart1.addSeries(series1)
        chart1.setTitle("test")
        chart1.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

        xTags = ['a'] #, 'b', 'c', 'd', 'e']

        axisX = QtCharts.QBarCategoryAxis()
        axisX.append(xTags)

        axisY = QtCharts.QValueAxis()
        axisY.setRange(0, 15)

        chart1.addAxis(axisX, QtCore.Qt.AlignBottom)
        chart1.addAxis(axisY, QtCore.Qt.AlignLeft)

        chart1.legend().setVisible(True)
        chart1.legend().setAlignment(QtCore.Qt.AlignBottom)

        chartview = QtCharts.QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        chartview1 = QtCharts.QChartView(chart1)
        chartview1.setRenderHint(QPainter.Antialiasing)

        ComparisonSTUI.TAB_cmpExpWay.insertTab(0, chartview, "카테고리별")
        ComparisonSTUI.TAB_cmpExpWay.insertTab(1, chartview1, "대한민국 평균지출")
        ComparisonSTUI.show()

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
            #. Name: totDataFile()
            #. Feature
                (1) 사용자 입력 데이터 csv 파일(file_path)에 저장
        '''
    def toDataFile(self):
        df1=pd.read_csv(file_path)
        data={'mtype': addItem_typeMoney, 'date': addItem_dateMoney, 'category': addItem_categoryMoney,'place': addItem_placeMoney, 'balance': addItem_amountMoney, 'comment': addItem_commentMoney}
        df2 = df1.append(data, ignore_index=True)
        df2.to_csv("accounts_data.csv")
        
        '''
        #. Name: checkStat()
        #. Feature
            (1) 데이터 분석을 위한 기초
    '''
    def checkStat(self):
        self.stat=pd.read_csv("./가구당_월평균_가계수지.csv")
    
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

    '''
        #. Name: getPeriodStartDay()
        #. Feature
            (1) 실행조건 : 사용자가 DE_periodStartDay에서 날짜를 변경했을 때
            (2) QDate 형식의 사용자가 선택한 특정 날짜 정보가 담긴 객체 받아옴.
            (3) 전역변수 periodStartDay_detail, periodStartDay_day, periodStartDay_month, periodStartDay_year 에 해당 정보 저장
    '''
    def getPeriodStartDay(self):
        global periodStartDay_detail, periodStartDay_day, periodStartDay_month, periodStartDay_year
        periodStartDay = UI_set.DE_periodStartDay.date()
        periodStartDay_detail = str(periodStartDay.year()) + "-" + str(periodStartDay.month()) + "-" + str(periodStartDay.day())
        periodStartDay_day = periodStartDay.day()
        periodStartDay_month = periodStartDay.month()
        periodStartDay_year = periodStartDay.year()
        print(periodStartDay_detail)

    '''
        #. Name: getPeriodEndDay()
        #. Feature
            (1) 실행조건 : 사용자가 DE_periodEndDay에서 날짜를 변경했을 떄
            (2) QDate 형식의 사용자가 선택한 특정 날짜 정보가 담긴 객체 받아옴.
            (3) 전역변수 periodEndDay_detail, periodEndDay_day, periodEndDay_month, periodEndDay_year 에 해당 정보 저장
    '''
    def getPeriodEndDay(self):
        global periodEndDay_detail, periodEndDay_day, periodEndDay_month, periodEndDay_year
        periodEndDay = UI_set.DE_periodEndDay.date()
        periodEndDay_detail = str(periodEndDay.year()) + "-" + str(periodEndDay.month()) + "-" + str(periodEndDay.day())
        periodEndDay_day = periodEndDay.day()
        periodEndDay_month = periodEndDay.month()
        periodEndDay_year = periodEndDay.year()
        print(periodEndDay_detail)

    '''
        #. Name: getAddItem_typeMoney()
        #. Feature
            (1) 실행조건 : 사용자가 CB_typeMoney에서 "현금흐름 유형"을 변경했을 떄
            (2) 변경된 "현금흐름 유형" 사항을 갱신
    '''
    def getAddItem_typeMoney(self):
        global addItem_typeMoney
        addItem_typeMoney = UI_set.CB_typeMoney.currentText()

        if addItem_typeMoney == "지출":
            UI_set.CH_fixedMoney.setText("고정지출")
        elif addItem_typeMoney == "수입":
            UI_set.CH_fixedMoney.setText("고정수입")
    '''
        #. Name: getAddItem_dateMoney()
        #. Feature
            (1) 실행조건 : 사용자가 DE_dateMoney에서 "날짜"를 변경했을 떄
            (2) 변경된 "날짜" 사항을 갱신
    '''
    def getAddItem_dateMoney(self):
        global addItem_dateMoney
        addItem_date = UI_set.DE_dateMoney.date()
        addItem_dateMoney = str(addItem_date.year()) + "-" + str(addItem_date.money()) + "-" + str(addItem_date.day())

    '''
        #. Name: getAddItem_categoryMoney()
        #. Feature
            (1) 실행조건 : 사용자가 CB_categoryMoney에서 "카테고리"를 변경했을 떄
            (2) 변경된 "카테고리" 사항을 갱신
    '''
    def getAddItem_categoryMoney(self):
        global addItem_categoryMoney
        addItem_categoryMoney = UI_set.CB_categoryMoney.currentText()

    '''
        #. Name: getAddItem_remainValues()
        #. Feature
            (1) 실행조건 : 사용자가 항목추가 中 "항목추가" 버튼을 눌렀을 때
            (2) 나머지 "사용처", "금액", "코멘트", "고정"여부를 받아와 전역변수에 저장
            (3) 만약 "사용처", "금액", "카테고리" 란이 비었으면 에러메세지를 띄움. -> 데이터파일 저장 거부
    '''
    def getAddItem_remainValues(self):
        global addItem_placeMoney, addItem_amountMoney, addItem_commentMoney, addItem_fixedMoney

        addItem_placeMoney = UI_set.LE_placeMoney.text()
        addItem_amountMoney = UI_set.LE_amountMoeny.text()
        addItem_commentMoney = UI_set.LE_commentMoney.text()
        addItem_fixedMoney = UI_set.CH_fixedMoney.isChecked()

        if len(addItem_placeMoney) == 0 or len(addItem_amountMoney) == 0 or addItem_categoryMoney == "카테고리":
            if len(addItem_placeMoney) == 0 or len(addItem_amountMoney) == 0:
                ErrorUI.LB_addError.setText("사용처 또는 금액 정보가 없습니다.")
                ErrorUI.LB_addError.setStyleSheet("color: red; font-size: 20px")
            else:
                ErrorUI.LB_addError.setText("")
            if addItem_categoryMoney == "카테고리":
                ErrorUI.LB_categoryError.setText("카테고리를 지정해주세요.")
                ErrorUI.LB_categoryError.setStyleSheet("color: red; font-size: 20px")
            else:
                ErrorUI.LB_categoryError.setText("")

            ErrorUI.show()

    '''
        #. Name: closeError()
        #. Feature
            (1) ErrorUI를 닫음
    '''
    def closeError(self):
        ErrorUI.close()


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
    UI_set.CH_fixExpCategory  <- 전체 출납목록 Tab에 존재하는 QCheckBox
    UI_set.CH_fixIncomCategory  <- 전체 출납목록 Tab에 존재하는 QCheckBox
    UI_set.CH_fixExpCategory_2  <- 지출 Tab에 존재하는 QCheckBox

<ComboBox>
    UI_set.CB_fixExpCategory  <- 전체 출납목록 Tab에 존재하는 QComboBox
    UI_set.CB_fixIncomeCategory  <- 전체 출납목록 Tab에 존재하는 QComboBox
    UI_set.CB_fixExpCategory_2  <- 지출 Tab에 존재하는 QComboBox
    UI_set.CB_typeMoney  <- 항목추가 Group에 존재하는 QComboBox
    UI_set.CB_categoryMoney <- 항목추가 Group에 존재하는 QComboBox

<RadioButton>
    UI_set.RB_viewByPeriod  <- 조회방법에 존재하는 QRadioBox
    UI_set.RB_viewByDay  <- 조회방법에 존재하는 QRadioBox

<Calendar>
    UI_set.CW_selectDay  <- 일별 조회방식으로 특정한 날(Day)를 선택하는 켈린더 QCalendarWidget

<DateEdit>
    UI_set.DE_periodStartDay  <- 기간 조회방식으로 특정 기간(Period)의 시작일을 선택하는 QDateEdit
    UI_set.DE_periodEndDay  <- 기간 조회방식으로 특정 기간(Period)의 종료일을 선택하는 QDateEdit
    UI_set.DE_dateMoney  <- 항목추가 Group에 존재하는 QDateEdit

<TextBrowser>
    UI_set.TB_displayTips  <- 사용자 지출, 수입 내역을 기반으로한 재무관리 TIP 제공하는 QTextBrowser

<PushButton>
    UI_set.BT_compareByStatic  <- 통계자료로 사용자 데이터 기반 비교를 위한 UI표시 이벤트 발생 QPushButton
    BT_addItem  <- 항목추가 Group에 존재하는 QPushButton

<LineEdit>
    UI_set.LE_placeMoney  <- 항목추가 Group에 존재하는 QLineEdit
    UI_set.LE_amountMoney  <- 항목추가 Group에 존재하는 QLineEdit
    UI_set.LE_commentMoney  <- 항목추가 Group에 존재하는 QLineEdit
    UI_set.LE_moneyState  <- 한달 재무현황 표시 QLineEdit
    UI_set.LE_dayState  <- 하루 재무현황 표시 QLineEdit
'''
