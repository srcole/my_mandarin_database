from constants import ALL_TYPES

# Basic video info - not used in program
video_name = '21 common Chinese apps - name explanations'
video_description = '''
This video was made for quickly reviewing popular Chinese apps, practicing both listening comprehension and character recognition.
The Chinese is spoken first, followed by the english, and an example sentence in Chinese.
Words may come from HSK1, HSK2, HSK3, HSK4, HSK5, or above.
Because these videos are programmatically generated, the format is customizable to quickly produce alternate formats with different vocabulary categories.
See the code used to produce this video at https://github.com/srcole/my_mandarin_database.
If you have any corrections, suggestions, feedback, or questions, please leave a comment.
'''

# Main settings
data_settings = {
    'recording_id': 'ceword_components_csent',
    'filename_suffix': 'app_names',
    'min_combo_quality': 5,
    'categories2_allowed': ['app'],
    'types_allowed': ALL_TYPES,
}
video_number = '7'


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
    'decrease_font_step_size': 2,
    # TODO - finish

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
        'x': 40,
        'y': 75,
        'color': "#777777",
    },
    'previous_sent': {
        'font_name': hanzi_font_path,
        'font_size': 18,
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
        'y': 330,
        'x': 30,
        'color': "#000000",
        'width': 5,
    },

    'vocab_slide': {
        'chinese': {
            'y': 60,
            },
        'component_words': {
            'y': 140,
            'spacing': 10,
            'font_size': 32,
            },
        'english': {
            'y': 250,
            },
        'sentence_chinese': {
            'y': 380,
            'font_size': 40,
            },
        'sentence_pinyin': {
            'y': 440,
            'font_size': 35,
            },
        'sentence_english': {
            'y': 490,
            'font_size': 35,
            },
    },
}

# Video icon
icon_configs = {
    'file_suffix': '_sentence_english',
    'word': '微博',
    'border_color_hex': "#1E90FF",
    'border_width': 30,
}

# Non-vocab slide configs
subtitle_1 = {'chinese': '中国应用', 'pinyin': 'Zhōngguó yìngyòng', 'english': 'Chinese apps'}
subtitle_2 = {'chinese': '名字解释', 'pinyin': 'Míngzì jiěshì', 'english': 'names explanation'}
nonvocab_slides = {
    'intro': {
        'chinese': f"欢迎观看我的普通话数据库视频 {video_number}: {subtitle_1['chinese']}: {subtitle_2['chinese']}",
        'pinyin': f"Huānyíng guānkàn wǒ de pǔtōnghuà shùjùkù shìpín {video_number}: {subtitle_1['pinyin']}: {subtitle_2['pinyin']}",
        'english': f"Welcome to my Mandarin Chinese Database Video {video_number}: {subtitle_1['english']}: {subtitle_2['english']}",
        'clip_index': 0,
        'change_index': -2,
        'pause_ms': 500,

        'channel_title': ('My Mandarin Database', '我的普通话数据库'),
        'video_number': (f'Video #{video_number}', f'视频#{video_number}'),
        'video_name': (f"{subtitle_1['english']}: {subtitle_2['english']}", f"{subtitle_1['chinese']}: {subtitle_2['chinese']}"),
        'video_structure': ('Chinese first, English second\nExample sentences', '先中文，后英文\n并附例句'),
        'count_str': ("{n_vocab_words} words", "{n_vocab_words}个词汇"),
        'duration_str': ('{audio_duration_minutes:.0f} minutes', '{audio_duration_minutes:.0f}分钟'),
        'feedback': ('If you have any questions, suggestions, or feedback\nplease leave a comment', '如果你有任何问题、建议或反馈\n请留言'),

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
        'chinese_unfill': '这些是将在接下来的{audio_duration_minutes:.0f}分钟内复习的{n_vocab}个单词',
        'pinyin_unfill': 'Zhèxiē shì jiàng zài jiē xiàlái de {audio_duration_minutes:.0f} fēnzhōng nèi fùxí de {n_vocab} gè dāncí',
        'english_unfill': 'These are the {n_vocab} words that will be reviewed over the next {audio_duration_minutes:.0f} minutes',
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
    },
}

subtitle_text_configs = {
    'font_size': 22,
    'font_name': hanzi_font_path,
    'y': 600,
    'spacing': 20,
    'align': 'center',
    'fill': "#000000",
}
