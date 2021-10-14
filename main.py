#coding=utf-8

import ddddocr
import requests
import json
import os
import time
import sys
import xlrd
import threading
import re


from msg_logger import logger


url = 'http://tiaoma.cnaidc.com'
headers = {'User-Agent':'Mozilla/5.0'}

path = os.path.abspath(os.path.dirname(sys.argv[0]))

# json化
def parse_json(s):
    begin = s.find('{')
    end = s.rfind('}') + 1
    return json.loads(s[begin:end])

# 请求查询商品
def request(shop_id):
    s = requests.session()

    # 获取验证码
    img_data  = s.get(url + '/index/verify.html?time=',  headers=headers).content
    with open('verification_code.png','wb') as v:
        v.write(img_data)

    # 解验证码
    ocr = ddddocr.DdddOcr()
    with open('verification_code.png', 'rb') as f:
        img_bytes = f.read()
    code = ocr.classification(img_bytes)
    logger.info('当前验证码为 ' + code)
    # 请求接口参数
    data = {"code": shop_id, "verify": code}
    resp = s.post(url + '/index/search.html',headers=headers,data=data)
    resp_json = parse_json(resp.text)
    logger.info(resp_json)
    # 判断是否查询成功
    if resp_json['msg'] == '查询成功' and resp_json['json'].get('code_img'):
        # 保存商品图片
        img_url = ''
        if resp_json['json']['code_img'].find('http') == -1:
            img_url =  url + resp_json['json']['code_img']
        else:
            img_url =  resp_json['json']['code_img']

        try:
            shop_img_data  = s.get(img_url,  headers=headers, timeout=10,).content
             # 新建目录
            mkdir(path + '\\' + shop_id)
            localtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
            # 保存图片
            with open(path + '\\' + shop_id + '\\' + str(localtime) +'.png','wb') as v:
                v.write(shop_img_data)
            logger.info(path + '\\' + shop_id + '\\' + str(localtime) +'.png')
        except requests.exceptions.ConnectionError:
            logger.info('访问图片URL出现错误！') 
       
    if resp_json['msg'] == '验证码错误':
        request(shop_id)

# 创建目录
def mkdir(path):
     # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    isExists=os.path.exists(path)
    # 判断结果
    if not isExists:
        os.makedirs(path)
        logger.info(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        logger.info(path + ' 目录已存在')
        return False

# 通过配合商品名通过百度找图片
def getBaiDu(shop_id, search_title):
    baidu_url ="http://image.baidu.com/search/flip?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1460997499750_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word={}".format(search_title)
    result = requests.get(baidu_url, headers=headers)
    dowmloadPic(result.text, shop_id)

def dowmloadPic(html, shop_id):
    # 爬取多少张
    num_download = 5
    # 新建目录
    mkdir(path + '\\' + shop_id)
    for addr in re.findall('"objURL":"(.*?)"', html, re.S):
        if num_download < 0:
            break
        logger.info('现在正在爬取URL中的地址：' + str(addr))
        try:
            pic = requests.get(addr, timeout=10, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.info('您当前的URL出现错误！')
            continue
        localtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
        fn = open(path + '\\' + shop_id + '\\' + str(localtime) +'.png','wb')
        fn.write(pic.content)
        fn.close()

        # drop_wartermark(path + '\\' + shop_id + '\\' + str(localtime) +'.png', path + '\\' + shop_id + '\\' + str(localtime) +'-0.png')

        num_download = num_download - 1
        logger.info(path + '\\' + shop_id + '\\' + str(localtime) +'.png')

# 去水印
def drop_wartermark(path):
    print('因为找不到合适的库, 就没有对接')

# 调用万维容源api
def requestShowApi(shop_id):
    shop_time = int(time.time())
    appid = '791873'
    sign = 'b84e7b3717df4f18a4f8380707ef6663'
    showapi_url = 'https://route.showapi.com/66-22?code='+shop_id+'&showapi_appid='+appid+'&showapi_timestamp='+str(shop_time)+'&showapi_sign='+sign
    resp = s.get(showapi_url, headers=headers)
    resp_json = parse_json(resp.text)
    logger.info(resp_json)
    print(resp_json['showapi_res_body'])
     # 判断是否查询成功
    if str(resp_json['showapi_res_code']) == '0' and resp_json['showapi_res_body'].get('img'):
        # 保存商品图片
        img_url = resp_json['showapi_res_body']['img']
        shop_img_data  = s.get(img_url,  headers=headers).content
        # 新建目录
        mkdir(path + '\\' + shop_id)
        localtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
        # 保存图片
        with open(path + '\\' + shop_id + '\\' + str(localtime) +'.png','wb') as v:
            v.write(shop_img_data)
        logger.info(path + '\\' + shop_id + '\\' + str(localtime) +'.png')


def run(sheet1_content1, start_num, end_num):
    for i in range(start_num, end_num):
        rows = sheet1_content1.cell(i, 2).value
        rows_str = int(rows)
        shop_id = str(rows_str)
        # print(shop_id)
        shop_name = sheet1_content1.cell(i, 0).value
        if shop_id.startswith('6'):
            if len(shop_id) == 13 or len(shop_id) == 8:
                logger.info('开始执行 ' + str(i) + ' 个' + ' 商品id ' + shop_id + ' 商品名 ' + shop_name)
                
                # 从哪里中断就从哪里开始执行
                # if i >= 370:
                    # request('6935284412918')
                    # request(shop_id)

                # request('6935284412918')
                # request(shop_id)
            
                # getBaiDu('6903148094501', '矿泉水')
                getBaiDu(shop_id, shop_name)

                # requestShowApi('6956367338666')
                # requestShowApi(shop_id)
                # time.sleep(0.5)

# 读取exec进行循环访问
def readExcel():
    # 打开文件
    workBook = xlrd.open_workbook(path + '\\' + '商品列表.xls')
    sheet1_content1 = workBook.sheet_by_index(0)
    # 获取总行数
    nrows = sheet1_content1.nrows
    work_count = 5
    num = int(nrows / work_count)
    start_num = 1
    end_num = 0

    end_num = 600

    run(sheet1_content1, start_num, end_num)

    # for i in range(work_count):
    #     if i == 0:
    #         start_num = 1
    #         end_num = num
    #         # print(nrows, i, num, start_num, end_num)
    #         thread_seckill = threading.Thread(target=run, args=(sheet1_content1, start_num, end_num))
    #         thread_seckill.start()
    #     else:
    #         start_num = end_num
    #         end_num = end_num + num
    #         # print(nrows, i, num, start_num, end_num)
    #         thread_seckill = threading.Thread(target=run, args=(sheet1_content1, start_num, end_num))
    #         thread_seckill.start()


def t():
    workBook = xlrd.open_workbook(path + '\\' + '商品列表.xls')
    sheet1_content1 = workBook.sheet_by_index(0)
    # 获取总行数
    nrows = sheet1_content1.nrows
    run(sheet1_content1, 1, nrows)

if __name__ == '__main__':
    readExcel()