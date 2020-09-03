from bs4 import BeautifulSoup
import requests
import xlwt #用于将数据写入excel文件
import pandas
import re

#获取各省市历年高考人数
def getTestNum(url):
    r = requests.get(url)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text,"html.parser")
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

    data_write("各省历年高考人数.xls",numList)


#将数据写入excel
def data_write(path,datas):
    workbook = xlwt.Workbook() #创建一个新的工作簿
    sheet1 = workbook.add_sheet(u'sheet1',cell_overwrite_ok=True) #在工作簿中添加一个工作表，命名为sheet1,第二个参数用于确认同一个单元格是否可以重设值，为True表明可以重新设置
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






def main():
    url = 'https://www.wiizii.com/yk/127994.html'
    getTestNum(url)


main()