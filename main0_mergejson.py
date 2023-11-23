"""
合并 ck, 从已知的 cookie_file 中读取 cookie, 并写入到 config.yaml 中
并做一些检查,
"""
import json
import os
import sys
from pathlib import Path

from init import ArrayObjectHandler, ProjectInfoGetter, ProxyInfo
from utils.loghelper import log
from utils.tool import read_json_file, read_yaml_file, write_dict_to_yaml


###########################
# 循环读取账号和密码
# uid = 1  #表示第一个账号
def convert_json_to_yaml(uid, verbose_log=True, username=None, out_yaml_file=None):
    m1 = ProjectInfoGetter()

    alldata = ArrayObjectHandler(filename=m1.op_cookie_file)
    jdata = alldata.select_by_uid(uid)
    try:
        newdata = {
            "cookie_token_v2": jdata["miyoushe"]["cookie_token_v2"],
            "account_mid_v2": jdata["miyoushe"]["account_mid_v2"],
            "account_id_v2": jdata["miyoushe"]["account_id_v2"],
            "ltoken_v2": jdata["miyoushe"]["ltoken_v2"],
            "ltmid_v2": jdata["miyoushe"]["ltmid_v2"],
            "ltuid_v2": jdata["miyoushe"]["ltuid_v2"],
            "_MHYUUID": jdata["miyoushe"]["_MHYUUID"],
            "DEVICEFP_SEED_ID": jdata["miyoushe"]["DEVICEFP_SEED_ID"],
            "DEVICEFP_SEED_TIME": jdata["miyoushe"]["DEVICEFP_SEED_TIME"],
            "DEVICEFP": jdata["miyoushe"]["DEVICEFP"],
            "login_uid": jdata["mihoyo"]["login_uid"],
            "login_ticket": jdata["mihoyo"]["login_ticket"],
        }
    except:
        log.error("cookie有问题, 请检查")
        raise Exception("cookie有问题, 请检查")

    newdata_str = "; ".join([f"{key}={str(value)}" for key, value in newdata.items()])

    ####################################################
    ### 下面依赖于 outputjson/config.yaml 文件 #####################
    ### 该文件拷贝自 https://github.com/Womsxd/MihoyoBBSTools/blob/master/config/config.yaml.example
    ### 主要是构造一个 config.yaml 文件, 用于后续的操作
    ### 根据 inputyaml/config_template.yaml 文件的内容, 填充其字段,该文件来自 inputyaml/config.yaml.example
    ##
    config_file = os.path.join(m1.pj_dir, "inputyaml", "config_template.yaml")
    yamldata = read_yaml_file(config_file)
    yamldata["account"]["cookie"] = newdata_str

    ### 并检查一下 -- 根据自己的需要修改
    if not yamldata["enable"]:
        yamldata["enable"] = True

    if not yamldata["games"]["cn"]["enable"]:
        yamldata["games"]["cn"]["enable"] = True
    if not yamldata["games"]["cn"]["genshin"]["auto_checkin"]:
        yamldata["games"]["cn"]["genshin"]["auto_checkin"] = True

    yamldata["account"]["login_ticket"] = ""
    yamldata["account"]["stuid"] = ""
    yamldata["account"]["stoken"] = ""

    ########### 检查是否有 yunys 配置 #######
    if "yunys" in jdata and jdata["yunys"]:
        # 不弄云原神
        yamldata["cloud_games"]["genshin"]["enable"] = False  # True
        yamldata["cloud_games"]["genshin"]["token"] = ""  # jdata["yunys"]["X-Rpc-Combo_token"]
    else:
        yamldata["cloud_games"]["genshin"]["enable"] = False
        yamldata["cloud_games"]["genshin"]["token"] = ""
    if not out_yaml_file:
        # 输出文件
        out_yaml_file = os.path.join(m1.pj_dir, "outputjson", f"config_uid{uid}.yaml")

    write_dict_to_yaml(out_yaml_file, yamldata)
    # 读取原始 YAML 文件
    if not username:
        comment = f"# 这是账号, uid: {uid} \n"
    else:
        comment = f"# 这是账号, uid:{uid}, username: {username} \n"

    with open(out_yaml_file, "r", encoding="utf-8") as yaml_file:
        yaml_content = yaml_file.read()
    # 在 YAML 文件开头添加注释
    yaml_with_comment = comment + yaml_content
    # 写入更新后的 YAML 文件
    with open(out_yaml_file, "w", encoding="utf-8") as yaml_file:
        yaml_file.write(yaml_with_comment)

    return yamldata


if __name__ == "__main__":
    uid = 1
    data = convert_json_to_yaml(uid=uid)
    log.info("合并完成 data 为:  " + str(data))
