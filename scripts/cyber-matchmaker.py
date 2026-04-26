#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赛博月老 - 缘分指数计算脚本
基于五行属性和音律和谐度测算两个名字的缘分指数
"""

import argparse
import json
import sys
from typing import List, Dict, Tuple

try:
    from pypinyin import pinyin, Style
except ImportError:
    print("错误: 需要安装 pypinyin 库，请运行: pip install pypinyin==0.49.0")
    sys.exit(1)


# 五行相生相克关系
WUXING_SHENG = {
    "水": "木",  # 水生木
    "木": "火",  # 木生火
    "火": "土",  # 火生土
    "土": "金",  # 土生金
    "金": "水"   # 金生水
}

WUXING_KE = {
    "水": "火",  # 水克火
    "火": "金",  # 火克金
    "金": "木",  # 金克木
    "木": "土",  # 木克土
    "土": "水"   # 土克水
}


# 常见汉字五行映射（简化版，覆盖常用姓氏和名字用字）
WUXING_MAP = {
    # 金
    "金": "金", "钦": "金", "铭": "金", "锐": "金", "锡": "金", "锋": "金",
    "锦": "金", "银": "金", "钟": "金", "钢": "金", "钰": "金", "铎": "金",
    "陈": "金", "沈": "金", "钱": "金", "石": "金", "白": "金", "申": "金",
    "辛": "金", "郑": "金", "赵": "金", "周": "金", "祖": "金", "郝": "金",
    # 木
    "木": "木", "林": "木", "森": "木", "杨": "木", "柳": "木", "桃": "木",
    "李": "木", "柏": "木", "松": "木", "桂": "木", "梅": "木", "竹": "木",
    "王": "木", "张": "木", "朱": "木", "孔": "木", "何": "木", "宋": "木",
    "杜": "木", "汪": "木", "牛": "木", "董": "木", "贾": "木", "梁": "木",
    # 水
    "水": "水", "江": "水", "河": "水", "海": "水", "洋": "水", "波": "水",
    "涛": "水", "涵": "水", "清": "水", "洁": "水", "冰": "水", "雨": "水",
    "刘": "水", "黄": "水", "许": "水", "邓": "水", "曾": "水", "彭": "水",
    "潘": "水", "于": "水", "冯": "水", "苏": "水", "吕": "水", "卢": "水",
    # 火
    "火": "火", "炎": "火", "烈": "火", "炜": "火", "烁": "火", "煜": "火",
    "焕": "火", "灯": "火", "光": "火", "明": "火", "亮": "火", "辉": "火",
    "吴": "火", "孙": "火", "马": "火", "秦": "火", "袁": "火", "曹": "火",
    "田": "火", "丁": "火", "魏": "火", "史": "火", "萧": "火", "尹": "火",
    # 土
    "土": "土", "地": "土", "坤": "土", "坡": "土", "坦": "土", "培": "土",
    "基": "土", "坚": "土", "固": "土", "山": "土", "岩": "土", "峰": "土",
    "徐": "土", "高": "土", "郭": "土", "罗": "土", "梁": "土", "宋": "土",
    "唐": "土", "韩": "土", "姜": "土", "谢": "土", "邹": "土", "傅": "土"
}

# 默认五行（用于未收录的汉字，按笔画数取模）
DEFAULT_WUXING = ["金", "木", "水", "火", "土"]


def get_char_wuxing(char: str) -> str:
    """获取单个汉字的五行属性"""
    if char in WUXING_MAP:
        return WUXING_MAP[char]
    # 未收录的汉字，使用笔画数简单映射（这里用unicode码点模拟）
    code = ord(char)
    return DEFAULT_WUXING[code % 5]


def get_name_wuxing(name: str) -> List[str]:
    """获取姓名中每个字的五行属性"""
    return [get_char_wuxing(char) for char in name]


def get_pinyin_with_tone(name: str) -> Tuple[List[str], List[int]]:
    """获取姓名的拼音和声调"""
    py_list = pinyin(name, style=Style.TONE)
    tones = []
    pinyins = []
    for py in py_list:
        if py:
            pinyin_str = py[0]
            # 提取声调（1-4，轻声为5或0）
            tone = 5  # 默认轻声
            for i, char in enumerate(pinyin_str):
                if char in "āáǎà": tone = 1; break
                elif char in "ēéěè": tone = 2; break
                elif char in "īíǐì": tone = 3; break
                elif char in "ōóǒò": tone = 4; break
            # 去掉声调标记
            pinyin_clean = pinyin_str
            for old, new in zip("āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ", "aaaaeeeeiiiioooouuuuüüüü"):
                pinyin_clean = pinyin_clean.replace(old, new)
            tones.append(tone)
            pinyins.append(pinyin_clean)
    return pinyins, tones


def calculate_wuxing_score(wuxing1: List[str], wuxing2: List[str]) -> int:
    """计算五行相合度得分"""
    score = 0
    for wx1 in wuxing1:
        for wx2 in wuxing2:
            if wx1 == wx2:
                score += 10  # 相同，加分
            elif WUXING_SHENG.get(wx1) == wx2:
                score += 20  # 相生，大幅加分
            elif WUXING_SHENG.get(wx2) == wx1:
                score += 20  # 互相生
            elif WUXING_KE.get(wx1) == wx2:
                score -= 10  # 相克，减分
            elif WUXING_KE.get(wx2) == wx1:
                score -= 10  # 互相克
    return score


def calculate_tone_score(tones1: List[int], tones2: List[int]) -> int:
    """计算音律和谐度得分"""
    score = 0
    # 计算两名字中各声调的匹配度
    for t1 in tones1:
        for t2 in tones2:
            if t1 == t2:
                score += 5  # 声调相同，小幅加分
            elif abs(t1 - t2) <= 1 or (t1 == 5 and t2 in [1, 2, 3, 4]) or (t2 == 5 and t1 in [1, 2, 3, 4]):
                score += 10  # 声调相邻或平仄搭配，加分
    return score


def calculate_match_index(name1: str, name2: str) -> Dict:
    """计算两个姓名的缘分指数"""
    # 获取五行属性
    wuxing1 = get_name_wuxing(name1)
    wuxing2 = get_name_wuxing(name2)
    
    # 获取拼音和声调
    pinyin1, tones1 = get_pinyin_with_tone(name1)
    pinyin2, tones2 = get_pinyin_with_tone(name2)
    
    # 计算各维度得分
    wuxing_score = calculate_wuxing_score(wuxing1, wuxing2)
    tone_score = calculate_tone_score(tones1, tones2)
    
    # 基础分50分，加上五行和音律得分
    base_score = 50
    total_score = base_score + wuxing_score + tone_score
    
    # 限制在0-100范围内
    match_index = max(0, min(100, total_score))
    
    return {
        "index": int(match_index),
        "wuxing_name1": wuxing1,
        "wuxing_name2": wuxing2,
        "pinyin_name1": pinyin1,
        "pinyin_name2": pinyin2,
        "tones_name1": tones1,
        "tones_name2": tones2,
        "wuxing_score": wuxing_score,
        "tone_score": tone_score
    }


def main():
    parser = argparse.ArgumentParser(description="赛博月老 - 缘分指数计算")
    parser.add_argument("--name1", required=True, help="第一个姓名")
    parser.add_argument("--name2", required=True, help="第二个姓名")
    
    args = parser.parse_args()
    
    result = calculate_match_index(args.name1, args.name2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
