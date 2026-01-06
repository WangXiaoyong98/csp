#!/usr/bin/env python3
# -*- coding:utf-8 -*-


# Licensed under the Apache License v. 2 (the "License")
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright (C) 2025-2025 xqyjlj<xqyjlj@126.com>
#
# @author      xqyjlj
# @file        pin.py
#
# Change Logs:
# Date           Author       Notes
# ------------   ----------   -----------------------------------------------
# 2025-11-12     xqyjlj       initial version
#


import json


class Pin:
    def __init__(self, data: dict):
        # 创建数据副本，移除modes字段
        self.__data = data.copy()
        
        # 处理GPIO信息，将modes中的GPIO信息整合到signals中
        self.__process_gpio_signals()

    def __process_gpio_signals(self):
        """处理GPIO信息，将modes中的GPIO信息整合到signals中"""
        # 获取原始signals和modes
        original_signals = self.__data.get("signals", [])
        modes = self.__data.get("modes", [])
        
        # 从modes中提取GPIO信息
        gpio_signals = []
        for mode in modes:
            if mode.startswith("GPIO:"):
                # 将GPIO:Input等转换为GPIO:0格式
                gpio_type = mode.split(":")[1]  # 获取Input, Output等
                gpio_signal = f"GPIO:{gpio_type}"
                gpio_signals.append(gpio_signal)
        
        # 合并signals，确保GPIO信号在最后
        combined_signals = original_signals.copy()
        for gpio_signal in gpio_signals:
            if gpio_signal not in combined_signals:
                combined_signals.append(gpio_signal)
        
        # 更新数据中的signals，移除modes字段
        self.__data["signals"] = combined_signals
        if "modes" in self.__data:
            del self.__data["modes"]

    def __str__(self) -> str:
        return json.dumps(self.__data, indent=2, ensure_ascii=False)

    @property
    def origin(self) -> dict:
        return self.__data

    @property
    def position(self) -> int:
        return self.__data.get("position", -1)

    @property
    def type(self) -> str:
        return self.__data.get("type", "")

    @property
    def signals(self) -> list[str]:
        return self.__data.get("signals", [])

    @property
    def modes(self) -> list[str]:
        # 返回空列表，因为modes字段已被移除并整合到signals中
        return []
