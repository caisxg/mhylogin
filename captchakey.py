import os
from pathlib import Path

import yaml


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


current_directory = os.path.dirname(os.path.realpath(__file__))
captechakey_file = os.path.join(current_directory,"inputyaml", "captcha.yaml")
captechakey = read_yaml_file(captechakey_file)


apikey = captechakey["CAPTCHA2"]["apikey"]


__all__ = ["apikey"]