"""
Copyright 2017 刘士

Licensed under the Apache License, Version 2.0 (the "License"): you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""
import base64
import logging
import os
import random
import threading
import time
from typing import Union

report_path = ""
image_list = {}
image = True


def add_image(base64_data: Union[bytes, str], title: str = "", describe: str = ""):
    """添加截图到报告

    :param base64_data: base64格式的图片文本
    :param title: 图片标题
    :param describe: 图片提示
    :return: None
    """

    if not image or not base64_data or not report_path:
        return

    try:
        current_id = str(threading.current_thread().ident)
        if current_id not in image_list:
            image_list[current_id] = []

        random_name = f"image_{current_id}_{time.strftime('%Y_%m_%d_%H_%M_%S')}_{random.randint(1, 999)}.jpg"

        image_path = os.path.join(report_path, "images")
        if not os.path.exists(image_path):
            os.makedirs(image_path)

        image_file = os.path.join(image_path, random_name)
        with open(image_file, "wb") as f:
            f.write(base64.b64decode(base64_data))
            image_list[current_id].append(
                (os.path.join('images', random_name).replace("\\", "/"), describe, title, image_file)
            )
    except Exception as e:
        logging.error(f"保存截图失败\n{e}")
