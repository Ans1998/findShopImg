安装依赖
```
pip install -r requriements.txt
```
运行
```
python main.py
```
说明
主要看 readExcel 方法
```
workBook = xlrd.open_workbook(path + '\\' + '商品列表.xls')
```
修改这行代码的 '商品列表.xls'

request方法访问接口
request('6935284412918') # 固定测试
request(shop_id)

getBaiDu方法访问百度接口
getBaiDu('6903148094501', '矿泉水') # 固定测试
getBaiDu(shop_id, shop_name)
dowmloadPic方法里面的num_download变量设置下载图片数量

requestShowApi方法是访问易源的接口(收费)