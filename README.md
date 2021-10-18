# 安装依赖
```
pip install -r requriements.txt
```
# 运行
```
python main.py
```
# 说明
主要看 readExcel 方法
```
workBook = xlrd.open_workbook(path + '\\' + '商品列表.xls')
# 修改这行代码的 '商品列表.xls'

# requestT1通过（tiaoma.cnaidc.com）查询商品信息
# requestT1('6935284412918') # 固定测试
requestT1(shop_id)

# getBaiDu方法访问百度接口
# getBaiDu('6903148094501', '矿泉水') # 固定测试
getBaiDu(shop_id, shop_name)
# dowmloadPic 方法里面的 num_download 变量 设置下载图片数量

# requestT2 中国物品编码
# getBaiDu('6903148094501') # 固定测试 
requestT2(shop_id)
'''
使用方法
 1.先来到中国物品编码（http://www.ancc.org.cn/Service/queryTools/Internal.aspx）
 2.填写验证码
 3.网络抓包拿到cookie
 4.填写进该项目 requestT2 里面的 headers['Cookie'] = 'ASP.NET_SessionId=blgmvuf5s54mtz45si25rga2' # 需要手动获取
 '''
 ```