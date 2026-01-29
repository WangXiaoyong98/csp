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


def _gpio_channels(project, channels=None):
    if not hasattr(project, 'configs'):
        return []
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return []
    
    # 尝试从pins中获取GPIO通道
    pins = configs.get("pins", {})
    gpio_channels = []
    for pin_name, pin_config in pins.items():
        if pin_config.get('function', '').startswith('GPIO:'):
            gpio_channels.append(pin_name)
    
    # 如果pins中没有GPIO通道，尝试从GPIO配置中获取
    if not gpio_channels:
        gpio_config = configs.get("GPIO", {})
        for channel_name in gpio_config:
            if isinstance(gpio_config[channel_name], dict):
                gpio_channels.append(channel_name)
    
    return gpio_channels


def _gpio_used_ports(channels):
    # 对于GPIO32这样的通道格式，直接返回通道本身作为端口
    return list(set(channels))


def _gpio_eint_channels(project, channels=None):
    if not hasattr(project, 'configs'):
        return []
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return []
    
    pins = configs.get("pins", {})
    if not pins:
        return []
    
    eint_channels = []
    for channel, pin_config in pins.items():
        function = pin_config.get('function', '')
        if function and function.startswith("GPIO:EINT"):
            eint_channels.append(channel)
    
    return eint_channels


def _gpio_eventout_channels(project, channels=None):
    if not hasattr(project, 'configs'):
        return []
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return []
    
    pins = configs.get("pins", {})
    if not pins:
        return []
    
    eventout_channels = []
    for channel, pin_config in pins.items():
        function = pin_config.get('function', '')
        if function and function.startswith("GPIO:EVENTOUT"):
            eventout_channels.append(channel)
    
    return eventout_channels


def _gpio_channels_group_by_port(project, channels, port):
    # 返回一个列表的列表，每个子列表包含与指定端口匹配的通道
    matched_channels = []
    for channel in channels:
        if channel == port:
            matched_channels.append(channel)
    # 如果有匹配的通道，返回包含这些通道的列表的列表
    if matched_channels:
        return [matched_channels]
    return []


def _gpio_channels_classify_by_state(project, channels):
    if not hasattr(project, 'configs'):
        return {}
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return {}
    
    state_groups_map = {}
    for channel in channels:
        state = configs.get(f"GPIO.{channel}.gpio_state_t", "reset")
        if state not in state_groups_map:
            state_groups_map[state] = []
        state_groups_map[state].append(channel)
    
    return state_groups_map


def _gpio_channel_mode(project, channel):
    if not hasattr(project, 'configs'):
        return ""
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return ""
    
    mode = configs.get(f"GPIO.{channel}.gpio_mode_t", "input")
    pull = configs.get(f"GPIO.{channel}.gpio_pull_t", "nopull")
    
    mode_map = {
        "input": "GPIO_MODE_IN_FLOATING",
        "it_rising": "GPIO_MODE_IT_RISING",
        "it_falling": "GPIO_MODE_IT_FALLING",
        "it_rising_falling": "GPIO_MODE_IT_RISING_FALLING",
        "evt_rising": "GPIO_MODE_EVT_RISING",
        "evt_falling": "GPIO_MODE_EVT_FALLING",
        "evt_rising_falling": "GPIO_MODE_EVT_RISING_FALLING",
        "output_pp": "GPIO_MODE_OUTPUT_PP",
        "output_od": "GPIO_MODE_OUTPUT_OD",
        "af_pp": "GPIO_MODE_AF_PP",
        "af_od": "GPIO_MODE_AF_OD",
        "analog": "GPIO_MODE_ANALOG"
    }
    
    return mode_map.get(mode, "GPIO_MODE_IN_FLOATING")


def _gpio_channel_speed(project, channel):
    if not hasattr(project, 'configs'):
        return ""
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return ""
    
    speed = configs.get(f"GPIO.{channel}.gpio_speed_t", "low")
    
    speed_map = {
        "low": "GPIO_SPEED_2MHz",
        "medium": "GPIO_SPEED_10MHz",
        "high": "GPIO_SPEED_50MHz"
    }
    
    return speed_map.get(speed, "GPIO_SPEED_2MHz")


def _gpio_channel_eint_mode(project, channel):
    if not hasattr(project, 'configs'):
        return ""
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return ""
    
    mode = configs.get(f"GPIO.{channel}.gpio_mode_t", "")
    
    if mode in ["it_rising", "it_falling", "it_rising_falling"]:
        return "EINT_MODE_INTERRUPT"
    elif mode in ["evt_rising", "evt_falling", "evt_rising_falling"]:
        return "EINT_MODE_EVENT"
    
    return ""


def _gpio_channel_eint_trigger(project, channel):
    if not hasattr(project, 'configs'):
        return ""
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return ""
    
    mode = configs.get(f"GPIO.{channel}.gpio_mode_t", "")
    
    if mode in ["it_rising", "evt_rising"]:
        return "EINT_TRIGGER_RISING"
    elif mode in ["it_falling", "evt_falling"]:
        return "EINT_TRIGGER_FALLING"
    elif mode in ["it_rising_falling", "evt_rising_falling"]:
        return "EINT_TRIGGER_RISING_FALLING"
    
    return ""


def _gpio_channel_direction(project, channel, instance="GPIO"):
    if not hasattr(project, 'configs'):
        return "GPIO_DIR_MODE_IN"
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return "GPIO_DIR_MODE_IN"
    
    direction = configs.get(f"{instance}.{channel}.gpio_direction_t", "input")
    return "GPIO_DIR_MODE_OUT" if direction == "output" else "GPIO_DIR_MODE_IN"


def _gpio_channel_pad_config(project, channel, instance="GPIO"):
    if not hasattr(project, 'configs'):
        return "GPIO_PIN_TYPE_IE"
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return "GPIO_PIN_TYPE_IE"
    
    # 尝试直接获取预计算的pad_config
    pad_config = configs.get(f"{instance}.{channel}.gpio_pad_config", "")
    if pad_config:
        return pad_config
    
    # 如果没有预计算的pad_config，则根据各个配置选项计算
    pin_type = configs.get(f"{instance}.{channel}.gpio_pin_type_t", "")
    direction = configs.get(f"{instance}.{channel}.gpio_direction_t", "input")
    drive_strength = configs.get(f"{instance}.{channel}.gpio_drive_strength_t", "low")
    slew_rate = configs.get(f"{instance}.{channel}.gpio_slew_rate_t", "low")
    current_source = configs.get(f"{instance}.{channel}.gpio_current_source_t", "false")
    input_enable = configs.get(f"{instance}.{channel}.gpio_input_enable_t", "true")
    
    # 初始化宏列表
    macros = []
    
    # 根据pin_type添加相应的宏
    if pin_type == "open_drain":
        macros.append("GPIO_PIN_TYPE_OD")
    elif pin_type == "pullup":
        macros.append("GPIO_PIN_TYPE_PULLUP")
    elif pin_type == "pulldown":
        macros.append("GPIO_PIN_TYPE_PULLDOWN")
    
    # 检查驱动强度
    if drive_strength == "high":
        macros.append("GPIO_PIN_TYPE_DRE")
    
    # 检查转换率
    if slew_rate == "high":
        macros.append("GPIO_PIN_TYPE_SRE")
    
    # 检查输入施密特触发器
    if current_source == "true":
        macros.append("GPIO_PIN_TYPE_CSE")
    
    # 检查输入使能
    if input_enable == "true":
        macros.append("GPIO_PIN_TYPE_IE")
    
    return " | ".join(macros) if macros else "GPIO_PIN_TYPE_IE"


def _gpio_channel_qualification_mode(project, channel):
    return "GPIO_QUAL_SYNC"


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


def _gpio_channel_state(project, channel):
    if not hasattr(project, 'configs'):
        return "BIT_RESET"
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return "BIT_RESET"
    
    state = configs.get(f"GPIO.{channel}.gpio_state_t", "reset")
    return "BIT_SET" if state == "set" else "BIT_RESET"


def _gpio_channel_clock(project, channel):
    if len(channel) >= 2:
        return f"RCM_APB2_PERIPH_GPIO{channel[1].upper()}"
    return ""


def _gpio_channel_port(project, channel):
    if len(channel) >= 2:
        return f"GPIO{channel[1].upper()}"
    return ""


def _gpio_channel_to_port(channel):
    # 对于GPIO32这样的通道格式，直接返回通道本身作为端口
    if channel.startswith('GPIO'):
        return channel
    return ""


def _gpio_channel_to_clock(channel):
    # 对于GPIO32这样的通道格式，我们假设所有GPIO都使用同一个时钟
    if channel.startswith('GPIO'):
        return "RCM_APB2_PERIPH_GPIO"
    return ""


def _gpio_channel_to_port_source(channel):
    # 对于GPIO32这样的通道格式，我们假设所有GPIO都使用同一个端口源
    if channel.startswith('GPIO'):
        return "GPIO_PORT_SOURCE_GPIO"
    return ""


def _gpio_channel_to_pin(channel):
    if len(channel) >= 5 and channel.startswith('GPIO'):
        pin_num = channel[4:]
        return f"GPIO_PIN_{pin_num}"
    return ""


def _gpio_channel_to_pin_source(channel):
    if len(channel) >= 5 and channel.startswith('GPIO'):
        pin_num = channel[4:]
        return f"GPIO_PIN_SOURCE_{pin_num}"
    return ""


def _gpio_channel_to_eint_line(channel):
    if len(channel) >= 5 and channel.startswith('GPIO'):
        pin_num = channel[4:]
        return f"EINT_LINE_{pin_num}"
    return ""


def _gpio_channel_port_source(project, channel):
    # 对于GPIO32这样的通道格式，我们假设所有GPIO都使用同一个端口源
    if channel.startswith('GPIO'):
        return "GPIO_PORT_SOURCE_GPIO"
    return ""


def _gpio_channel_pin(project, channel):
    if len(channel) >= 5 and channel.startswith('GPIO'):
        pin_num = channel[4:]
        return f"GPIO_PIN_{pin_num}"
    return ""


def _gpio_channel_pin_source(project, channel):
    if len(channel) >= 5 and channel.startswith('GPIO'):
        pin_num = channel[4:]
        return f"GPIO_PIN_SOURCE_{pin_num}"
    return ""


def _gpio_channel_eint_line(project, channel):
    if len(channel) >= 5 and channel.startswith('GPIO'):
        pin_num = channel[4:]
        return f"EINT_LINE_{pin_num}"
    return ""


def _gpio_channels_to_pins(channels):
    pins = []
    for channel in channels:
        if len(channel) >= 5 and channel.startswith('GPIO'):
            pin_num = channel[4:]
            pins.append(f"GPIO_PIN_{pin_num}")
    return pins


def _gpio_used_clocks(project, channels=None):
    if not hasattr(project, 'configs'):
        return []
    
    configs = project.configs
    if not hasattr(configs, 'get'):
        return []
    
    # 尝试从pins中获取GPIO通道
    pins = configs.get("pins", {})
    clocks = []
    
    for pin_name, pin_config in pins.items():
        if pin_config.get('function', '').startswith('GPIO:'):
            # 对于GPIO32这样的通道格式，我们假设所有GPIO都使用同一个时钟
            clocks.append("RCM_APB2_PERIPH_GPIO")
            if 'EINT' in pin_config.get('function', '') or 'EVENTOUT' in pin_config.get('function', ''):
                clocks.append("RCM_APB2_PERIPH_AFIO")
    
    # 如果pins中没有GPIO通道，尝试从GPIO配置中获取
    if not clocks:
        gpio_config = configs.get("GPIO", {})
        for channel_name in gpio_config:
            if isinstance(gpio_config[channel_name], dict):
                clocks.append("RCM_APB2_PERIPH_GPIO")
    
    return list(set(clocks))


def _gpio_clocks_to_alias(clocks):
    aliases = []
    for clock in clocks:
        if clock.startswith("RCM_APB2_PERIPH_"):
            aliases.append(clock[16:])
    return aliases


FILTERS = {
    "hex": _do_hex,
    "pin_channels": _pin_channels,
    "pin_function": _pin_function,
    "gpio_used_channels": _gpio_used_channels,
    "gpio_channel_alias": _gpio_channel_alias,
    "gpio_channels": _gpio_channels,
    "gpio_used_ports": _gpio_used_ports,
    "gpio_eint_channels": _gpio_eint_channels,
    "gpio_eventout_channels": _gpio_eventout_channels,
    "gpio_channels_group_by_port": _gpio_channels_group_by_port,
    "gpio_channels_classify_by_state": _gpio_channels_classify_by_state,
    "gpio_channel_mode": _gpio_channel_mode,
    "gpio_channel_speed": _gpio_channel_speed,
    "gpio_channel_eint_mode": _gpio_channel_eint_mode,
    "gpio_channel_eint_trigger": _gpio_channel_eint_trigger,
    "gpio_channel_direction": _gpio_channel_direction,
    "gpio_channel_pad_config": _gpio_channel_pad_config,
    "gpio_channel_qualification_mode": _gpio_channel_qualification_mode,
    "gpio_channel_state": _gpio_channel_state,
    "gpio_channel_clock": _gpio_channel_clock,
    "gpio_channel_port": _gpio_channel_port,
    "gpio_channel_port_source": _gpio_channel_port_source,
    "gpio_channel_pin": _gpio_channel_pin,
    "gpio_channel_pin_source": _gpio_channel_pin_source,
    "gpio_channel_eint_line": _gpio_channel_eint_line,
    "gpio_channel_to_port": _gpio_channel_to_port,
    "gpio_channel_to_clock": _gpio_channel_to_clock,
    "gpio_channel_to_port_source": _gpio_channel_to_port_source,
    "gpio_channel_to_pin": _gpio_channel_to_pin,
    "gpio_channel_to_pin_source": _gpio_channel_to_pin_source,
    "gpio_channel_to_eint_line": _gpio_channel_to_eint_line,
    "gpio_channels_to_pins": _gpio_channels_to_pins,
    "gpio_used_clocks": _gpio_used_clocks,
    "gpio_clocks_to_alias": _gpio_clocks_to_alias,
}
