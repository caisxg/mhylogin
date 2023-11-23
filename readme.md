## 环境准备

#### 使用之前

- 安装依赖

```bash
conda create -n mihoyo python=3.10
conda activate mihoyo
pip install -r requirements.txt

## 如果需要 设置代理, 请自行购买,
## 如果不设置代理, 可能获取不到 cookie, 比如腾讯云的 ip 可能被识别, 导致获取不到 cookie
## 可以按照需求自己选择 requests 或者 httpx

```
#### 准备输入文件
```bash
inputyaml/captcha.yaml   # 验证码的key 文件
inputyaml/config_template.yaml  # 模板文件, 来自Womsxd/MihoyoBBSTools模板, 主要根据模板自动生成 outputjson/config.yaml 文件.该文件用于Womsxd/MihoyoBBSTools
inputyaml/proxyinfo.yaml  #代理文件
inputyaml/userinfo.yaml   # 用户信息文件, 
```

#### 功能

主要根据[网址](https://github.com/Womsxd/MihoyoBBSTools): 获取米游社和通行证个网站的 cookie, 并保存到 outputjson/user_cookies.json 中

- 详细的功能, 如下

#### 记录

```bash
# 所有的 cookie 都输出到: outputjson/user_cookies.json

# 主文件夹新增文件
./main0_mihoyo.py   #用于登录米哈游
./main0_miyoushe.py  #用于登录米游社
./main0_mergeck.py  # 对上面两个网站的 cookie 进行合并,并输出

./js/*          # 存放 js 文件, 主要是加密函数
./logs_mhy/*         # 存放日志文件
./outputjson/*  # 存放输出的 json 文件
./utils/*       # 存放工具函数
./inputyaml/*    # 存放配置文件

```

- 详细的文件说明

```bash
## 不过由于 js 可能会读取浏览器信息, 这里暂时应该用不到, 直接先用 python 来实现
./js/fake_information.js   # 利用 js 来产生 uuid 等设备信息
./js/enraspwbyjs.js   # 产生加密公钥的 (当然可以直接扣出来, 即 enrsapw.py) 效果是一样的

enrsapw.py  # 等同于 enraspwbyjs.js, (不过这个文件的包不好安装)


./logs_mhy/*.log # 生成的日志文件


./outputjson/user_cookies.json  # 存放 cookie 的文件, 用于后续的使用
./outputjson/proxy_info.json  # 存放代理的信息, 用于决定是否更新代理
./outputjson/config.yaml.example  # 利用这个文件夹下的 json 文件, 根据这个配置模板, 生成 config.yaml 文件


./utils/handl_captcha.py  # 用于处理验证码, 不过暂时没遇到过验证码, 所以没用到,
./utils/loghelper.py  # 用于记录日志的工具函数
./utils/tools.py  # 工具函数
./utils/UAinfo.py  # 根据UA获取一些设备信息



./enrsapw.py  # 产生加密公钥的 (当然可以直接扣出来, 即 enraspwbyjs.js) 效果是一样的
./init.py # 初始化几个类
./main0_mihoyo.py   #用于登录米哈游
./main0_miyoushe.py  #用于登录米游社
./main0_mergeck.py  # 对上面两个网站的 cookie 进行合并,并输出
./main03_yun.py   # 获取云原神的 cookie, ,并输出
./myrequest.py  # 封装了 requests 和 httpx, 用于请求网页, 根据需要选择(封装的不好,能用就行)

shangcaptcha.py  #处理上层的验证码,这里用不到

```

- UA 信息

```bash
Mozilla/5.0 (Linux; U; Android 13; zh-cn; M2102J2SC Build/TKQ1.220829.002)
      AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/100.0.4896.127 Mobile
      Safari/537.36 XiaoMi/MiuiBrowser/17.6.100509 swan-mibrowser
```

#### 注意

```
如果遇到短信登录, 可以重复多次登录, 有些时候会跳出短信而采用验证码登录, 这个首次登录就算成功了, 以后就不会再出现短信登录了
```
