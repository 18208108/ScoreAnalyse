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

    data_write("各省历年高考人数.xls",numList,"高考人数")


#将数据写入excel
def data_write(path,datas,name):
    workbook = xlwt.Workbook() #创建一个新的工作簿
    sheet1 = workbook.add_sheet(name,cell_overwrite_ok=True) #在工作簿中添加一个工作表，命名为sheet1,第二个参数用于确认同一个单元格是否可以重设值，为True表明可以重新设置
    i = 0
    k = 0
    while i < 1: #指示变量，保证数据只写入一次
        for j in range(len(datas)): #表中包括2020-2012共9年的数据，采用循环使数据写入自动换行
            if j > 9 and j % 10 == 0:
                k = k + 1
                sheet1.write(k,j % 10,str(datas[j]))
            else:
                sheet1.write(k,j % 10,str(datas[j]))
        i = i + 1
        workbook.save(path)
        print("文件保存成功\n")


#获取四川历年分数线
def getSichuanScore(urlist):
    cityscore = getHtmlText(urlist)
    citysoup = BeautifulSoup(cityscore,"html.parser")
    h2 = citysoup.select("div.cjArea.tm15 > h2 > a") #筛选历年批次线所在的标签
    #Title = re.sub("[a-z0-9\/\<\.\"\>\=\:\_\ \[\]]","",str(h2)) #爬取到的内容为列表形式，通过正则方式提取出所需内容
    #Title = str(Title) #经过上一步处理后的结果为列表形式，转换为字符串形式
    h3_art = citysoup.select("div.cjArea.tm15 > h3:nth-child(2)") #文科标题
    title1 = re.sub("[a-zA-Z0-9\ \<\=\"\>\/\[\]]","",str(h3_art))
    title1 = "".join(title1)
    h3_math = citysoup.select("div.cjArea.tm15 > h3.blue.ft14.txtC.lkTit") #理科标题
    title2 = re.sub("[a-zA-Z0-9\ \<\=\"\>\/\[\]]", "", str(h3_math))
    title2 = "".join(title2)
    yearTitle = citysoup.select("tr.wkTit > th")[0:10]
    yearTitleList1 = []
    yearTitleList2 = []
    for yT in yearTitle:
        yearTitleList1.append(yT.text)
    for yT in yearTitle:
        yearTitleList2.append(yT.text)
    yearTitleList1[0] = title1 #yearTitleList中的元素为空格，将其替换为“文科”，指示当前分数所代表的意义
    yearTitleList2[0] = title2 #yearTitleList中的元素为空格，将其替换为“理科”，指示当前分数所代表的意义
    tds_one = citysoup.select("tr.c_blue > td") #爬取文科一本线分数
    tds_two = citysoup.select("tr.c_white > td") #爬取文科二本线分数
    artOne = [] #文科一本线
    artTwo = [] #文科二本线
    mathOne = [] #理科一本线
    mathTwo = [] #理科二本线
    tds_sub = []
    tds2_sub = []
    for td in tds_one:
        td_sub = re.sub("[a-z\"\=\/\<\>\\r\\t\\n\ ]","",str(td))
        tds_sub.append(td_sub)
    for td in tds_two:
        td2_sub = re.sub("[a-z\"\=\/\<\>\\r\\t\\n\ ]","",str(td))
        tds2_sub.append(td2_sub)
    for i in range(10):
        artOne.append(tds_sub[i])
        artTwo.append(tds2_sub[i])
    for i in range(10,):
        mathOne.append(tds_sub[i])
    for i in range(24,34):
        mathTwo.append(tds2_sub[i])

    #将分别获取到的一本和二本线合并成一个列表
    SiChuan = []
    for year in yearTitleList1:
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
        SiChuan.append(score2)
    data_write("四川省历年高考分数线.xls",SiChuan,"批次分数线")


def main():
    url = 'https://www.wiizii.com/yk/127994.html'
    urlist = "http://www.gaokao.com/sichuan/fsx/"
    getTestNum(url)
    getSichuanScore(urlist)


main()