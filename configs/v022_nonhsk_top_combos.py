from constants import WORD_TYPES

# Basic video info - not used in program  # UPDATE ON NEW VIDEO
video_name = '19 of the most useful HSK 5 words: breakdown by hanzi + Chinese-English example sentences in 2 minutes'
video_description = '''
TODO
Because these videos are programmatically generated, the format is customizable to quickly produce alternate formats with different vocabulary categories, so please let me know if you have any corrections, suggestions, feedback, or questions, please leave a comment.

Python code to produce this video: https://github.com/srcole/my_mandarin_database
'''

# Main settings  # UPDATE ON NEW VIDEO
video_number = '22'
data_settings = {
    'recording_id': 'ec_csent_scombo',
    'filename_suffix': 'hsk5_top_scombos',
    'voice_name_zh': 'zh-CN-XiaoyuMultilingualNeural',
    'voice_name_en': 'en-US-AvaMultilingualNeural',
    'pause_between_words_ms': 1000,
    'min_priority': 1, 'max_priority': 1,
    'min_combo_quality': 3,
    'types_allowed': WORD_TYPES,
    'pause_between_words_ms': 800,
    'pause_start_ms': 200,
    'hsk_levels_allowed': ['5'],
    'min_adu': 5,
    'min_per': 5,
}


# Misc properties
output_path = 'output/videos/'
hanzi_font_path = '/System/Library/Fonts/STHeiti Medium.ttc'
DEFAULT_TEXT_PROPERTIES = {
    'font_path': hanzi_font_path,
    'fill': 'black',
    'spacing': 30,
    'align': 'center',
    'font_size': 50,
}

# Aesthetic configs
video_configs = {
    'bg_size': (1280, 720),
    'bg_color': 'white',
    'text_color': 'black',
    'max_line_length_buffer_size': 60,
    'decrease_font_step_size': 1,

    'vocab_font_sizes': {
        'words': 50,
        'components': 40,
        'sent_chinese': 50,
        'sent': 45
    },
    'word_index': {
        'font_name': 'Arial Black',
        'font_size': 36,
        'x': 30,
        'y': 30,
        'color1': "#000000",
        'color2': "#777777",
    },
    'logo': {
        'font_name': 'Arial Black',
        'font_size': 20,
        'x': 40,
        'y': 40,
        'color1': "#000080",
        'color2': "#1E90FF",
    },
    'previous_word': {
        'font_name': hanzi_font_path,
        'font_size': 18,
        'spacing': 6,
        'x': 40,
        'y': 75,
        'color': "#777777",
    },
    'previous_sent': {
        'font_name': hanzi_font_path,
        'font_size': 18,
        'spacing': 6,
        'y': 75,
        'color': "#777777",
    },
    'footer_line': {
        'y': 100,
        'x': 10,
        'color': "#1E90FF",
        'width': 4,
    },
    'sentence_line': {
        'y': 340,
        'x': 30,
        'color': "#000000",
        'width': 5,
    },

    'vocab_slide': {
        'chinese': {
            'y': 60,
            },
        'english': {
            'y': 140,
            },
        'component_words': {
            'y': 210,
            'font_size': 38,
            'spacing': 8,
            },
        'sentence_chinese': {
            'y': 380,
            'font_size': 40,
            },
        'sentence_pinyin': {
            'y': 450,
            'font_size': 35,
            },
        'sentence_english': {
            'y': 530,
            'font_size': 35,
            },
    },

    # Video icon
    'icon_configs': {
        'file_suffix': '_sentence_english', # UPDATE ON NEW VIDEO
        'word': '更新', # UPDATE ON NEW VIDEO
        'border_color_hex': "#1E90FF",
        'border_width': 30,
    },
}

# Non-vocab slide configs
subtitle = {
    'chinese': '实用的HSK5词汇',
    'pinyin': 'shíyòng de HSK5 cíhuì',
    'english': 'Useful HSK 5 words'
    }  # UPDATE ON NEW VIDEO
nonvocab_slides = {
    'intro': {
        'chinese': f"我的普通话数据库视频 {video_number}",
        'pinyin': f"wǒ de pǔtōnghuà shùjùkù shìpín {video_number}",
        'english': f"My Mandarin Chinese Database Video {video_number}",
        'clip_index': 0,
        'change_index': -2,
        'pause_ms': 500,

        'channel_title': ('My Mandarin Database', '我的普通话数据库'),
        'video_number': (f'Video #{video_number}', f'视频#{video_number}'),
        'video_name': (subtitle['english'], subtitle['chinese']),
        'video_structure': ('English first, Chinese second\nExample Chinese sentences', '先英文，后中文\n并附中文例句'),
        'count_str': ("{n_vocab_words} words", "{n_vocab_words}个词汇"),
        'duration_str': ('{audio_duration_minutes:.0f} minutes', '{audio_duration_minutes:.0f}分钟'),
        'feedback': ('If you have any questions, suggestions, or feedback\nplease leave a comment', '如果你有任何问题、建议或反馈\n请留言'),

        'x_bias_english_side': 80,
        'text_configs': [
            {
            'font_name': hanzi_font_path,
            'font_size': 32,
            'y': 100,
            'spacing': 20,
            'align': 'center',
            'fill': "#000000",
            },
            {
            'font_name': hanzi_font_path,
            'font_size': 24,
            'y': 300,
            'spacing': 10,
            'align': 'center',
            'fill': "#555555",
            },
            ]
    },

    'word_list': {
        'chinese_unfill': '{audio_duration_minutes:.0f}分钟, {n_vocab}个单词',
        'pinyin_unfill': '{audio_duration_minutes:.0f} fēnzhōng, {n_vocab} gè dāncí',
        'english_unfill': '{audio_duration_minutes:.0f} minutes, {n_vocab} words',
        'clip_index': 1,
        'change_index': -1,
        'pause_ms': 500,

        'y_top': 40,
        'y_bottom': 150,
        'x_top': 20,
        'spacing': 10,
        'font_size': 26,
        'fill': '#000000',
        'align': 'left',
        'col_space': 10,
        'col_space_big': 20,
        'definition_configs':{
            'chinese': {'x_offset': 0, 'x_max': 100, 'font_path': hanzi_font_path},
            'pinyin': {'x_offset': None, 'x_max': 200, 'font_path': hanzi_font_path},
            'english': {'x_offset': None, 'x_max': 290, 'font_path': hanzi_font_path},
        },
    },

    'outro': {
        'chinese': '如果你有任何问题、建议或反馈，请留言。请点赞并订阅。',
        'pinyin': 'Rúguǒ nǐ yǒu rènhé wèntí, jiànyì huò fǎnkuì, qǐng liúyán. Qǐng diǎn zàn bìng dìngyuè.',
        'english': 'If you have any questions, suggestions, or feedback, please leave a comment. Please like and subscribe.',
        'clip_index': -1,
        'change_index': None,
        'pause_ms': 500,

        'y_top': 40,
        'y_bottom': 150,
        'x_top': 20,
        'spacing': 10,
        'font_size': 26,
        'fill': '#000000',
        'align': 'left',
        'col_space': 10,
        'col_space_big': 20,
        'definition_configs':{
            'chinese': {'x_offset': 0, 'x_max': 100, 'font_path': hanzi_font_path},
            'pinyin': {'x_offset': None, 'x_max': 200, 'font_path': hanzi_font_path},
            'english': {'x_offset': None, 'x_max': 290, 'font_path': hanzi_font_path},
        },
    }
}

subtitle_text_configs = {
    'font_size': 20,
    'font_name': hanzi_font_path,
    'y': 640,
    'spacing': 5,
    'align': 'center',
    'fill': "#000000",
}
