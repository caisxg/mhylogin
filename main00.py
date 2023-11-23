import os
import shutil
import time

from init import ArrayObjectHandler, ProjectInfoGetter, ProxyInfo, ProxyManager
from main0_mergejson import convert_json_to_yaml
from main0_mihoyo import from_mihoyo_get_cook
from main0_miyoushe import from_miyoushe_get_cook
from utils.loghelper import log
from utils.tool import get_sleep_time, read_yaml_file

m1 = ProjectInfoGetter()
yamldata = read_yaml_file(m1.in_userinfo_file)
assert len(yamldata) >= 1, "请在 userinfo.yaml 文件中输入账号和密码"

uid = 1
log.info(f"====== 检测到共有 {len(yamldata)} 个账号 =======")
for user, info in yamldata.items():
    username = info["username"]
    password = info["password"]
    log.info(f"..... User: {user}, Username: {username}  beginning ......")

    ck1 = from_mihoyo_get_cook(uid, verbose_log=True, enable=True)
    ck2 = from_miyoushe_get_cook(uid, verbose_log=True, enable=True)
    # ck3 = from_yun_get_cook(uid, verbose_log=True, enable=True)
    data = convert_json_to_yaml(uid, verbose_log=True, username=username)

    if len(yamldata) >= 1:
        source_file = os.path.join(m1.pj_dir, "outputjson", "config_uid1.yaml")
        destination_file = os.path.join(m1.pj_dir, "outputjson", "config.yaml")
        if os.path.exists(source_file):
            shutil.copy2(source_file, destination_file)
            log.warning(f"File '{source_file}' copied to '{destination_file}'")
        else:
            log.warning(f"File '{source_file}' does not exist")

    uid += 1
    log.info(f"..... User: {user}, Username: {username}  Done ......")
    get_sleep_time(10, 15)

log.info("\n"*5)
