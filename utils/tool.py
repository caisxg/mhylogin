import json
import os
import random
import sys
import time
from pathlib import Path

import yaml


def get_sleep_time(start_sleep_time=3, end_sleeptime=5):
    time.sleep(random.uniform(start_sleep_time, end_sleeptime))
    return None


def read_yaml_file(file_path, **kw):
    """
    读取YAML文件并转换为字典, 返回字典
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if not Path(file_path).exists():
        raise Exception(f"文件{file_path.absolute()}不存在")
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader, **kw)
    return data


def write_dict_to_yaml(filename, data, **kw):
    """
    将字典写入yaml文件
    :param filename: 文件名
    :param data: 字典
    :param indent: 缩进
    :param sort_keys: 是否按键排序
    """
    if not isinstance(data, dict):
        raise Exception("data must be dict")

    if Path(filename).exists():
        Path(filename).unlink()
    with open(filename, "w", encoding="utf-8") as file:
        yaml.dump(
            data,
            file,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
            default_flow_style=False,
            width=3000,
            **kw,
        )


def read_json_file(file_path, **kw):
    """
    读取JSON文件并转换为字典, 返回字典
    """
    if not Path(file_path).exists():
        raise Exception(f"文件{file_path}不存在")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f, **kw)
    return data


def write_dict_to_json(filename, data, **kw):
    """
    将字典写入json文件
    :param filename: 文件名
    :param data: 字典
    :param indent: 缩进
    :param sort_keys: 是否按键排序
    """
    if not isinstance(data, dict):
        raise Exception("data must be dict")

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, **kw)


# 读取 JSON 文件并追加新数据的函数
def append_to_json(filename, new_data):
    """
    读取 JSON 文件并追加新数据
    :param filename: 文件名
    :param new_data: 新数据
    """
    if not isinstance(new_data, dict):
        raise Exception("new_data must be dict")

    if not Path(filename).exists():
        # 自动创建文件
        write_dict_to_json(filename, new_data, ensure_ascii=False, indent=2, sort_keys=False)
        return

    jsondata = read_json_file(filename)
    jsondata.update(new_data)
    write_dict_to_json(filename, jsondata, ensure_ascii=False, indent=2, sort_keys=False)


def convert_cookie_str_to_dict(cookie_str):
    """
    将cookie字符串转换为字典
    :param cookie_str: cookie字符串
    :return: 转换后的cookie字典
    """
    if not cookie_str:
        return {}  # 处理空字符串或空值的情况，返回空字典

    cookie_list = cookie_str.split(";")
    cookie_dict = {}
    for item in cookie_list:
        try:
            key, value = item.strip().split("=", 1)  # 处理键值对格式错误的情况
            cookie_dict[key] = value
        except ValueError:
            # 如果键值对格式错误，则跳过该键值对或根据需求处理异常情况
            pass

    return cookie_dict



