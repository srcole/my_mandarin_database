import pandas as pd
import numpy as np
import os
import time
import shutil
import datetime
from edge_tts import Communicate
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, VideoFileClip
from utils_video import determine_if_text_size_too_big
from pydub import AudioSegment
from utils_shorts import draw_logo, draw_resized_text_on_image
from constants import WORD_TYPES, PROPER_NOUN_TYPES


data_settings_by_char = {
#     '': {
#         'shared_char': '',
#         'char_pinyin': '',
#         'char_english': '',
#         'max_priority': 6,
#         'min_adu': 3,
#         'min_per': 3,
#         'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
#         'sort_cols': ['priority', 'cat_v3', 'pinyin'],
#         'sort_ascending': [True, True, True],
#         'words_rmv': ,
#         'n_words_per_video': 11,
#         'current_part': 1,
#         'text_replacements': 
#     }
# ,
#     '': {
#         'shared_char': '',
#         'char_pinyin': '',
#         'char_english': '',
#         'max_priority': 6,
#         'min_adu': 3,
#         'min_per': 3,
#         'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
#         'sort_cols': ['priority', 'cat_v3', 'pinyin'],
#         'sort_ascending': [True, True, True],
#         'words_rmv': ,
#         'n_words_per_video': 11,
#         'current_part': 1,
#         'text_replacements': 
#     }
# ,
#     '': {
#         'shared_char': '',
#         'char_pinyin': '',
#         'char_english': '',
#         'max_priority': 6,
#         'min_adu': 3,
#         'min_per': 3,
#         'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
#         'sort_cols': ['priority', 'cat_v3', 'pinyin'],
#         'sort_ascending': [True, True, True],
#         'words_rmv': ,
#         'n_words_per_video': 11,
#         'current_part': 1,
#         'text_replacements': 
#     }
# ,
    '情': {
        'shared_char': '情',
        'char_pinyin': 'qíng',
        'char_english': 'emotion / feeling',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['情绪稳定', '详情', '情绪价值', '有情况'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            '(facial) expression': 'facial expression',
            'emoji;emoticon;meme': 'emoji',
            'COVID19;epidemic situation': 'epidemic',
            'it depends;depending on the situation': 'it depends',
            'emotional intelligence;EQ': 'emotional intelligence',
            'condition;state (of an illness)': 'illness state',
            'local customs and practices': 'local customs'}

    }
,
    '鱼': {
        'shared_char': '鱼',
        'char_pinyin': 'yú',
        'char_english': 'fish',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['鱼香肉丝', '西湖醋鱼', '闲鱼', '小鱼干', '醋笋壳鱼'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'fire someone;get fired;to sack': 'get fired (slang)'}
    }
,
    '面': {
        'shared_char': '面',
        'char_pinyin': 'miàn',
        'char_english': 'noodle / face',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['重庆小面', '红烧牛肉面', '杂酱面', '黑麦面包', '全麦面包', '羊角面包',
                      '政治局面', '蒙面鬼', '泡椒鸡胗面', '香干肉丝面'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'to face;confront': 'confront',
            'interview (job)': 'interview for job',
            'face; reputation': 'reputation',
            'superficial;surface': 'superficial',
            'unilateral;one-sided': 'unilateral'}
    }
,
    '果': {
        'shared_char': '果',
        'char_pinyin': 'guǒ',
        'char_english': 'fruit / result',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['苹果酒', '综合果汁', '平安果', '芒果黄', '糖果传奇'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'result;outcome': 'result',
            'jam;jelly': 'jam',
            'fruits and vegetables;produce': 'produce',
            'foreigner': 'foreigner (slang)'}
    }
,
    '马': {
        'shared_char': '马',
        'char_pinyin': 'mǎ',
        'char_english': 'horse',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['亚马逊', '马云', '埃隆 马斯克', '盒马', '马尼拉', '马里奥赛车',
                      '危地马拉', '奥巴马', '马化腾', '罗马', '亚马逊河', '白马寺'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'immediately;at once;right away': 'immediately',
            'careless;sloppy': 'careless'}
    }
,
    '主': {
        'shared_char': '主',
        'char_pinyin': 'zhǔ',
        'char_english': 'main / master',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['女权主义', '个人主义', '消费主义', '保守主义', '不婚主义者', '共产主义', '民主党', '碧琪公主',
                      '家庭主妇', '极简主义', '公主病', '单身主义'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'blogger;vlogger': 'blogger / vlogger',
            'initiative;voluntarily': 'initiative',
            'theme;subject': 'theme',
            'subject (part of speech)': 'subject'}
    }
,
    '体': {
        'shared_char': '体',
        'char_pinyin': 'tǐ',
        'char_english': 'body / form',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['具体的时间', '身体部位', '体力不支'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'to personally experience': 'to experience',
            'thoughtful;considerate': 'thoughtful',
            'traditional Chinese characters': 'traditional Chinese',
            'simplified Chinese characters': 'simplified Chinese',
            'physical examination': 'physical exam',
            'brick and mortar store': 'brick & mortar',
            '(body) thermometer': 'body thermometer',
            'reflect;embodies': 'embodies',
            'solid (state)': 'solid', 'gas (state)': 'gas', 'liquid (state)': 'liquid'}
    }
,
    '可': {
        'shared_char': '可',
        'char_pinyin': 'kě',
        'char_english': 'can / may',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['可怜的狗', '百事可乐', '可回收物', '不可思议', 'CoCo都可', '塔可钟', '无家可归的人', '必不可少', '未经许可', '可乐罐'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'what a pity;unfortunately': 'what a pity',
            'pitiful;pathetic': 'pitiful',
            'coke;cola;amusing;entertaining': 'Cola / amusing',
            'reliable (reputation)': 'reliable',
            'to approve;approval': 'to approve',
            'clear;can be seen;clearly be seen': 'clearly be seen',}
    }
,
    '点': {
        'shared_char': '点',
        'char_pinyin': 'diǎn',
        'char_english': 'dot / point',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['大众点评', '二点四万人', '标点符号', '快递点', '最大的弱点', '有点模糊', '没有终点', '一点点'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'like (social media)': 'to like',
            'shortcoming;disadvantage;con': 'disadvantage',
            'advantage;pro': 'advantage', 'click (here)': 'click here',
            'characteristic feature;trait': 'characteristic feature',
            'focus;key;main point': 'main point',
            'argument;thesis': 'argument / thesis'}
    }
,
    '行': {
        'shared_char': '行',
        'char_pinyin': 'xíng',
        'char_english': 'walk / go',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['随身的行李', '银行','中国工商银行', '中国建设银行', '中国农业银行', '中国银行', 
                      '携程旅行', '托运行李', '行李寄存', '行业', '流行音乐', '爬行动物', '流行歌曲', '违法行为',  '行李转盘', '香港特别行政区', '澳门特别行政区'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {}
    }
,
    '气': {
        'shared_char': '气',
        'char_pinyin': 'qì',
        'char_english': 'air / gas',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['天气预报', '节日气氛', '口气清新', '假客气', '圣诞气氛'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'tone;mood': 'tone / mood',
            'to lose temper;get angry': 'to lose temper',
            'temper;character;disposition': 'temper / disposition',
            'atmosphere;mood': 'atmosphere / mood',
            'naughty;mischievous': 'naughty',
            'to ventilate;exhaust': 'to ventilate / exhaust',
            'gas (state)': 'gas'}
    }
,
    '平': {
        'shared_char': '平',
        'char_pinyin': 'píng',
        'char_english': 'flat / level',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['世界和平', '邓小平', '习近平', '平均每天', '男女平等', '平遥古城', '平安果', '平地人', '平壤'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'calm;tranquil': 'calm',
            'dull;plain;ordinary': 'dull'}
    }
,
    '学': {
        'shared_char': '学',
        'char_pinyin': 'xué',
        'char_english': 'study',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['学到', '科学家', '孔子学院', '计算机科学', '北京大学', '清华大学', '肾脏病学', '家用化学品',
                      '复旦大学', '化学反应', '核医学科', '老年医学科', '全科医学科'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'semester;term': 'semester'}
    }
,
    '家': {
        'shared_char': '家',
        'char_pinyin': 'jiā',
        'char_english': 'home',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['买家的评价', '外婆家', '科学家', '艺术家', '京东到家', '发展中国家',
                      '优胜美地国家公园', '陆家嘴', '买家秀', '全家福卷', '画家', '作家', '石家庄',
                      '家乐福', '国家地理', '家用化学品', '无家可归的人', '张家口', '乔家大院', '王家大院', '娘家', '婆家'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'to move (home)': 'to move (home)',
            'parent;guardian': 'parent',
            'housework;chore': 'housework',
            'to start a family': 'start a family'}
    }
,
    '小': {
        'shared_char': '小',
        'char_pinyin': 'xiǎo',
        'char_english': 'small',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['不小心', '小红书', '邓小平', '线条小狗', '小鲜肉', '小库巴', '小游戏', '小猪佩奇', '重庆小面',
                      '小鱼干', '李小龙', '小燃', '丑小鸭', '小明', '愤怒的小鸟'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'be careful': 'careful',
            'to underestimate;look down on': 'underestimate',
            'to urinate;pee': 'urinate',
            'number one;pee;trumpet': 'to pee'}
    }
,
    '中': {
        'shared_char': '中',
        'char_pinyin': 'zhōng',
        'char_english': 'middle',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['中年危机', '四月中', '中国联通', '中国移动', '中央电视台', '中国工商银行', '中国建设银行', '中国农业银行', '中国银行',
                      '中年油腻大叔', '中国国际航空', '发展中国家', '中国电信', '孙中山', '四月中旬',  '中央人民广播电台', '中央空调', '中国达人秀', '放疗中心'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
           'moderation;golden mean': 'moderation',
           'halfway;midway': 'midway',
           'middle of the month': 'mid-month',
           'middle ages;medieval': 'middle ages',
           'overly self-conscious or immature': 'overly self-conscious',
           'Winning the lottery': 'win the lottery'}
    }
,
    '心': {
        'shared_char': '心',
        'char_pinyin': 'xīn',
        'char_english': 'heart',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['穷开心', '放疗中心', '神经心理评估', '心脏大血管外科', '核心运动'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'anxious;worried': 'worried',
            'core;essence': 'core',
            'distraction;distracted': 'distracted',
            'intimate;close;considerate': 'intimate',
            'psychology;mentality': 'psychology',
            'mood': 'mood',
            'concerned;feel sorry for someone': 'feel sorry for',
            'nausea;feel sick;disgusting': 'disgusting',
            'fragile (person)': 'fragile person',
            'to feel relieved;reassured;at ease': 'to feel relieved',
            'sad;heartbroken': 'sad',
            'electrocardiogram;ECG': 'electrocardiogram',
            'flirtatious;unfaithful': 'flirtatious',
            'petty;narrow-minded': 'petty',
            'peace of mind;at ease; relieved': 'peace of mind',
            'palm (of hand)': 'palm of hand',
            'good samaritan;good hearted person': 'good samaritan'}
    }
,
    '机': {
        'shared_char': '机',
        'char_pinyin': 'jī',
        'char_english': 'machine',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['中年危机', '计算机软件开发', '金融危机', '计算机科学', '赚钱的机器', '工作机会'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'opportunity;chance': 'opportunity',
            'driver;chauffeur': 'driver',
            'audio recorder;tape recorder': 'tape recorder',
            'check-in (airline)': 'airline check-in',
            'photocopier;copy machine': 'photocopier',
            'Government agencies': 'government agency'}
    }
,
    '上': {
        'shared_char': '上',
        'char_pinyin': 'shàng',
        'char_english': 'upper',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['上海', '今年上半年', '四月上旬', '上流社会', '太上皇', '上座', '上海市', '清明上河园'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'rise;ascent;increased': 'rise',
            'immediately;at once;right away': 'immediately',
            'lap;on the legs': 'on lap',
            'previous;last': 'previous',
            'to fall in love': 'fall in love',
            'above': 'and above',
            'start of the month': 'start of month',
            'make progress;ambitious;motivated': 'make progress',
            'On the internet': 'on the internet',
            'high society;upper class': 'upper class',
            'like;interested;fancy': 'to fancy',
            'get overly obsessed or hyped (head rush)': 'overly obsessed'}
    }
,
    '天': {
        'shared_char': '天',
        'char_pinyin': 'tiān',
        'char_english': 'day / sky',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['平均每天', '这几天', '天安门广场', '天猫', '天津', '天妇罗', '天坛', '天蓝', '天津市'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'heaven;paradise': 'heaven',
            'innocent;naive': 'naive'}
    }
,
    '金': {
        'shared_char': '金',
        'char_pinyin': 'jīn',
        'char_english': 'metal / gold',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['金', '金融危机', '金正恩', '金门大桥', '订金', '交易所交易基金',
                     '金州勇士', '金华', '金黄', '玫瑰金', '黄金周'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'finance;banking': 'finance',
            'bonus (money)': 'bonus',
            'rent (amount)': 'rent'}
    }
,
    '物': {
        'shared_char': '物',
        'char_pinyin': 'wù',
        'char_english': 'thing',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['食物中毒', '有机的食物', '哺乳动物', '两栖动物', '啮齿动物', '爬行动物',
                      '卡通人物', '濒危物种', '礼物标签',
                      '疯狂动物城', '礼物袋', '礼物盒', '圣诞礼物', '失物招领架'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {}
    }
,
    '语': {
        'shared_char': '语',
        'char_pinyin': 'yǔ',
        'char_english': 'language',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['德语', '法语', '韩语', '日语', '西班牙语', '意大利语', '俄语',
                     '阿拉伯语', '哑巴英语者'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'tone;mood': 'tone / mood',
            'intonation (language)': 'intonation',
            'modal particles': 'modal particle',
            'word;term;expression': 'word / term',
            'collocations (word combinations)': 'collocations',
            'subject (part of speech)': 'subject',
            'common saying;idiom': 'common saying'}
    }
,
    '时': {
        'shared_char': '时',
        'char_pinyin': 'shí',
        'char_english': 'time',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['平时', '世界和平', '邓小平', '习近平', '平均每天', '男女平等',
                      '生活水平', '平遥古城', '平地人', '平壤'],
        'n_words_per_video': 12,
        'current_part': 1,
        'text_replacements': {
            'level;standard': 'level',
            'calm;tranquil': 'tranquil', 
            'dull;plain;ordinary': 'dull',
            'level (tool)': 'level tool'}
    }
,
    '红': {
        'shared_char': '红',
        'char_pinyin': 'hóng',
        'char_english': 'red',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['红', '红烧牛肉面','酒红', '玫红', '红遍', '红海',  '桃红', '西瓜红', '胭脂红', '砖红', '枣红', '红楼梦', '粉红', '橘红'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'Chinese Instagram + Pinterest': 'Little Red Book',
            'to blush;face turn red': 'to blush',
            'red scarf;young pioneer': 'red scarf kid',
            'rambutan;rumbutan': 'rambutan',
            'red bean;azuki bean': 'adzuki bean'}

    }
,
    '公': {
        'shared_char': '公',
        'char_pinyin': 'gōng',
        'char_english': 'public',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['铁公鸡', '公立医院', '航空公司', '黄石公园', '优胜美地国家公园', '共享办公室',
                      '碧琪公主', '公主病', '芝加哥公牛', '北海公园'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'branch (office)': 'branch office',
            'husband (casual)': 'husband',
            'grandfather (maternal)': 'maternal grandfather',
            'father-in-law (husband’s father)': "husband's father"}
    }
,
    '发': {
        'shared_char': '发',
        'char_pinyin': 'fā',
        'char_english': 'to emit',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['计算机软件开发', '沙发', '发展中国家', '发车', '大润发', '发胶', '打发时间', '发热门诊'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'serve (ball)': 'serve a ball',
            'to invent;invention': 'invent',
            '(to have) fever': 'fever',
            'to set off;depart': 'depart',
            'to lose temper;get angry': 'lose temper',
            'to get moldy': 'get moldy'}

    }
,
    '时': {
        'shared_char': '时',
        'char_pinyin': 'shí',
        'char_english': 'time',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['等待时间', '过渡时期', '具体的时间', '空闲时间', '按时'
                      '随时退', '营业时间', '开放时间', '下单时间', '纽约时报', '打发时间'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'jetlag;time difference': 'jetlag / time difference',
            'fashion;fashionable': 'fashion',
            'interim;ad hoc;temporary': 'interim',
            'era;Time Magazine': 'era',
            'schedule;timetable': 'timetable',
            'on time;on schedule;punctual': 'on time',
            'fixed time;definite time': 'fixed time',
            'at the same time;simultaneously': 'simultaneously',
            'meanwhile;at the same time': 'meanwhile'}

    }
,
    '自': {
        'shared_char': '自',
        'char_pinyin': 'zì',
        'char_english': 'self',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['自选菜饭店', '广西壮族自治区', '宁夏回族自治区', '自学的', '过度自信', '盲目自信', '不自觉地', '自相矛盾',
                      '自由女神', '自由女神像', '自我介绍', '内蒙古自治区', '西藏自治区', '新疆维吾尔自治区'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'inferior;self-deprecating': 'self-deprecating',
            'free;freedom;liberty': 'freedom',
            'self-driving cars': 'autonomous cars',
            'conscious;aware': 'conscious'}
    }
,
    '一': {
        'shared_char': '一',
        'char_pinyin': 'yī',
        'char_english': 'one',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['投诉一下', '一八年',  '第一作者', '一对三', '最后一名', '十一长假', '一点点', '一颗药', '一加'],
        'n_words_per_video': 12,
        'current_part': 1,
        'text_replacements': {
            'B1;basement level 1': 'basement level 1',
            'freshman (college)': 'college freshman',
            'first year graduate student': 'year 1 grad student',
            'other half;partner': 'partner',
            'previous;last': 'previous',
            'just in case;what if': 'what if',
            'Double 11 shopping festival;Singles day': 'Singles day'}
    }
,
    '山': {
        'shared_char': '山',
        'char_pinyin': 'shān',
        'char_english': 'mountain',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['桂林山水', '黄山', '泰山', '山东省', '山西省', '乐山大佛', '鸣沙山',
                      '佛山', '华山', '玉龙雪山', '山地人', '唐山', '长白山', '鞍山', '火山爆发', '承德避暑山庄',
                      '丹霞山', '火焰山', '老君山', '南岳衡山', '青城山', '嵩山', '五台山', '武夷山', '香山', '雁荡山'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {}
    }
,
    '头': {
        'shared_char': '头',
        'char_pinyin': 'tóu',
        'char_english': 'head',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['头', '梳头', '猫头鹰', '石头剪刀布', '头三', '低头族', '罐头', '多余的枕头', '橘子洲头','上头', '偏头痛', '包头'],
        'n_words_per_video': 12,
        'current_part': 1,
        'text_replacements': {
            'avatar;portrait;profile picture': 'profile picture',
            'pier;dock;wharf': 'wharf',
            'to look up;raise head': 'to look up',
            'video camera;webcam': 'video camera'}
    }
,
    '花': {
        'shared_char': '花',
        'char_pinyin': 'huā',
        'char_english': 'flower',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['花生酱', '菊花', '兰花', '樱花', '花光', '梅花', '荷花', '樱花粉'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'marshmallow;cotton candy': 'marshmallow/cotton candy',
            'spark;sparkle': 'spark',
            'flirtatious;unfaithful': 'flirty',
            'pattern;variety;style;trick': 'pattern/style',
            'lotus flower;water lily': 'water lily',
            'fangirl;infatuated': 'infatuated'}
    }
,
    '外': {
        'shared_char': '外',
        'char_pinyin': 'wài',
        'char_english': 'outside',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['外婆家', '整形外科', '户外活动', '外卖员', '课外补习班', '肝胆胰外科', '结直肠外科', '普通外科', '普胸外科', '乳腺外科', '神经外科', '胃肠外科', '血管外科', '心脏大血管外科', '肿瘤外科', '曾外祖父', '曾外祖母'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'coat;jacket': 'coat', 
            'in addition;furthermore': 'furthermore',
            'unexpected;surprised': 'unexpected',
            'grandfather (maternal)': 'maternal grandfather',
            'grandmother (maternal)': 'maternal grandmother',
            'foreign word;loanword': 'loanword', 
            'The Bund (Shanghai), historic waterfront area': 'The Bund, Shanghai',
            'grandson (daughter’s son)': "daughter's son",
            'granddaughter (daughter’s daughter)': "daughter's daughter",
            'nephew;sister’s son': "sister's son",
            'niece;sister’s daughter': "sister's daughter",
            'extramarital affair': 'affair'}

    }
,
    '手': {
        'shared_char': '手',
        'char_pinyin': 'shēng',
        'char_english': 'hand',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['智能手表', '手串', '松手', '浪漫杀手', '门诊手术室'],
        'n_words_per_video': 11,
        'current_part': 1,
        'text_replacements': {
            'glove;mitten': 'glove',
            'master;expert': 'expert',
            'rider;delivery person': 'delivery rider',
            'handrail;armrest': 'handrail',
            'to let go;letting go': 'let go',
            'manual;handbook': 'handbook',
            'handmade;manual': 'handmade',
            'palm (of hand)': 'palm',
            'gesture;signal;sign': 'gesture',
            'handgun;pistol': 'pistol',
            'video game controller;handle': 'video game controller'
            }
    }
,
    '生': {
        'shared_char': '生',
        'char_pinyin': 'shēng',
        'char_english': 'life',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': [
            '花生酱', '轻奢生活', '生育率', '独生女', '独生子', '博士生导师', '咖啡生产地',
            '出生率', '低生育率', '招生', '精神卫生科', '生效', '生产者名称'],
        'n_words_per_video': 12,
        'current_part': 1,
        'text_replacements': {
            'to produce;production': 'production',
            'lifestyle;way of life': 'lifestyle',
            'business (how doing)': 'business', 
            'physiological;physical': 'physiological'}
            },
    '地': {
        'shared_char': '地',
        'char_pinyin': 'dì',
        'char_english': 'land',
        'max_priority': 5,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['高德地图', '圣地亚哥', '房地产开发', '咖啡生产地', '优胜美地国家公园', '地中海', '危地马拉', '不自觉地'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'spit;spitting anywhere': 'spit anywhere',
            'grassland;field;lawn': 'grassland',
            }
            },
    '水': {
        'shared_char': '水',
        'char_pinyin': 'shuǐ',
        'char_english': 'water',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['水', '碱水', '碳水化合物', '桂林山水', '水晶虾饺', '水杯','生活水平', '吐口水', '苏打水'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'kettle;canteen;watering can': 'kettle',
            'dehydrated;dehydration': 'dehydration',
            '': '',
            }
    },
    '动': {
        'shared_char': '动',
        'char_pinyin': 'dòng',
        'char_english': 'move',
        'max_priority': 6,
        'min_adu': 3,
        'min_per': 3,
        'types_allowed': WORD_TYPES + PROPER_NOUN_TYPES,
        'sort_cols': ['priority', 'cat_v3', 'pinyin'],
        'sort_ascending': [True, True, True],
        'words_rmv': ['自动驾驶汽车', '中国移动', '哺乳动物', '两栖动物', '啮齿动物', '爬行动物', '电动工具', '电动汽车牌子', '疯狂动物城', '核心运动', '户外活动'],
        'n_words_per_video': 10,
        'current_part': 1,
        'text_replacements': {
            'to start (machine)': 'to start up',
            'impulse;urge;to have an urge': 'implulse',
            'immovable assets;real estate': 'immovable assets',
            'to beat;throb;pulse': 'to beat;pulsate',
            }
    },
}

def enhance_data_settings(data_settings):
    data_settings['output_path_base'] = 'output/shared_char_shorts/'
    data_settings['output_path'] = os.path.join(
        data_settings['output_path_base'],
        data_settings['shared_char']
    )
    data_settings['output_path_audio'] = os.path.join(
        data_settings['output_path'],
        'audio_files'
    )
    data_settings['output_path_images'] = os.path.join(
        data_settings['output_path'],
        'images'
    )
    return data_settings


def load_video_configs():
    BG_SIZE = (720, 1280)
    video_configs = {
        'bg_size': BG_SIZE,
        'bg_color': 'white',
        'text_color': 'black',

        'max_line_length': BG_SIZE[0] - 160,
        'decrease_font_step_size': 1,
        'font_path': '/System/Library/Fonts/STHeiti Medium.ttc',

        'highlight_rect_x_buffer': 24,
        'highlight_rect_color': [0, 255, 0],
        'highlight_rect_opacity': 0.5,

        'title_settings': {
            'x': 50,
            'y': 40,
            'spacing': 8,
            'align': 'center',
            'font_size': {'chinese': 48, 'pinyin': 32, 'english': 32},
            'fill': {'chinese': '#000000', 'pinyin': '#222222', 'english': '#222222'},
        },

        'words_settings': {
            'x': {'chinese': 50, 'pinyin': 185, 'english': 440},
            'max_line_length_buffer_size': {'chinese': 15, 'pinyin': 30, 'english': 60},
            'max_line_length': {},
            'y_gap': 50,
            'spacing': 56,
            'font_size': {'chinese': 32, 'pinyin': 32, 'english': 32},
            'align': {'chinese': 'left', 'pinyin': 'left', 'english': 'left'},
            'fill': {'chinese': '#000000', 'pinyin': '#000000', 'english': '#000000'},
        },

        'horizontal_line': {
            'y_gap': 20,
            'x': 10,
            'color': "#1E90FF",
            'width': 10,
        },

        'bottom_line': {
            'y_gap': 10,
            'x': 10,
            'color': "#1E90FF",
            'width': 10,
        },

        'logo': {
            'font_name': 'Arial Black',
            'font_size': 20,
            'x': BG_SIZE[0] - 50,
            'y': 1130,
            'color1': "#3E78D6",
            'color2': "#2FDDFC",
        },

        'category_index': {
            'index_value': 1,
            'index_total': 100,
            'font_name': 'Arial Black',
            'font_size': 48,
            'x': 240,
            'y': 1110,
            'color1': "#000000",
            'color2': "#777777",
        },
    }
    video_configs['horizontal_line']['y'] = video_configs['title_settings']['y'] + \
        video_configs['title_settings']['font_size']['chinese']+ \
        video_configs['title_settings']['font_size']['pinyin'] + \
        video_configs['title_settings']['font_size']['english'] + \
        video_configs['horizontal_line']['y_gap'] + \
        2*video_configs['title_settings']['spacing']

    video_configs['bottom_line']['y'] = video_configs['category_index']['y'] - \
        video_configs['bottom_line']['y_gap']

    video_configs['words_settings']['y'] = video_configs['horizontal_line']['y'] + \
        video_configs['words_settings']['y_gap']
    video_configs['words_settings']['max_line_length']['chinese'] = video_configs['words_settings']['x']['pinyin'] - video_configs['words_settings']['x']['chinese'] - video_configs['words_settings']['max_line_length_buffer_size']['chinese']
    video_configs['words_settings']['max_line_length']['pinyin'] = video_configs['words_settings']['x']['english'] - video_configs['words_settings']['x']['pinyin'] - video_configs['words_settings']['max_line_length_buffer_size']['pinyin']
    video_configs['words_settings']['max_line_length']['english'] = BG_SIZE[0] - video_configs['words_settings']['x']['english'] - video_configs['words_settings']['max_line_length_buffer_size']['english']
    return video_configs


def get_filtered_words(df_all_vocab, data_settings):
    if data_settings['shared_char'] is None:
        df_filtered = df_all_vocab[
            (df_all_vocab['type'].isin(data_settings['types_allowed'])) &
            (df_all_vocab['priority'] <= data_settings['max_priority']) &
            (~(df_all_vocab['adu'] < data_settings['min_adu'])) &
            (~(df_all_vocab['per'] < data_settings['min_per']))
        ].sort_values(by=data_settings['sort_cols'], ascending=data_settings['sort_ascending']).reset_index(drop=True)
    else:
        df_filtered = df_all_vocab[
            (df_all_vocab['chinese'].str.contains(data_settings['shared_char'])) &
            (df_all_vocab['type'].isin(data_settings['types_allowed'])) &
            (df_all_vocab['priority'] <= data_settings['max_priority']) &
            (~(df_all_vocab['adu'] < data_settings['min_adu'])) &
            (~(df_all_vocab['per'] < data_settings['min_per'])) &
            (~(df_all_vocab['chinese'].isin(data_settings['words_rmv'])))
        ].sort_values(data_settings['sort_cols'], ascending=data_settings['sort_ascending']).reset_index(drop=True)
    df_filtered = df_filtered.replace(data_settings['text_replacements'])
    return df_filtered


def get_character_counts(df_all_vocab, data_settings):
    data_settings2 = data_settings.copy()
    data_settings2['shared_char'] = None
    df_all_vocab_post_filtered = get_filtered_words(df_all_vocab, data_settings2)
    dict_character_appearances = defaultdict(list)
    for _, row in df_all_vocab_post_filtered.iterrows():
        for char in row['chinese']:
            dict_character_appearances['character'].append(char)
            dict_character_appearances['word'].append(row['chinese'])
            dict_character_appearances['word_idx'].append(row['id'])
    df_character_appearances = pd.DataFrame(dict_character_appearances)
    return df_character_appearances


def stitch_audios(audio_settings, data_settings, example_words):
    dict_audio_durations = defaultdict(list)
    if audio_settings['audio_plan'] == 'ctitle_c2word':
        current_start_time = 0

        # beginning pause
        pause_beginning = AudioSegment.silent(duration=audio_settings['pause_ms_beginning'])
        combined = pause_beginning
        dict_audio_durations['audio_path'].append('pause_beginning')
        dict_audio_durations['duration'].append(audio_settings['pause_ms_beginning'] / 1000)
        dict_audio_durations['start_time'].append(current_start_time)
        current_start_time += audio_settings['pause_ms_beginning'] / 1000
        dict_audio_durations['end_time'].append(current_start_time)

        # title
        title_audio_path = f"{data_settings['output_path_audio']}/{data_settings['shared_char']}.mp3"
        audio = AudioSegment.from_mp3(title_audio_path)
        combined += audio
        dict_audio_durations['audio_path'].append(title_audio_path)
        dict_audio_durations['duration'].append(audio.duration_seconds)
        dict_audio_durations['start_time'].append(current_start_time)
        current_start_time += audio.duration_seconds
        dict_audio_durations['end_time'].append(current_start_time)

        # words
        for _, word in enumerate(example_words):
            # inter-word pause
            pause_inter_word = AudioSegment.silent(duration=audio_settings['pause_ms_between'])
            combined += pause_inter_word
            dict_audio_durations['audio_path'].append('inter_word_pause')
            dict_audio_durations['duration'].append(audio_settings['pause_ms_between'] / 1000)
            dict_audio_durations['start_time'].append(current_start_time)
            current_start_time += audio_settings['pause_ms_between'] / 1000
            dict_audio_durations['end_time'].append(current_start_time)
            
            # word audio
            word_audio_path = f"{data_settings['output_path_audio']}/{word}.mp3"
            audio = AudioSegment.from_mp3(word_audio_path)
            combined += audio 
            dict_audio_durations['audio_path'].append(word_audio_path)
            dict_audio_durations['duration'].append(audio.duration_seconds)
            dict_audio_durations['start_time'].append(current_start_time)
            current_start_time += audio.duration_seconds
            dict_audio_durations['end_time'].append(current_start_time)

            # within-word pause
            pause_within_word = AudioSegment.silent(duration=audio_settings['pause_ms_within_word'])
            combined += pause_within_word
            dict_audio_durations['audio_path'].append('within_word_pause')
            dict_audio_durations['duration'].append(audio_settings['pause_ms_within_word'] / 1000)
            dict_audio_durations['start_time'].append(current_start_time)
            current_start_time += audio_settings['pause_ms_within_word'] / 1000
            dict_audio_durations['end_time'].append(current_start_time)

            # word again audio
            combined += audio 
            dict_audio_durations['audio_path'].append(word_audio_path)
            dict_audio_durations['duration'].append(audio.duration_seconds)
            dict_audio_durations['start_time'].append(current_start_time)
            current_start_time += audio.duration_seconds
            dict_audio_durations['end_time'].append(current_start_time)

    # export the combined audio file
    combined.export(f"{data_settings['output_path_audio']}/!combined_part{data_settings['current_part']}.mp3", format="mp3")
    print(f'Audio duration: {combined.duration_seconds:.1f}s')

    # Add in static slide audio into dataframe of audio durations
    df_durations = pd.DataFrame(dict_audio_durations)
    return df_durations


def draw_vocab_list_whole_image(video_configs, data_settings, df_filt, title_format='cpe'):
    original_img = Image.new("RGB", video_configs['bg_size'], color=video_configs['bg_color'])
    draw = ImageDraw.Draw(original_img)
    draw_logo(draw, video_configs)

    if title_format == 'cpe':
        title_text_settings = {}
        title_text_settings['chinese'] = {
            'text': data_settings['shared_char'],
            'font_path': video_configs['font_path'],
            'font_size': video_configs['title_settings']['font_size']['chinese'],
            'y': video_configs['title_settings']['y'],
            'spacing': video_configs['title_settings']['spacing'],
            'align': video_configs['title_settings']['align'],
            'fill': video_configs['title_settings']['fill']['chinese'],
            'max_line_length': video_configs['max_line_length'],
        }
        title_text_settings['pinyin'] = {
            'text': data_settings['char_pinyin'],
            'font_path': video_configs['font_path'],
            'font_size': video_configs['title_settings']['font_size']['pinyin'],
            'y': video_configs['title_settings']['y'] + video_configs['title_settings']['font_size']['chinese'] + video_configs['title_settings']['spacing'],
            'spacing': video_configs['title_settings']['spacing'],
            'align': video_configs['title_settings']['align'],
            'fill': video_configs['title_settings']['fill']['chinese'],
            'max_line_length': video_configs['max_line_length'],
        }
        title_text_settings['english'] = {
            'text': data_settings['char_english'],
            'font_path': video_configs['font_path'],
            'font_size': video_configs['title_settings']['font_size']['english'],
            'y': video_configs['title_settings']['y'] + video_configs['title_settings']['font_size']['chinese'] + video_configs['title_settings']['font_size']['pinyin'] + 2*video_configs['title_settings']['spacing'],
            'spacing': video_configs['title_settings']['spacing'],
            'align': video_configs['title_settings']['align'],
            'fill': video_configs['title_settings']['fill']['chinese'],
            'max_line_length': video_configs['max_line_length'],
        }
        draw_resized_text_on_image(draw, title_text_settings['chinese'], video_configs, is_centered=True)
        draw_resized_text_on_image(draw, title_text_settings['pinyin'], video_configs, is_centered=True)
        draw_resized_text_on_image(draw, title_text_settings['english'], video_configs, is_centered=True)
    else:
        draw_resized_text_on_image(draw, video_configs['title_text_settings'], video_configs, is_centered=True)


    # 4. Horizontal line
    draw.line([
        (video_configs['horizontal_line']['x'], video_configs['horizontal_line']['y']),
        (video_configs['bg_size'][0] - video_configs['horizontal_line']['x'], video_configs['horizontal_line']['y'])],
        fill=video_configs['horizontal_line']['color'],
        width=video_configs['horizontal_line']['width'],
        joint=None)
    draw.line([
        (video_configs['bottom_line']['x'], video_configs['bottom_line']['y']),
        (video_configs['bg_size'][0] - video_configs['bottom_line']['x'], video_configs['bottom_line']['y'])],
        fill=video_configs['bottom_line']['color'],
        width=video_configs['bottom_line']['width'],
        joint=None)
    
    # Write part number, if applicable
    if 'current_part' in data_settings:
        part_text_settings = {
            'text': f"Page\n{data_settings['current_part']}/{data_settings['n_parts']}",
            'font_path': 'Arial Black',
            'font_size': 32,
            'x': video_configs['bg_size'][0] - 150,
            'y': 80 - 40,
            'spacing': 4,
            'align': 'center',
            'fill': '#000000',
            'max_line_length': 300,
        }
        draw.circle(
            [video_configs['bg_size'][0] - 115, 80, 300, 300],
            outline="#000000",
            width=4,
            radius=60,
            fill=(255, 255, 255, 200),
        )
        draw_resized_text_on_image(draw, part_text_settings, video_configs, is_centered=False)

    # 5. Words
    for i_row, row in df_filt.iterrows():
        # Chinese
        text_settings = {
            'text': row['chinese'],
            'font_path': video_configs['font_path'],
            'font_size': video_configs['words_settings']['font_size']['chinese'],
            'x': video_configs['words_settings']['x']['chinese'],
            'y': video_configs['words_settings']['y'] + i_row * (video_configs['words_settings']['font_size']['chinese'] + video_configs['words_settings']['spacing']),
            'spacing': video_configs['words_settings']['spacing'],
            'align': video_configs['words_settings']['align']['chinese'],
            'fill': video_configs['words_settings']['fill']['chinese'],
            'max_line_length': video_configs['words_settings']['max_line_length']['chinese'],
        }
        draw_resized_text_on_image(draw, text_settings, video_configs)

        # Pinyin
        text_settings = {
            'text': row['pinyin'],
            'font_path': video_configs['font_path'],
            'font_size': video_configs['words_settings']['font_size']['pinyin'],
            'x': video_configs['words_settings']['x']['pinyin'],
            'y': video_configs['words_settings']['y'] + i_row * (video_configs['words_settings']['font_size']['chinese'] + video_configs['words_settings']['spacing']),
            'spacing': video_configs['words_settings']['spacing'],
            'align': video_configs['words_settings']['align']['pinyin'],
            'fill': video_configs['words_settings']['fill']['pinyin'],
            'max_line_length': video_configs['words_settings']['max_line_length']['pinyin'],
        }
        draw_resized_text_on_image(draw, text_settings, video_configs)

        # English
        text_settings = {
            'text': row['english'],
            'font_path': video_configs['font_path'],
            'font_size': video_configs['words_settings']['font_size']['english'],
            'x': video_configs['words_settings']['x']['english'],
            'y': video_configs['words_settings']['y'] + i_row * (video_configs['words_settings']['font_size']['chinese'] + video_configs['words_settings']['spacing']),
            'spacing': video_configs['words_settings']['spacing'],
            'align': video_configs['words_settings']['align']['english'],
            'fill': video_configs['words_settings']['fill']['english'],
            'max_line_length': video_configs['words_settings']['max_line_length']['english'],
        }
        draw_resized_text_on_image(draw, text_settings, video_configs)

    no_hl_img_file_path = f"{data_settings['output_path_images']}/no_highlights.png"
    original_img.save(no_hl_img_file_path)
    return no_hl_img_file_path


def create_video_without_highlights(data_settings, video_configs, no_hl_img_file_path):
    combined_audio = AudioFileClip(f"{data_settings['output_path_audio']}/!combined_part{data_settings['current_part']}.mp3")
    clips_no_highlights = [ImageClip(no_hl_img_file_path, duration=combined_audio.duration).with_start(0)]
    video = CompositeVideoClip(clips_no_highlights, size=video_configs['bg_size'])
    video.audio = combined_audio
    video.duration = combined_audio.duration
    no_highlights_video_path = f"{data_settings['output_path']}/{data_settings['shared_char']}_no_highlights_part{data_settings['current_part']}.mp4"
    video.write_videofile(no_highlights_video_path, fps=24)
    

def create_video_with_highlights(df_durations, audio_settings, data_settings, video_configs, method_to_determine_highlight_timing='inter_word_pause', highlight_start_ids=None):
    # Compute highlight durations
    if method_to_determine_highlight_timing=='inter_word_pause':
        highlight_start_ids = [1+x for x in df_durations[df_durations['audio_path']=='inter_word_pause'].index.tolist()]
        highlight_end_ids = [2+x for x in highlight_start_ids]
    else:
        highlight_end_ids = [2+x for x in highlight_start_ids]

    dict_highlight_durations = defaultdict(list)
    for i_row, row in df_durations.iterrows():
        if i_row in highlight_start_ids:
            dict_highlight_durations['start_time'].append(row['start_time'] - audio_settings['pause_ms_within_word']/(2*1000))
        if i_row in highlight_end_ids:
            dict_highlight_durations['end_time'].append(row['end_time'] + audio_settings['pause_ms_within_word']/(2*1000))
    df_highlight_durations = pd.DataFrame(dict_highlight_durations)
    df_highlight_durations['duration'] = df_highlight_durations['end_time'] - df_highlight_durations['start_time']

    no_highlights_video_path = f"{data_settings['output_path']}/{data_settings['shared_char']}_no_highlights_part{data_settings['current_part']}.mp4"
    video = VideoFileClip(no_highlights_video_path)
    clips_with_highlights = [video]

    rect_width = video_configs['bg_size'][0] - 2*video_configs['words_settings']['max_line_length_buffer_size']['english'] + 2*video_configs['highlight_rect_x_buffer']
    rect_height = video_configs['words_settings']['font_size']['chinese'] + video_configs['words_settings']['spacing']
    rect_x = video_configs['words_settings']['max_line_length_buffer_size']['english'] - video_configs['highlight_rect_x_buffer']
    for i_row, row in df_highlight_durations.iterrows():
        rect_y = video_configs['words_settings']['y'] - \
            (video_configs['words_settings']['spacing']/2) + \
            i_row*(video_configs['words_settings']['spacing'] + video_configs['words_settings']['font_size']['chinese'])
        rect = (ColorClip(size=(rect_width, rect_height), color=video_configs['highlight_rect_color'], duration=row['duration'])
                .with_start(row['start_time'])
                .with_opacity(video_configs['highlight_rect_opacity'])
                .with_position((rect_x, rect_y)))
        clips_with_highlights.append(rect)

    # Overlay the rectangle on the video
    final_video = CompositeVideoClip(clips_with_highlights)
    final_video.write_videofile(f"{data_settings['output_path']}/{data_settings['shared_char']}_part{data_settings['current_part']}.mp4", codec="libx264")
