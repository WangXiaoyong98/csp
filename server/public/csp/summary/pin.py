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
        """处理GPIO信息，保持modes中的GPIO信息作为可选模式，同时确保它们也在signals中可用"""
        # 获取原始signals和modes
        original_signals = self.__data.get("signals", [])
        original_modes = self.__data.get("modes", [])
        
        # 分离GPIO modes和其他modes
        gpio_modes = []
        other_modes = []
        for mode in original_modes:
            if mode.startswith("GPIO:"):
                # 对于GPIO模式，保持原样（如GPIO:0, GPIO:Input, GPIO:Output）
                gpio_modes.append(mode)
            else:
                other_modes.append(mode)
        
        # 提取GPIO信号部分（用于添加到signals列表）
        gpio_signals_for_output = []
        for mode in gpio_modes:
            if mode.startswith("GPIO:") and len(mode.split(":")) >= 2:
                # 如果是像GPIO:0这样的格式，直接使用完整形式
                gpio_signals_for_output.append(mode)
        
        # 合并signals，确保GPIO信号在最后，避免重复
        combined_signals = original_signals.copy()
        for gpio_signal in gpio_signals_for_output:
            if gpio_signal not in combined_signals:
                combined_signals.append(gpio_signal)
        
        # 更新数据中的signals
        self.__data["signals"] = combined_signals
        
        # 保留所有modes，包括GPIO modes
        all_modes = []
        all_modes.extend(other_modes)
        all_modes.extend(gpio_modes)
        
        # 只有当存在modes时才设置modes字段
        if all_modes:
            # 去除modes中的重复项，保持原有顺序
            unique_modes = []
            seen = set()
            for mode in all_modes:
                if mode not in seen:
                    unique_modes.append(mode)
                    seen.add(mode)
            self.__data["modes"] = unique_modes
        elif "modes" in self.__data:
            # 如果原本有modes但处理后为空，则删除该字段
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
        # 返回实际的modes列表
        return self.__data.get("modes", [])
