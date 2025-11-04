# Basic video info - not used in program  # UPDATE ON NEW VIDEO
video_name = '20 male virtues from social media: Chinese listening practice (+English translations)'
video_description = '''
This video was made for practicing both listening comprehension and character recognition.

The Chinese text comes from a popular post on Chinese social media, and English translations and pinyin are provided. 

Because these videos are programmatically generated, the format is customizable to quickly produce alternate formats, so please let me know if you have any corrections, suggestions, feedback, or questions, please leave a comment.

Python code to produce this video: https://github.com/srcole/my_mandarin_database
'''

# Main settings  # UPDATE ON NEW VIDEO
video_number = '32'
data_settings = {
    'recording_id': 'conly',
    'filename_suffix': 'male_virtues',
    'voice_name_zh': 'zh-CN-XiaoyuMultilingualNeural',
    # 'voice_name_zh': 'zh',
    'different_file_name': 'static/texts/lists/20251028_malevirtues.csv',
    'sort_keys': ['index'],
    'sort_asc': [True],
    'pause_between_words_ms': 1000,
    'pause_start_ms': 200,
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
    'global_n_lines_max': 6,

    'vocab_font_sizes': {
        'words': 30
    },
    'word_index': {
        'font_name': 'Arial Black',
        'font_size': 36,
        'x': 30,
        'y': 30,
        'color1': "#000000",
        'color2': "#777777",
    },
    'previous_word': {
        'font_name': hanzi_font_path,
        'font_size': 12,
        'spacing': 6,
        'line_length': 1100,
        'n_lines_max': 4,
        'x': 20,
        'y': 75,
        'color': "#777777",
    },
    'logo': {
        'font_name': 'Arial Black',
        'font_size': 20,
        'x': 40,
        'y': 40,
        'color1': "#000080",
        'color2': "#1E90FF",
    },
    'footer_line': {
        'y': 100,
        'x': 10,
        'color': "#1E90FF",
        'width': 4,
    },

    'vocab_slide': {
        'chinese': {
            'y': 110,
            'font_size': 48,
            'spacing': 25,
            },
        'english': {
            'y': 450,
            'font_size': 45,
            'spacing': 20,
            },
    },

    # Video icon
    'icon_configs': {
        'file_suffix': '_chinese', # UPDATE ON NEW VIDEO
        'word': '必须点赞老婆的每一条朋友圈 老婆的自拍必须夸奖', # UPDATE ON NEW VIDEO
        'border_color_hex': "#1E90FF",
        'border_width': 30,
    },
}

# Non-vocab slide configs
subtitle = {
    'chinese': '网友的男德经',
    'pinyin': 'wǎngyǒu de nán dé jīng',
    'english': "Internet guide to Male Virtue"
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
        'video_structure': ('News spoken in Chinese + English translations', '中文新闻+英文翻译'),
        'count_str': ("", ""),
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

    'outro': {
        'chinese': '如果你有任何问题、建议或反馈，请留言。请点赞并订阅。',
        'pinyin': 'Rúguǒ nǐ yǒu rènhé wèntí, jiànyì huò fǎnkuì, qǐng liúyán. Qǐng diǎn zàn bìng dìngyuè.',
        'english': 'If you have any questions, suggestions, or feedback, please leave a comment. Please like and subscribe.',
        'clip_index': -1,
        'change_index': None,
        'pause_ms': 500,

        'y_top': 20,
        'y_bottom': 80,
        'x_top': 20,
        'spacing': 6,
        'font_size': 24,
        'fill': '#000000',
        'align': 'left',
        'col_space': 5,
        'col_space_big': 10,
        'definition_configs':{
            'chinese': {'x_offset': 0, 'x_max': 450, 'font_path': hanzi_font_path},
            'english': {'x_offset': None, 'x_max': 800, 'font_path': hanzi_font_path},
        }
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
