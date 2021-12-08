import sys, random
import os, os.path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from PySide2.QtCharts import *
from PySide2.QtGui import QPainter, QPen
from PySide2 import QtUiTools, QtGui, QtCore, QtWidgets
from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QGraphicsView, QGraphicsScene
from PySide2.QtWidgets import QPushButton
from matplotlib import font_manager,rc

# 한글 폰트 설정
font_path = './malgun.ttf'
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

row = 0
col = 1

categoryExp = ['지출 카테고리', '음식', '공부', '취미', '생활', '기타']  # dataType: List
categoryIncome = ['수입 카테고리', '경상소득', '비경상소득']  # dataType: List

today=datetime.today().day #현재 일 , dataType: Int
now_month=datetime.today().month #현재 달, dataType: Int

stat = pd.read_csv("./가구당_월평균_가계수지.csv")
stat2 = pd.read_csv("./accounts_data.csv")

viewSelectedWay = None # dateType: Int, purpose: "조회 방법"(Group)에 RB(Radio Button) 활성화 옵션값 저장,  VIEW_ONEDAY, VIEW_PERIOD 둘 중 하나로 초기화
VIEW_ONEDAY = 1 # dateType: Int, purpose: 상수 for "일별 조회" 식별
VIEW_PREIOD = 2 # dateType: Int, purpose: 상수 for "기간 조회" 식별

COL_TYPE_IDX = 0 # dateType: Int, purpose: 상수 for 데이터파일 현금흐름 유형(열-헤더) 식별
COL_DATE_IDX = 1 # dateType: Int, purpose: 상수 for 데이터파일 날짜(열-헤더) 식별
COL_CATEGORY_IDX = 2 # dateType: Int, purpose: 상수 for 데이터파일 카테고리(열-헤더) 식별
removeButtonList = list() # dataType: list(of OPushButton)
removeEventIndex = 0

currentTableObject = None # dateType: QTabWidget, purpose: loadUserData_toFile에서 탭 종류 식별
currentTabType = list() # dateType: list, purpose: loadUserData_toFile에서 현금흐름 유형 종류 식별

isFixExp = False
isFixIncome = False
currentFixCategory_Exp = 0
currentFixCategory_Income = 0

tabIndex = 0
TAB_ALL_ACCOUNT = 0
TAB_EXP = 1
TAB_INCOME = 2

selectedDay = None # dateType: QtDate
selectedDay_detail = 0 # dataType: Str, form: "2021-02-02"
selectedDay_day = 0 # dataType: Int, form: 5
selectedDay_month = 0 # dataType:Int, form: 12
selectedDay_year = 0 # dataType: Int, form : 2021

periodStartToEnd = list()

periodStartDay = None # dateType: QtDate
periodStartDay_detail = 0 # dataType: Str
periodStartDay_day = 0 # dataType: Int
periodStartDay_month = 0 # dataType: Int
periodStartDay_year = 0 # dataType: Int

periodEndDay = None # dateType: QtDate
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

total_income = 0 #dataType: Int, 한달 수입
m_total_expd = 0 #dataType: Int, 한달 지출
d_total_expd = 0 #dataType: Int, 하루 지출

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.printMonth()

    def setupUI(self):

        global UI_set, ErrorUI, ComparisonSTUI

        UI_set = QtUiTools.QUiLoader().load(resource_path("./dku_accounts_project.ui"))
        ErrorUI = QtUiTools.QUiLoader().load(resource_path("./addError.ui"))
        ComparisonSTUI = QtUiTools.QUiLoader().load(resource_path("./ComparisonST.ui"))

        global removeEventIndex
        global currentTableObject, currentTabType
        global addItem_typeMoney, addItem_dateMoney, addItem_categoryMoney
        global selectedDay, selectedDay_detail, selectedDay_year, selectedDay_month, selectedDay_day
        global periodStartDay, periodStartDay_detail, periodStartDay_year, periodStartDay_month, periodStartDay_day
        global periodEndDay, periodEndDay_detail, periodEndDay_year, periodEndDay_month, periodEndDay_day

        # TAB_displayType의 TAB이 전환될 때 -> loadUserData_toFile() 과 유기적 연결 필요
        currentTableObject = UI_set.TW_displayAllAccounts # Default값: 전체 출납목록 TW
        currentTabType = ['지출', '수입']
        UI_set.TAB_displayType.setCurrentIndex(tabIndex)
        UI_set.TAB_displayType.currentChanged.connect(self.getCurrentTableObject)

        self.openUserDataFile() # accounts_data.csv 파일 (rt+)모드로 오픈
        self.loadUserData_toTable() # 처음 실행 시 파일데이터 전체를 "전체 출납목록"에 출력

        # TAB_displayType의 CB(ComboBox)_fixExpCategory 목록 작성
        UI_set.CB_fixExpCategory.addItems(categoryExp)
        UI_set.CB_fixExpCategory_2.addItems(categoryExp)

        # TAB_displayType의 CB(ComboBox)_fixIncomeCategory 목록 작성
        UI_set.CB_fixIncomeCategory.addItems(categoryIncome)
        UI_set.CB_fixIncomeCategory_2.addItems(categoryIncome)

        self.listenRemoveSignal()

        # 지출/수입 카테고리 CH(CheckBox)가 활성화
        UI_set.CH_fixExpCategory.stateChanged.connect(self.isFixCategory)
        UI_set.CH_fixExpCategory_2.stateChanged.connect(self.isFixCategory)
        UI_set.CH_fixIncomeCategory.stateChanged.connect(self.isFixCategory)
        UI_set.CH_fixIncomeCategory_2.stateChanged.connect(self.isFixCategory)

        #
        UI_set.CB_fixExpCategory.currentTextChanged.connect(self.fixCategory_Exp)
        UI_set.CB_fixExpCategory_2.currentTextChanged.connect(self.fixCategory_Exp)
        UI_set.CB_fixIncomeCategory.currentTextChanged.connect(self.fixCategory_Income)
        UI_set.CB_fixIncomeCategory_2.currentTextChanged.connect(self.fixCategory_Income)

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
        # >>>> Part1: [일별 조회] Default값: 초기 설정값 받아오기
        selectedDay = UI_set.CW_selectDay.selectedDate()
        selectedDay_detail = selectedDay.toString(QtCore.Qt.ISODate)
        selectedDay_day = selectedDay.day()
        selectedDay_month = selectedDay.month()
        selectedDay_year = selectedDay.year()
        # >>>> Part2: [일별 조회] 사용자 초기값 변경 시, 변경값 받아오기
        UI_set.CW_selectDay.clicked.connect(self.getSelectedDay)

        # 조회방법: "기간별 조회"에서 "조회 시작일" 정보를 받아서 전역변수에 저장
        # >>>> Part1: [조회 시작일] Default값: 초기 설정값 받아오기
        periodStartDay = UI_set.DE_periodStartDay.date()
        periodStartDay_detail = periodStartDay.toString(QtCore.Qt.ISODate)
        periodStartDay_day = periodStartDay.day()
        periodStartDay_month = periodStartDay.month()
        periodStartDay_year = periodStartDay.year()
        # >>>> Part2: [조회 시작일] 사용자 초기값 변경 시, 변경값 받아오기
        UI_set.DE_periodStartDay.dateChanged.connect(self.getPeriodStartDay)

        # 조회방법: "기간별 조회"에서 "조회 종료일" 정보를 받아서 전역변수에 저장
        # >>>> Part1: [조회 종료일] Default값: 초기 설정값 받아오기
        periodEndDay = UI_set.DE_periodEndDay.date()
        periodEndDay_detail = periodEndDay.toString(QtCore.Qt.ISODate)
        periodEndDay_day = periodEndDay.day()
        periodEndDay_month = periodEndDay.month()
        periodEndDay_year = periodEndDay.year()
        # >>>> Part2: [조회 종료일] 사용자 초기값 변경 시, 변경값 받아오기
        UI_set.DE_periodEndDay.dateChanged.connect(self.getPeriodEndDay)

        # 항목추가 中 "현금흐름 유형"에 대한 정보를 받아 전역변수에 저장
        addItem_typeMoney = UI_set.CB_typeMoney.currentText() # Default값: "지출"
        UI_set.CB_typeMoney.currentTextChanged.connect(self.getAddItem_typeMoney) # 변경되면 갱신, "고정지출" 라벨(LB) <-> "고정수입" 라벨(LB)

        # 항목추가 中 "날짜"에 대한 정보를 받아 전역변수에 저장
        addItem_date = UI_set.DE_dateMoney.date()
        addItem_dateMoney = addItem_date.toString(QtCore.Qt.ISODate) # Default값: "2021-12-01"
        UI_set.DE_dateMoney.dateChanged.connect(self.getAddItem_dateMoney) # 변경되면 갱신

        # 항목추가 中 "현금흐름 유형"의 기본값 "지출"에 따라 CB_categoryMoney를 categoryExp(지출 카테고리)로 초기화
        UI_set.CB_categoryMoney.addItems(categoryExp)

        # 항목추가 中 "카테고리"에 대한 정보를 받아 전역변수에 저장
        addItem_categoryMoney = UI_set.CB_categoryMoney.currentText()  # Default값: "카테고리"
        UI_set.CB_categoryMoney.currentTextChanged.connect(self.getAddItem_categoryMoney) # 변경되면 갱신

        # 항목추가 中 "항목추가" 버튼을 클릭했을 때 addItem_typeMoney, addItem_date, addItem_categoryMoney 이외에 나머지
        # addItem_placeMoney, addItem_amountMoney, addItem_commentMoney와 함께 데이터를 취합저장
        # 단, addItem_placeMoney, addItem_amountMoney의 항목이 채워져 있지 않으면 항목추가 거부
        UI_set.BT_addItem.clicked.connect(self.getAddItem_remainValues)

        # BT(버튼): '재무관리 통계비교'를 누를 때 연결된 UI로 이동한다.
        UI_set.BT_compareByStatic.clicked.connect(self.popUpUi)
        
        #'나의 카테고리별 지출 비교'를 누를 때 이벤트 발생
        ComparisonSTUI.BT_compMyCategory.clicked.connect(self.getUserCategoryChart)
        
        #'나의 지출 비교 통계' 누를 때 이벤트 발생
        ComparisonSTUI.BT_compST.clicked.connect(self.getBothCategoryChart)
        
        #'재무 현황 새로고침' 누를 때 csv파일 읽어오기
        #UI_set.BT_f5.clicked.connect(self.reNewData)

        self.reNewData()
        self.printMoneyState()

        # 항목추가 에러UI에서 '확인'버튼을 눌렀을 때 UI를 닫는다.
        ErrorUI.BT_close.clicked.connect(self.closeError)

        self.setCentralWidget(UI_set)
        self.setWindowTitle("가계부")
        self.setWindowIcon(QtGui.QPixmap(resource_path("./image/icon.png")))
        self.resize(1300, 800)
        self.show()

        ErrorUI.setWindowTitle("Error")
        ErrorUI.setWindowIcon(QtGui.QPixmap(resource_path("./image/icon.png")))
        ErrorUI.resize(450, 200)
        
        ComparisonSTUI.setWindowTitle("재무 관리 통계")
        ComparisonSTUI.setWindowIcon(QtGui.QPixmap(resource_path("./image/dku.jpg")))

    '''
        #. Name: fixExped()
        #. Feature
            (1) 지출카테고리 고정
        #동작원리
            (1)기존 통합된 db에서 type이 지출인 데이터만 따로 추출
            (2) csv파일이 아니라 딕셔너리처럼 사용할 수 있습니다. 
             ex) {'type':['지출','지출'],'date':['2021-12-01','2021-12-02'],'category':['기타','음식']}
             이런 형태로 데이터를 자료형으로 만듭니다. 
            >>테이블위젯으로 출력하는 건 딕셔너리 자료형에서 추출해서 하시면 될 것 
    '''
    def fixExpd(self):
        expd_stat2 = stat2.loc[stat2['type'] == '지출']

    '''
        #. Name: fixIncome()
        #. Feature
            (1) 수입카테고리 고정
    '''
    def fixIncome(self):
        income_stat2 = stat2.loc[stat2['type'] == '수입']

    '''
        #. Name: reNewData()
        #. Feature
            (1) 총 수입, 총 지출량 갱신
    '''
    def reNewData(self):
        global total_income, m_total_expd, d_total_expd
        stat2=pd.read_csv("./accounts_data.csv")
        total_income=stat2.loc[(stat2['type']=='수입') & (str(now_month) in stat2["date"]),"balance"].sum()
        m_total_expd = stat2.loc[(stat2['type'] == '지출') & (str(now_month) in stat2["date"]), "balance"].sum() #한달 지출합계
        d_total_expd=stat2.loc[(stat2['type'] == '지출') & ( str(today) in stat2["date"]), "balance"].sum() #하루 지출합계
      
    '''
        #. Name: printMonth()
        #. Feature
            (1) 재무 현황에 무슨 달인지 프린트
    '''
    def printMonth(self):
        UI_set.LB_monthState.setText("%d월 한달 재무현황" %now_month)

    '''
        #. Name: printMoneyState()
        #. Feature
            (1) 재무 현황에 텍스트 프린트
    '''

    def printMoneyState(self):
        UI_set.LE_moneyState.setText("수입합계[%d] - 지출합계[%d] = %d(원)" %(total_income,m_total_expd,total_income-m_total_expd))
        UI_set.LE_dayState.setText("수입합계[%d] - 지출합계[%d] = %d(원)" % (total_income, d_total_expd, total_income - d_total_expd))

        
    def popUpUi(self):
        ComparisonSTUI.show()

    '''
        #. Name: openUserDataFile()
        #. Feature
            (1) accounts_data.csv 파일 오픈
            (2) 파일 디스크립터 userDataFile 획득
    '''
    def openUserDataFile(self):
        global userDataFile
        try:
            userDataFile = open("accounts_data.csv", "rt+", encoding="UTF8")
        except:
            sys.stderr.write("No file: %s\n" % "accounts_data.csv")
            exit(1)

    '''
        #. Name: loadUserData_toTable()
        #. Feature
            (0) 실행조건 [아래는 해당 함수에서 호출 여부를 확인할 수 있습니다.]
                >>> 프로그램 실행 시 전체 출납목록에 출력을 위해 실행
                >>> TAB_displayType에서 탭이 전환될 때 / (전체 출납목록) <-> (지출) <-> (수입)
                >>> "조회 방법" 중 "일별 조회" 활성화
                >>> "조회 방법" 중 "일별 조회" 조회 일자 변경
                >>> "조회 방법" 중 "기간별 조회" 활성화 
                >>> "조회 방법" 중 "기간별 조회" 조회 일자 변경
                >>> "항목 추가" 중 "항목 추가" 버튼 시 파일 갱신을 위해 실행
            (1) (전체 출납목록)TW(TableWidget)_displayAllAccounts에 accounts_data.csv에 존재하는 모든 데이터 출력
            (2) (지출)TW(TableWidget)_displayExpenditure에 accounts_data.cvs 데이터 中 "지출"에 해당하는 데이터만 출력
            (3) (수입)TW(TableWidget)_displayIncome에 accounts_data.cvs 데이터 中 "수입"에 해당하는 데이터만 출력
            (4) (전체 출납목록)(지출)(수입) TW(TableWidget)데이터 날짜 필터링
            (5) (전체 출납목록)(지출)(수입) TW(TableWidget)데이터 (지출)(수입)카테고리 필터링
    '''
    def loadUserData_toTable(self):
        global removeButtonList
        global row
        global col

        row = 0
        col = 1

        userDataFile.seek(0, 0)
        userData = userDataFile.readlines()

        currentTableObject.clearContents()
        removeButtonList.clear()
        for i in range(len(userData)):
            currentTableObject.removeRow(0)

        for dataSet in userData:
            dataFrag = dataSet.split(",")
            dataFrag[-1].replace("\n", "")

            for typeMoney in currentTabType: # (1) 현금흐름 유형 필터링
                type_flag = False
                if dataFrag[COL_TYPE_IDX] == typeMoney:
                    type_flag = True
                    break
                else:
                    type_flag = False
            if type_flag == True:
                pass
            else:
                continue


            if viewSelectedWay == None: # (2) 날짜 필터링
                pass
            elif viewSelectedWay == VIEW_ONEDAY:
                if dataFrag[COL_DATE_IDX] != selectedDay_detail:
                    continue
                else:
                    pass
            elif viewSelectedWay == VIEW_PREIOD:
                exist_flag = False
                for elementOfPeriod in periodStartToEnd:
                    if dataFrag[COL_DATE_IDX] == elementOfPeriod:
                        exist_flag = True
                        break
                    else:
                        flag = False
                if exist_flag == True:
                    pass
                elif exist_flag == False:
                    continue

            if isFixExp == True: # (3) 카테고리 필터링
                if dataFrag[COL_CATEGORY_IDX] != currentFixCategory_Exp:
                    continue
            if isFixIncome == True:
                if dataFrag[COL_CATEGORY_IDX] != currentFixCategory_Income:
                    continue

            currentTableObject.insertRow(row)
            removeButtonList.append(QPushButton("삭제"))
            currentTableObject.setCellWidget(row, 0, removeButtonList[row])
            for dataFragText in dataFrag:
                item = QTableWidgetItem(dataFragText)
                if dataFrag[COL_TYPE_IDX] == "지출":
                    item.setTextColor(QtGui.QColor("blue"))
                elif dataFrag[COL_TYPE_IDX] == "수입":
                    item.setTextColor(QtGui.QColor("red"))
                currentTableObject.setItem(row, col, item)
                col = col + 1
            row = row + 1
            col = 1

    '''
        #. Name: listenRemoveSignal()
        #. Feature
            (1) loadUserData_toFile() 호출 시 삭제 버튼 오브젝트를 재생성하므로 UI상에서 업데이트 하도록
    '''
    def listenRemoveSignal(self):
        for removeEventIndex in range(len(removeButtonList)):
            removeButtonList[removeEventIndex].clicked.connect(self.delFromFile)


    '''
        #. Name: delFromFile()
        #. Feature
            (1) listenRemoveSignal() 발생하는 삭제 이벤트, 그리고 이벤트가 발생한 버튼의 index를 추적
            (2) 그 index에 해당하는 모든 테이블 아이템을 csv내에 형식으로 합쳐서 str 생성
            (3) 생성된 str과 일치하는 파일데이터 삭제
    '''
    def delFromFile(self):
        global userDataFile
        removeData = list()

        removeEventIndex = removeButtonList.index(self.sender())

        for i in range(6):
            tempItemText = currentTableObject.item(removeEventIndex, i+1)
            tempItemText = tempItemText.text()
            removeData.append(tempItemText)

        removeDataStr = ",".join(removeData)

        userDataFile.seek(0, 0)
        userData = userDataFile.readlines()
        userData.remove(removeDataStr)

        userDataFile.close()
        try:
            userDataFile = open("accounts_data.csv", "wt+", encoding="UTF8") # 파일 내용을 모두 지우기 위해 읽기모드로 연다.
        except:
            sys.stderr.write("No file: %s\n" % "accounts_data.csv")
            exit(1)

        userDataFile.writelines(userData)

        self.loadUserData_toTable()
        self.listenRemoveSignal() # loadUserData_toTable() 호출 이후 "삭제" 버튼 객체가 모조리 재생성 되므로 setupUI()상에 존재하는 이벤트 대상 버튼을 갱신해줘야 한다.
        self.reNewData()

    '''
        #. Name: generatePeriodList()
        #. Feature
            (0) 실행조건 
                >>> "조회 방법" 그룹에서 "기간별 조회"를 활성화 시켰을 때
                >>> "기간별 조회"에서 "조회 시작일"과 "조회 종료일"을 변경시켰을 때 
            (1) 사용자가 설정한 기간 내 모든 날에 대한 QDate를 생성한다.
            (2) QDate를 Str 형식으로 변환하여 periodStartToEnd에 리스트로 append하여 저장한다.
            (3) periodStartToEnd(dataType: List)는 loadUserData_toFile()에서 데이터와 날짜 비교 시 사용된다.
    '''
    def generatePeriodList(self): # 기간별 조회에서 기간에 해당하는 모든 날의 Str값을 받아온다.
        global periodStartToEnd
        periodStartToEnd.clear()
        periodStartToEnd.append(periodStartDay)
        tempAddDay = periodStartDay.addDays(1)

        while periodEndDay.toString(QtCore.Qt.ISODate) != tempAddDay.toString(QtCore.Qt.ISODate):
            periodStartToEnd.append(tempAddDay)
            tempAddDay = tempAddDay.addDays(1)

        periodStartToEnd.append(tempAddDay)
        index = 0

        for elementOfperiod in periodStartToEnd: # 객체 형태(QDate)의 날짜를 Str형식의 날짜로 바꾼다.
            periodStartToEnd[index] = elementOfperiod.toString(QtCore.Qt.ISODate)
            index = index + 1

    '''
        #. Name: getCurrentTableObject()
        #. Feature
            (1) currentTableObject에 현재 UI 상에 표시되고 있는 TW객체 변경
            (2) currentTabType에 loadUserData_toFile에서 비교할 현금흐름 유형 지정
    '''
    def getCurrentTableObject(self):
        global currentTableObject # dataType: QTableWidget
        global currentTabType # dataType: List
        global tabIndex
        tabIndex = UI_set.TAB_displayType.currentIndex()

        if tabIndex == TAB_ALL_ACCOUNT:
            currentTableObject = UI_set.TW_displayAllAccounts
            currentTabType = ['지출', '수입']
        elif tabIndex == TAB_EXP:
            currentTableObject = UI_set.TW_displayExpenditure
            currentTabType = ['지출']
        elif tabIndex == TAB_INCOME:
            currentTableObject = UI_set.TW_displayIncome
            currentTabType = ['수입']

        self.loadUserData_toTable()
        self.listenRemoveSignal() # loadUserData_toTable() 호출 이후 "삭제" 버튼 객체가 모조리 재생성 되므로 setupUI()상에 존재하는 이벤트 대상 버튼을 갱신해줘야 한다.

    '''
        #. Name: isFixCategory()
        #. Feature
            (1) 테이블 위, [지출/수입]카테고리 체크 여부 저장
            (2) CH(CheckBox) on/off에 따라 CB(ComboBox) 활성화/비활성화
            (3) 그리고 loadUserData_toFile()을 호출하여 화면 갱신
    '''
    def isFixCategory(self):
        global isFixExp, isFixIncome

        if currentTableObject == UI_set.TW_displayAllAccounts:
            isFixExp = UI_set.CH_fixExpCategory.isChecked()
            if isFixExp == True:
                UI_set.CB_fixExpCategory.setEnabled(True)
            else:
                UI_set.CB_fixExpCategory.setEnabled(False)
            isFixIncome = UI_set.CH_fixIncomeCategory.isChecked()
            if isFixIncome == True:
                UI_set.CB_fixIncomeCategory.setEnabled(True)
            else:
                UI_set.CB_fixIncomeCategory.setEnabled(False)
        elif currentTableObject == UI_set.TW_displayExpenditure:
            isFixExp = UI_set.CH_fixExpCategory_2.isChecked()
            if isFixExp == True:
                UI_set.CB_fixExpCategory_2.setEnabled(True)
            else:
                UI_set.CB_fixExpCategory_2.setEnabled(False)
        elif currentTableObject == UI_set.TW_displayIncome:
            isFixIncome = UI_set.CH_fixIncomeCategory_2.isChecked()
            if isFixIncome == True:
                UI_set.CB_fixIncomeCategory_2.setEnabled(True)
            else:
                UI_set.CB_fixIncomeCategory_2.setEnabled(False)


        self.loadUserData_toTable()

    '''
        #. Name: fixCategory_Exp()
        #. Feature
            (1) 실제 CB에서 선택된 데이터 저장
            (2) 저장된 데이터는 loadUserData_toFile()에서 필터링하는데 사용
    '''
    def fixCategory_Exp(self):
        global currentFixCategory_Exp

        if currentTableObject == UI_set.TW_displayAllAccounts:
            currentFixCategory_Exp = UI_set.CB_fixExpCategory.currentText()
        elif currentTableObject == UI_set.TW_displayExpenditure:
            currentFixCategory_Exp = UI_set.CB_fixExpCategory_2.currentText()

        self.loadUserData_toTable()
        self.listenRemoveSignal()  # loadUserData_toTable() 호출 이후 "삭제" 버튼 객체가 모조리 재생성 되므로 setupUI()상에 존재하는 이벤트 대상 버튼을 갱신해줘야 한다.


    '''
        #. Name: fixCategory_Income()
        #. Feature
            (1) 실제 CB에서 선택된 데이터 저장
            (2) 저장된 데이터는 loadUserData_toFile()에서 필터링하는데 사용
    '''
    def fixCategory_Income(self):
        global currentFixCategory_Income

        if currentTableObject == UI_set.TW_displayAllAccounts:
            currentFixCategory_Income = UI_set.CB_fixIncomeCategory.currentText()
        elif currentTableObject == UI_set.TW_displayIncome:
            currentFixCategory_Income = UI_set.CB_fixIncomeCategory_2.currentText()

        self.loadUserData_toTable()
        self.listenRemoveSignal()  # loadUserData_toTable() 호출 이후 "삭제" 버튼 객체가 모조리 재생성 되므로 setupUI()상에 존재하는 이벤트 대상 버튼을 갱신해줘야 한다.

    '''
        #. Name: EnableViewDay()
        #. Feature
            (1) 켈린더 위젯 활성화, 기간설정 DateEdit 위젯 비활성화
            (2) viewSelectedWay값: VIEW_ONEDAY("일별 조회" 식별자)로 초기화 
    '''
    def EnableViewDay(self):
        global viewSelectedWay, VIEW_ONEDAY
        viewSelectedWay = VIEW_ONEDAY

        UI_set.CW_selectDay.setEnabled(1)
        UI_set.DE_periodStartDay.setEnabled(0)
        UI_set.DE_periodEndDay.setEnabled(0)

        self.loadUserData_toTable()
        self.listenRemoveSignal()  # loadUserData_toTable() 호출 이후 "삭제" 버튼 객체가 모조리 재생성 되므로 setupUI()상에 존재하는 이벤트 대상 버튼을 갱신해줘야 한다.
    '''
        #. Name: EnableViewPeriod()
        #. Feature
            (1) 켈린더 위젯 비활성화, 기간설정 DateEdit 위젯 활성화
            (2) viewSelectedWay값 초기화
    '''
    def EnableViewPeriod(self):
        global viewSelectedWay, VIEW_PREIOD
        viewSelectedWay = VIEW_PREIOD

        UI_set.CW_selectDay.setEnabled(0)
        UI_set.DE_periodStartDay.setEnabled(1)
        UI_set.DE_periodEndDay.setEnabled(1)

        self.generatePeriodList()
        self.loadUserData_toTable()
        self.listenRemoveSignal()  # loadUserData_toTable() 호출 이후 "삭제" 버튼 객체가 모조리 재생성 되므로 setupUI()상에 존재하는 이벤트 대상 버튼을 갱신해줘야 한다.

        '''
            #. Name: totDataFile()
            #. Feature
                (1) 사용자 입력 데이터 csv 파일에 저장
        '''
    def toDataFile(self):
        data={'type': addItem_typeMoney, 'date': addItem_dateMoney, 'category': addItem_categoryMoney,'place': addItem_placeMoney, 'balance': addItem_amountMoney, 'comment': addItem_commentMoney}
        df = stat.append(data, ignore_index=True)
        df.to_csv("accounts_data.csv")
   
        '''
            #. Name: getUserCategoryChart()
            #. Feature
                (1) 사용자의 카테고리별 지출 비율 출력
                <<"나의 분야 별 소비비율" 버튼을 눌렀을 때 발생>>
        '''
    def getUserCategoryChart(self):
        fig=plt.figure("나의 카테고리별 지출 비교")

        df = stat2.loc[stat2['type'] == "지출"]
        rate = df.groupby('category').sum()
        wedgeprops = {'width': 0.7, 'edgecolor': 'w', 'linewidth': 5}
        colors = ['#ff9999', '#ffc000', '#8fd9b6', '#d395d0', '#87CEFA']

        rate['balance'].plot(
            kind='pie', autopct="%1.1f%%", startangle=10, wedgeprops=wedgeprops, colors=colors
        )
        plt.title('나의 분야별 지출 비율', size=14)
        plt.axis('equal')
        plt.show()
        
        '''
            #. Name: getBothCategoryChart()
            #. Feature
                (1) 일반 가구들의 카테고리별 지출 비율을 보여줌으로써, 자신의 소비 비율 동시에 체크 가능
       '''
    def getBothCategoryChart(self):
        fig = plt.figure("통계별 지출 비교",figsize=(10, 10))
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        df = stat2.loc[stat2['type'] == "지출"]
        rate = df.groupby('category').sum()

        labels1 = [x for x in set(stat2['category'])]
        labels2 = [x for x in set(stat['category'])]
        colors = ['#ff9999', '#ffc000', '#8fd9b6', '#d395d0', '#87CEFA']
        wedgeprops = {'width': 0.7, 'edgecolor': 'w', 'linewidth': 5}

        ax1.pie(rate['balance'], autopct="%1.1f%%", startangle=10, wedgeprops=wedgeprops, colors=colors)
        ax1.legend(labels=labels1, loc='best')
        ax1.set_title('나의 분야별 소비비율')
        ax2.pie(stat['expense'], autopct="%1.1f%%", startangle=10, wedgeprops=wedgeprops, colors=colors)
        ax2.legend(labels=labels2, loc='best')
        ax2.set_title('일반 가구의 분야별 소비비율')

        plt.axis('equal')
        plt.show()
        '''
        #. Name: getSelectedDay()
        #. Feature
            (1) 실행조건 : CalendarWidget에서 사용자가 특정 날짜를 선택했을 때
            (2) QDate 형식의 사용자가 선택한 특정 날짜 정보가 담긴 객체 받아옴.
            (3) 전역변수 selectedDay_detail, selectedDay_day, selectedDay_month, selectedDay_year 에 해당 정보 저장
            (4) loadUserData_toTable()를 호출하야 테이블 출력도 갱신
        '''
    def getSelectedDay(self):
        global selectedDay, selectedDay_detail, selectedDay_day, selectedDay_month, selectedDay_year
        selectedDay = UI_set.CW_selectDay.selectedDate()
        selectedDay_detail = selectedDay.toString(QtCore.Qt.ISODate)
        selectedDay_day = selectedDay.day()
        selectedDay_month = selectedDay.month()
        selectedDay_year = selectedDay.year()

        self.loadUserData_toTable()
        self.listenRemoveSignal()  # loadUserData_toTable() 호출 이후 "삭제" 버튼 객체가 모조리 재생성 되므로 setupUI()상에 존재하는 이벤트 대상 버튼을 갱신해줘야 한다.

    '''
        #. Name: getPeriodStartDay()
        #. Feature
            (1) 실행조건 : 사용자가 DE_periodStartDay에서 날짜를 변경했을 때
            (2) QDate 형식의 사용자가 선택한 특정 날짜 정보가 담긴 객체 받아옴.
            (3) 전역변수 periodStartDay_detail, periodStartDay_day, periodStartDay_month, periodStartDay_year 에 해당 정보 저장
            (4) loadUserData_toTable()를 호출하야 테이블 출력도 갱신
    '''
    def getPeriodStartDay(self):
        global periodStartDay, periodStartDay_detail, periodStartDay_day, periodStartDay_month, periodStartDay_year
        periodStartDay = UI_set.DE_periodStartDay.date()
        periodStartDay_detail = periodStartDay.toString(QtCore.Qt.ISODate)
        periodStartDay_day = periodStartDay.day()
        periodStartDay_month = periodStartDay.month()
        periodStartDay_year = periodStartDay.year()

        self.generatePeriodList()
        self.loadUserData_toTable()
        self.listenRemoveSignal()  # loadUserData_toTable() 호출 이후 "삭제" 버튼 객체가 모조리 재생성 되므로 setupUI()상에 존재하는 이벤트 대상 버튼을 갱신해줘야 한다.

    '''
        #. Name: getPeriodEndDay()
        #. Feature
            (1) 실행조건 : 사용자가 DE_periodEndDay에서 날짜를 변경했을 떄
            (2) QDate 형식의 사용자가 선택한 특정 날짜 정보가 담긴 객체 받아옴.
            (3) 전역변수 periodEndDay_detail, periodEndDay_day, periodEndDay_month, periodEndDay_year 에 해당 정보 저장
            (4) loadUserData_toTable()를 호출하야 테이블 출력도 갱신
    '''
    def getPeriodEndDay(self):
        global periodEndDay, periodEndDay_detail, periodEndDay_day, periodEndDay_month, periodEndDay_year
        periodEndDay = UI_set.DE_periodEndDay.date()
        periodEndDay_detail = periodEndDay.toString(QtCore.Qt.ISODate)
        periodEndDay_day = periodEndDay.day()
        periodEndDay_month = periodEndDay.month()
        periodEndDay_year = periodEndDay.year()

        self.generatePeriodList()
        self.loadUserData_toTable()
        self.listenRemoveSignal()  # loadUserData_toTable() 호출 이후 "삭제" 버튼 객체가 모조리 재생성 되므로 setupUI()상에 존재하는 이벤트 대상 버튼을 갱신해줘야 한다.
        
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
            UI_set.LB_usePlace.setText("사용처")

            for i in range(len(categoryIncome)):
                UI_set.CB_categoryMoney.removeItem(0)
            UI_set.CB_categoryMoney.addItems(categoryExp)
        elif addItem_typeMoney == "수입":
            UI_set.CH_fixedMoney.setText("고정수입")
            UI_set.LB_usePlace.setText("수입처")

            for i in range(len(categoryExp)):
                UI_set.CB_categoryMoney.removeItem(0)
            UI_set.CB_categoryMoney.addItems(categoryIncome)
    '''
        #. Name: getAddItem_dateMoney()
        #. Feature
            (1) 실행조건 : 사용자가 DE_dateMoney에서 "날짜"를 변경했을 떄
            (2) 변경된 "날짜" 사항을 갱신
    '''
    def getAddItem_dateMoney(self):
        global addItem_dateMoney
        addItem_date = UI_set.DE_dateMoney.date()
        addItem_dateMoney = QtCore.QDate(addItem_date.year(), addItem_date.month(), addItem_date.day())
        addItem_dateMoney = addItem_dateMoney.toString(QtCore.Qt.ISODate)

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

        if len(addItem_placeMoney) == 0 or len(addItem_amountMoney) == 0 or addItem_categoryMoney == "지출 카테고리" or addItem_categoryMoney == "수입 카테고리":
            if len(addItem_placeMoney) == 0 or len(addItem_amountMoney) == 0:
                ErrorUI.LB_addError.setText("사용처 또는 금액 정보가 없습니다.")
                ErrorUI.LB_addError.setStyleSheet("color: red; font-size: 20px")
            else:
                ErrorUI.LB_addError.setText("")
            if addItem_categoryMoney == "지출 카테고리" or addItem_categoryMoney == "수입 카테고리":
                ErrorUI.LB_categoryError.setText("카테고리를 지정해주세요.")
                ErrorUI.LB_categoryError.setStyleSheet("color: red; font-size: 20px")
            else:
                ErrorUI.LB_categoryError.setText("")

            ErrorUI.show()
            return

        addItem_toString = list()
        addItem_toString.append(addItem_typeMoney)
        addItem_toString.append(addItem_dateMoney)
        addItem_toString.append(addItem_categoryMoney)
        addItem_toString.append(addItem_placeMoney)
        addItem_toString.append(addItem_amountMoney)
        if addItem_fixedMoney == True:
            addItem_toString.append("[고정]" + addItem_commentMoney + '\n')
        else:
            addItem_toString.append(addItem_commentMoney + '\n')
        addItem_toString = ",".join(addItem_toString)

        userDataFile.seek(0, 2)
        userDataFile.write(addItem_toString)

        self.loadUserData_toTable()
        self.listenRemoveSignal()
        self.printMoneyState()
        self.reNewData()

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
    UI_set.BT_addItem  <- 항목추가 Group에 존재하는 QPushButton

<LineEdit>
    UI_set.LE_placeMoney  <- 항목추가 Group에 존재하는 QLineEdit
    UI_set.LE_amountMoney  <- 항목추가 Group에 존재하는 QLineEdit
    UI_set.LE_commentMoney  <- 항목추가 Group에 존재하는 QLineEdit
    UI_set.LE_moneyState  <- 한달 재무현황 표시 QLineEdit
    UI_set.LE_dayState  <- 하루 재무현황 표시 QLineEdit
'''
''' in addError.ui
<LineEdit>
    ErrorUI.LB_addError  <- 항목추가 中 "사용처", "금액" 부분이 비었을 때 발생하는 에러 문구 출력하는 QLineEdit
    ErrorUI.LB_categoryError  <- 항목추가 中 "카테고리" 부분을 지정하지 않았을 때 발생하는 에러 문구 출력하는 QLineEdit
    
<PushButton>
    ErrorUI.BT_close  <- "확인" 눌렀을 때 윈도우 닫는 QPushButton
'''
''' in comparsionST.ui

<PushButton>
    ComparisonUI.BT_compMyCategory  <- "나의 카테고리별 지출 비교" QPushButton
    ComparisonUI.BT_compST  <- "통계별 지출 비교" QPushButton
'''
