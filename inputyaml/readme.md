#### 文件格式
需要四个文件, 文件名固定

- `inputyaml/userinfo.yaml` 用于记录游戏账号的密码和用户名, 可以只有一个


```yaml
user1:
  username: xxxx
  password: xxxx
user1:
  username: xxxx2
  password: xxxx2
```


- `inputyaml/captcha.yaml` 用于记录验证码的key, 这里值选择了 https://2captcha.com/enterpage 平台来处理验证码, 如果有其他平台的需求, 可以自行修改代码

```yaml
CAPTCHA2: 
  username: "xxxx"
  password: "xxxx" # 用户名和密码乱写, 有可能不同验证码平台可能会用到
  apikey: "****"
```



`inputyaml/proxyinfo.yaml`  代理ip的信息, 主要是如果挂在服务器上,有可能被识别 ip,看需要
```yaml
proxy:
  enable: true     # 是否启用代理ip
  api_url: '*****'   # 代理ip的api地址
  username: '*****' # 代理ip的用户名
  password: '*****' # 代理ip的密码
  valid_minutes: 10 # 代理ip的有效时间

```

- `inputyaml/config_template.yaml` 一个模板文件无需更改
