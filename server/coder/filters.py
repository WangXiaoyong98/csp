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
# @file        filters.py
#
# Change Logs:
# Date           Author       Notes
# ------------   ----------   -----------------------------------------------
# 2025-07-09     xqyjlj       initial version
#


def _do_hex(value: int, length: int = 8) -> str:
    return f"0x{int(value):0{length}X}"


def _pin_channels(project):
    if not hasattr(project, 'configs'):
        return []
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return []
    
    pinmux = configs.get("pinmux", {})
    if not pinmux:
        return []
    
    return list(pinmux.keys())


def _pin_function(project, channel):
    if not hasattr(project, 'configs'):
        return None
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return None
    
    pinmux = configs.get("pinmux", {})
    if not pinmux:
        return None
    
    return pinmux.get(channel)


def _gpio_used_channels(project):
    if not hasattr(project, 'configs'):
        return []
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return []
    
    pinmux = configs.get("pinmux", {})
    if not pinmux:
        return []
    
    used_channels = []
    for channel, function in pinmux.items():
        if function and function.startswith("GPIO:"):
            used_channels.append(channel)
    
    return used_channels


def _gpio_channel_alias(project, channel):
    if not hasattr(project, 'configs'):
        return channel
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return channel
    
    gpio = configs.get("gpio", {})
    if not gpio:
        return channel
    
    aliases = gpio.get("aliases", {})
    if not aliases:
        return channel
    
    return aliases.get(channel, channel)


FILTERS = {
    "hex": _do_hex,
    "pin_channels": _pin_channels,
    "pin_function": _pin_function,
    "gpio_used_channels": _gpio_used_channels,
    "gpio_channel_alias": _gpio_channel_alias,
}
