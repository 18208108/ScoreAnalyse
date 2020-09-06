from bs4 import BeautifulSoup
import requests
import xlwt #用于将数据写入excel文件
import pandas
import re

#获取网页内容
def getHtmlText(url):
    r = requests.get(url)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text


#获取各省市历年高考人数
def getTestNum(url):
    r = getHtmlText(url)
    soup = BeautifulSoup(r,"html.parser")
    #yearList = soup.find_all("tr",{"class":"firstRow"})#爬取年份
    yearList = [] #用于存储年份
    years = soup.select("td")[0:10] #提取表格中所有的年份
    for year in years:
        year = list(year)#years本身为列表类型，但将years中的每个元素转换为列表类型，可去除首尾的<td>标签
        for i in year:#每个year是只包含一个元素的列表，遍历列表，去除最后的汉字“年”
            i = i.replace("年","")
            yearList.append(i)#将处理后的每个年份添加到列表中，以便后续作为字典的键使用

    countryList = []#用于存储全国历年人数
    numCountry = soup.select("td")[10:]
    #获取为空的数值在列表中的位置
    tmp = [] #用于存储为空的元素在列表中的位置
    tag = 0
    for each in numCountry:
        if str(each) == "<td></td>": #如果该位置元素为空
            numCountry.remove(numCountry[tag])
            numCountry.insert(tag,' ')
            tmp.append(tag)
        tag += 1

    for numc in numCountry:
        numc = list(numc)
        #对全国的历年数据进行处理，去除数据后面的箭头和汉字“万”
        for j in numc:
            j = j.replace("↑","")
            j = j.replace("↓","")
            countryList.append(j)
    numList = [] #将爬取到的所有数据添加到同一个列表中
    for year in yearList:
        numList.append(year)
    for numc in countryList:
        numList.append(numc)

    data_write("高考成绩分析/各省历年高考人数.xls",numList,"高考人数",10)


#将数据写入excel
def data_write(path,datas,name,times):
    workbook = xlwt.Workbook() #创建一个新的工作簿
    sheet1 = workbook.add_sheet(name,cell_overwrite_ok=True) #在工作簿中添加一个工作表，命名为sheet1,第二个参数用于确认同一个单元格是否可以重设值，为True表明可以重新设置
    i = 0
    k = 0
    while i < 1: #指示变量，保证数据只写入一次
        for j in range(len(datas)): #表中包括2020-2012共9年的数据，采用循环使数据写入自动换行
            if j > (times - 1) and j % times == 0:
                k = k + 1
                sheet1.write(k,j % times,str(datas[j]))
            else:
                sheet1.write(k,j % times,str(datas[j]))
        i = i + 1
        workbook.save(path)
        print("文件保存成功\n")


#爬取文科理科标题
def getSubject(soup,locate):
    title_sub = soup.select(locate)
    title = re.sub("[a-zA-Z0-9\ \<\=\"\>\/\[\]]","",str(title_sub))
    title = "".join(title)
    return title


#爬取年份标题
def getYear(yearTitle,h3):
    yearTitleList = []
    for yT in yearTitle:
        if isinstance(yT,str): #如果传入的数据类型为字符串，则直接加入列表中
            yearTitleList.append(yT)
        else: #否则转换为字符串类型再加入
            yearTitleList.append(yT.text)
    yearTitleList[0] = h3
    return yearTitleList


#对爬取到的分数进行格式处理
def getFormatScore(soup,string):
    tds = soup.select(string)
    tds_sub = []
    for td in tds:
        td_sub = re.sub("[a-z\"\=\/\<\>\\r\\t\\n\\\ ]","",str(td))
        tds_sub.append(td_sub)
    return tds_sub


#将所有数据合并为一个列表
def getTotalList(yearTitleList1,yearTitleList2,artOne,artTwo,mathOne,mathTwo):
    total = []
    for year in yearTitleList1:
        total.append(year)
    for score1 in artOne:
        total.append(score1)
    for score2 in artTwo:
        total.append(score2)
    for year in yearTitleList2:
        total.append(year)
    for score1 in mathOne:
        total.append(score1)
    for score2 in mathTwo:
        total.append(score2)
    return total


#获取不分文理科分数线
def getScore(soup,num,time_set,h3):
    h2 = soup.select("div.cjArea.tm15 > h2") #获取包含省市名称的标题
    Title = re.sub("[a-zA-Z0-9\[\]\"\ \/:=_<>.]","",str(h2))
    #h3 = soup.select("div.cjArea.tm15 > h3:nth-child(2)")
    filetitle = re.sub("[a-zA-Z0-9\<\>\ \"\/\=\[\]]","",str(h3)) #获取文理不分科标题
    '''tbody = soup.select("div.cjArea.tm15 > table:nth-child(3) > tbody")[0].text
    time = str(tbody).split("\n")
    time_set = list(set(time))
    time_set.sort(key=time.index)'''
    data_write("高考成绩分析/" + Title + filetitle + ".xls", time_set, "分数线", num)



#获取四川历年分数线
def getSichuanScore(urlSi):
    Siscore = getHtmlText(urlSi)
    citysoup = BeautifulSoup(Siscore,"html.parser")
    #h2 = citysoup.select("div.cjArea.tm15 > h2 > a") #筛选历年批次线所在的标签
    #Title = re.sub("[a-z0-9\/\<\.\"\>\=\:\_\ \[\]]","",str(h2)) #爬取到的内容为列表形式，通过正则方式提取出所需内容
    #Title = str(Title) #经过上一步处理后的结果为列表形式，转换为字符串形式
    h3_art = getSubject(citysoup,"div.cjArea.tm15 > h3:nth-child(2)") #文科标题
    h3_math = getSubject(citysoup,"div.cjArea.tm15 > h3.blue.ft14.txtC.lkTit") #理科标题
    '''h3_art = citysoup.select("div.cjArea.tm15 > h3:nth-child(2)") #文科标题
    title1 = re.sub("[a-zA-Z0-9\ \<\=\"\>\/\[\]]","",str(h3_art))
    title1 = "".join(title1)
    h3_math = citysoup.select("div.cjArea.tm15 > h3.blue.ft14.txtC.lkTit") #理科标题
    title2 = re.sub("[a-zA-Z0-9\ \<\=\"\>\/\[\]]", "", str(h3_math))
    title2 = "".join(title2)'''
    yearTitle = citysoup.select("tr.wkTit > th")[0:10]
    yearTitleList1 = getYear(yearTitle,h3_art) #yearTitleList中的元素为空格，将其替换为“文科”，指示当前分数所代表的意义
    yearTitleList2 = getYear(yearTitle,h3_math) #yearTitleList中的元素为空格，将其替换为“理科”，指示当前分数所代表的意义
    '''yearTitleList1 = []
    yearTitleList2 = []
    for yT in yearTitle:
        yearTitleList1.append(yT.text)
    for yT in yearTitle:
        yearTitleList2.append(yT.text)
    yearTitleList1[0] = h3_art #yearTitleList中的元素为空格，将其替换为“文科”，指示当前分数所代表的意义
    yearTitleList2[0] = h3_math #yearTitleList中的元素为空格，将其替换为“理科”，指示当前分数所代表的意义'''
    '''tds_one = citysoup.select("tr.c_blue > td") #爬取一本线分数
    tds_two = citysoup.select("tr.c_white > td") #爬取二本线分数'''
    artOne = [] #文科一本线
    artTwo = [] #文科二本线
    mathOne = [] #理科一本线
    mathTwo = [] #理科二本线
    #对数据进行处理后将其存入新的数据，方便后续使用
    tds_sub = getFormatScore(citysoup,"tr.c_blue > td") #获取格式化的一本分数线
    tds2_sub = getFormatScore(citysoup,"tr.c_white > td") #获取格式化的二本分数线
    '''for td in tds_one:
        td_sub = re.sub("[a-z\"\=\/\<\>\\r\\t\\n\ ]","",str(td))
        tds_sub.append(td_sub)
    for td in tds_two:
        td2_sub = re.sub("[a-z\"\=\/\<\>\\r\\t\\n\ ]","",str(td))
        tds2_sub.append(td2_sub)'''
    for i in range(10):
        artOne.append(tds_sub[i])
        artTwo.append(tds2_sub[i])
    for i in range(10,):
        mathOne.append(tds_sub[i])
    for i in range(24,34):
        mathTwo.append(tds2_sub[i])

    #将分别获取到的一本和二本线合并成一个列表
    SiChuan = getTotalList(yearTitleList1,yearTitleList2,artOne,artTwo,mathOne,mathTwo)
    '''for year in yearTitleList1:
        SiChuan.append(year)
    for score1 in artOne:
        SiChuan.append(score1)
    for score2 in artTwo:
        SiChuan.append(score2)
    for year in yearTitleList2:
        SiChuan.append(year)
    for score1 in mathOne:
        SiChuan.append(score1)
    for score2 in mathTwo:
        SiChuan.append(score2)'''
    data_write("高考成绩分析/四川省历年高考分数线.xls",SiChuan,"批次分数线",10)


#获取北京历年分数线
def getBeijingScore(urlBei):
    BeiScore = getHtmlText(urlBei)
    beisoup = BeautifulSoup(BeiScore,"html.parser")
    h3 = beisoup.select("div.cjArea.tm15 > h3:nth-child(2)")
    tbody = beisoup.select("div.cjArea.tm15 > table:nth-child(3) > tbody")[0].text
    time = str(tbody).split("\n")
    time_set = list(set(time))
    time_set.sort(key=time.index)
    getScore(beisoup,2,time_set,h3)
    #h3 = beisoup.select("div.cjArea.tm15 > h3:nth-child(2)")
    #filetitle = re.sub("[a-zA-Z0-9\<\>\ \"\/\=\[\]]","",str(h3)) #获取第一个分类，不分文理
    '''path = "北京高考分数线" + filetitle + ".xls"
    name = "分数线"'''
    '''tbody = beisoup.select("div.cjArea.tm15 > table:nth-child(3) > tbody")[0].text
    time = str(tbody).split("\n")
    time_set = list(set(time))
    time_set.sort(key=time.index)'''
    #time_set = getScore(beisoup)
    #data_write("高考成绩分析/北京高考分数线" + filetitle + ".xls",time_set,"分数线",2)
    '''workbook = xlwt.Workbook()  # 创建一个新的工作簿
    sheet1 = workbook.add_sheet(name,cell_overwrite_ok=True)  # 在工作簿中添加一个工作表，命名为sheet1,第二个参数用于确认同一个单元格是否可以重设值，为True表明可以重新设置
    i = 0
    k = 0
    while i < 1:  # 指示变量，保证数据只写入一次
        for j in range(len(time_set)):  # 表中包括2020-2012共9年的数据，采用循环使数据写入自动换行
            if j > 1 and j % 2 == 0:
                k = k + 1
                sheet1.write(k, j % 2, str(time_set[j]))
            else:
                sheet1.write(k, j % 2, str(time_set[j]))
        i = i + 1
        workbook.save(path)
        print("文件保存成功\n")'''

    #爬取文科和理科历年数据
    h3_art = getSubject(beisoup,"div.cjArea.tm15 > h3:nth-child(4)") #文科标题
    h3_math = getSubject(beisoup,"div.cjArea.tm15 > h3.blue.ft14.txtC.lkTit") #理科标题
    yearTitle = beisoup.select("tr.wkTit > th")[2:11]
    yearTitleList1 = getYear(yearTitle,h3_art) #文科成绩年份列表
    yearTitleList2 = getYear(yearTitle,h3_math) #理科成绩年份列表
    '''tds_one = beisoup.select("tr.c_blue > td") #一本线
    tds_two = beisoup.select("tr.c_white > td") #二本分数线'''
    tds_sub = getFormatScore(beisoup,"tr.c_blue > td") #获取格式化的一本线
    tds2_sub = getFormatScore(beisoup,"tr.c_white > td") #获取格式化的二本线
    artOne = []  # 文科一本线
    artTwo = []  # 文科二本线
    mathOne = []  # 理科一本线
    mathTwo = []  # 理科二本线
    for i in range(9):
        artOne.append(tds_sub[i])
    for i in range(48,57):
        mathOne.append(tds_sub[i])
    for j in range(9):
        artTwo.append(tds2_sub[j])
    for j in range(48,57):
        mathTwo.append(tds2_sub[j])
    BeiJing = getTotalList(yearTitleList1,yearTitleList2,artOne,artTwo,mathOne,mathTwo)
    data_write("高考成绩分析/北京市历年高考分数线.xls",BeiJing,"批次分数线",9)


#获取天津历年分数线
def getTianjingScore(urlTian):
    TianScore = getHtmlText(urlTian)
    tiansoup = BeautifulSoup(TianScore,"html.parser")
    h3 = tiansoup.select("div.cjArea.tm15 > h3:nth-child(2)")
    tbody = tiansoup.select("div.cjArea.tm15 > table:nth-child(3) > tbody")[0].text
    time = str(tbody).split("\n")
    time_set = list(set(time))
    time_set.sort(key=time.index)
    getScore(tiansoup,2,time_set,h3) #爬取文理不分科数据

    #爬取文科和理科数据
    h3_art = getSubject(tiansoup, "div.cjArea.tm15 > h3:nth-child(4)")  # 文科标题
    h3_math = getSubject(tiansoup, "div.cjArea.tm15 > h3.blue.ft14.txtC.lkTit")  # 理科标题
    yearTitle = tiansoup.select("tr.wkTit > th")[2:12]
    yearTitleList1 = getYear(yearTitle, h3_art)  # 文科成绩年份列表
    yearTitleList2 = getYear(yearTitle, h3_math)  # 理科成绩年份列表
    '''tds_one = tiansoup.select("tr.c_blue > td")  # 爬取一本线分数
    tds_two = tiansoup.select("tr.c_white > td")  # 爬取二本线分数'''
    tds_sub = getFormatScore(tiansoup,"tr.c_blue > td")  # 获取格式化的一本线
    tds2_sub = getFormatScore(tiansoup,"tr.c_white > td")  # 获取格式化的二本线
    artOne = []  # 文科一本线
    artTwo = []  # 文科二本线
    mathOne = []  # 理科一本线
    mathTwo = []  # 理科二本线
    tds2_sub[0] = " " #由于存在“本科A，B段”，多一个空格，所以对列表元素进行修改
    for i in range(10):
        artOne.append(tds_sub[i])
        artTwo.append(tds2_sub[i])
    for j in range(13,23):
        mathOne.append(tds_sub[j])
        mathTwo.append(tds2_sub[j])
    TianJin = getTotalList(yearTitleList1, yearTitleList2, artOne, artTwo, mathOne, mathTwo)
    data_write("高考成绩分析/天津市历年高考分数线.xls", TianJin, "批次分数线", 10)


#获取江苏历年分数线
def getJiangsuScore(urlSu):
    SuScore = getHtmlText(urlSu)
    susoup = BeautifulSoup(SuScore,"html.parser")
    h3_art = getSubject(susoup, "div.cjArea.tm15 > h3:nth-child(4)")  # 文科标题
    h3_math = getSubject(susoup, "div.cjArea.tm15 > h3.blue.ft14.txtC.lkTit")  # 理科标题
    tds_sub = getFormatScore(susoup, "tr.c_blue > td")  # 获取格式化的一本线
    tds2_sub = getFormatScore(susoup, "tr.c_white > td")  # 获取格式化的二本线
    yearTitle = susoup.select("tr.wkTit > th")[0:10]
    yearTitleList1 = getYear(yearTitle, h3_art)  # 文科成绩年份列表
    yearTitleList2 = getYear(yearTitle, h3_math)  # 理科成绩年份列表
    artOne = []  # 文科一本线
    artTwo = []  # 文科二本线
    mathOne = []  # 理科一本线
    mathTwo = []  # 理科二本线
    for i in range(10):
        artOne.append(tds_sub[i])
        artTwo.append(tds2_sub[i])
    for j in range(12,22):
        mathOne.append(tds_sub[j])
        mathTwo.append(tds2_sub[j])
    JiangSu = getTotalList(yearTitleList1, yearTitleList2, artOne, artTwo, mathOne, mathTwo)
    data_write("高考成绩分析/江苏省历年高考分数线.xls", JiangSu, "批次分数线", 10)


#获取浙江省历年分数线
def getZhejiangScore(urlZhe):
    ZheScore = getHtmlText(urlZhe)
    zhesoup = BeautifulSoup(ZheScore,"html.parser")
    '''h3_art = getSubject(zhesoup, "div.cjArea.tm15 > h3:nth-child(4)")  # 文科标题
    h3_math = getSubject(zhesoup, "div.cjArea.tm15 > h3.blue.ft14.txtC.lkTit")  # 理科标题'''
    h3 = zhesoup.find_all("h3",attrs={"class":"txtC"})
    h3_art = h3[1].text
    h3_math = h3[2].text
    tds_sub = getFormatScore(zhesoup, "tr.c_blue > td")  # 获取格式化的一本线
    tds2_sub = getFormatScore(zhesoup, "tr.c_white > td")  # 获取格式化的二本线

    #爬取文理不分科数据
    h3 = zhesoup.select("div.cjArea.tm15 > h3:nth-child(2)")
    tbody = zhesoup.select("div.cjArea.tm15 > table")[0].text
    time = str(tbody).split("\n")
    time_year = list(set(time))
    time_year.sort(key=time.index)
    time_set = []
    for i in range(5):
        time_set.append(time_year[i])
    for i in range(5):
        time_set.append(tds_sub[i])
    for i in range(5):
        time_set.append(tds2_sub[i])
    for i in range(5,10):
        time_set.append(tds_sub[i])
    getScore(zhesoup,5,time_set,h3)

    #爬取文理分科数据
    year_sub = zhesoup.find_all("tr",attrs={"class":"wkTit"})[1].text #因为网页中包含多个相同属性的tr,所以不能使用select
    time_sub = str(year_sub).split("\n") #对数据进行处理，拆分字符串，存入数组
    time_year_sub = list(set(time_sub))
    time_year_sub.sort(key=time_sub.index)
    yearTitle = [] #将所需选取的年份存入新的列表，方便后续使用
    for i in range(6):
        yearTitle.append(time_year_sub[i])
    yearTitleList1 = getYear(yearTitle, h3_art)  # 文科成绩年份列表
    yearTitleList2 = getYear(yearTitle, h3_math)  # 理科成绩年份列表
    artOne = []  # 文科一本线
    artTwo = []  # 文科二本线
    mathOne = []  # 理科一本线
    mathTwo = []  # 理科二本线
    for i in range(10,16):
        artOne.append(tds_sub[i])
    for i in range(5,11):
        artTwo.append(tds2_sub[i])
    for j in range(30,36):
        mathOne.append(tds_sub[j])
    for j in range(25,31):
        mathTwo.append(tds2_sub[j])
    ZheJiang = getTotalList(yearTitleList1, yearTitleList2, artOne, artTwo, mathOne, mathTwo)
    data_write("高考成绩分析/浙江省历年高考分数线.xls", ZheJiang, "批次分数线", 6)


#获取重庆历年高考分数线
def getChongqingScore(urlChong):
    ChongScore = getHtmlText(urlChong)
    chongsoup = BeautifulSoup(ChongScore,"html.parser")
    h3_art = getSubject(chongsoup, "div.cjArea.tm15 > h3:nth-child(4)")  # 文科标题
    h3_math = getSubject(chongsoup, "div.cjArea.tm15 > h3.blue.ft14.txtC.lkTit")  # 理科标题
    tds_sub = getFormatScore(chongsoup, "tr.c_blue > td")  # 获取格式化的一本线
    tds2_sub = getFormatScore(chongsoup, "tr.c_white > td")  # 获取格式化的二本线
    yearTitle = chongsoup.select("tr.wkTit > th")[0:10]
    yearTitleList1 = getYear(yearTitle, h3_art)  # 文科成绩年份列表
    yearTitleList2 = getYear(yearTitle, h3_math)  # 理科成绩年份列表
    artOne = []  # 文科一本线
    artTwo = []  # 文科二本线
    mathOne = []  # 理科一本线
    mathTwo = []  # 理科二本线
    for i in range(10):
        artOne.append(tds_sub[i])
        artTwo.append(tds2_sub[i])
    for j in range(36, 46):
        mathOne.append(tds_sub[j])
        mathTwo.append(tds2_sub[j])
    ChongQing = getTotalList(yearTitleList1, yearTitleList2, artOne, artTwo, mathOne, mathTwo)
    data_write("高考成绩分析/重庆市历年高考分数线.xls", ChongQing, "批次分数线", 10)


#爬取广东历年分数线
def getGuangdongScore(urlDong):
    GuangScore = getHtmlText(urlDong)
    dongsoup = BeautifulSoup(GuangScore,"html.parser")
    h3_art = getSubject(dongsoup, "div.cjArea.tm15 > h3.blue.ft14.txtC")[0:2]  # 文科标题
    h3_math = getSubject(dongsoup, "div.cjArea.tm15 > h3.lkTit")  # 理科标题

    #爬取不划分一二本年份的分数线
    tbody_art = dongsoup.select("div.cjArea.tm15 > table")[0].text
    time_art = str(tbody_art).split("\n")
    time_year_art = list(set(time_art))
    time_year_art.sort(key=time_art.index) #获取到的time_year中包含文科不划分一二本的年份和分数线
    getScore(dongsoup,4,time_year_art,h3_art)
    tbody_math_score = dongsoup.select("div.cjArea.tm15 > table:nth-child(6) > tbody")[0].text
    time_math = str(tbody_math_score).split("\n")
    time_year_math = list(set(time_math))
    time_year_math.sort(key=time_math.index) #包含理科不划分一二本的年份和分数线
    getScore(dongsoup,4,time_year_math,h3_math)

    #爬取文理分科数据
    tds_sub = getFormatScore(dongsoup, "tr.c_blue > td")  # 获取格式化的一本线
    tds2_sub = getFormatScore(dongsoup, "tr.c_white > td")  # 获取格式化的二本线
    yeartitle = dongsoup.find_all("tr",attrs={"class":"wkTit"})[1]
    yearTitle = []
    for i in yeartitle:
        print(i)
        yearTitle.append(i)
    #print(yearTitle)
    yearTitleList1 = getYear(yearTitle, h3_art)  # 文科成绩年份列表
    yearTitleList2 = getYear(yearTitle, h3_math)  # 理科成绩年份列表
    print(yearTitle)


def main():
    url = 'https://www.wiizii.com/yk/127994.html' #全国高考人数数据
    urlSi = "http://www.gaokao.com/sichuan/fsx/" #四川数据
    urlBei = "http://www.gaokao.com/beijing/fsx/" #北京数据
    urlTian = "http://www.gaokao.com/tianjin/fsx/" #天津数据
    urlSu = "http://www.gaokao.com/jiangsu/fsx/" #江苏数据
    urlZhe = "http://www.gaokao.com/zhejiang/fsx/" #浙江数据
    urlChong = "http://www.gaokao.com/chongqing/fsx/" #重庆数据
    urlDong = "http://www.gaokao.com/guangdong/fsx/" #广东数据
    getTestNum(url)
    getSichuanScore(urlSi)
    getBeijingScore(urlBei)
    getTianjingScore(urlTian)
    getJiangsuScore(urlSu)
    getZhejiangScore(urlZhe)
    getChongqingScore(urlChong)
    getGuangdongScore(urlDong)


main()