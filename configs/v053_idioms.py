from constants import IDIOM_TYPES

# Main settings  # UPDATE ON NEW VIDEO
video_number = '53'
data_settings = {
    'recording_id': 'ce_csent',
    'filename_suffix': 'idioms',
    'voice_name_zh': 'zh-CN-XiaoxiaoNeural',
    'voice_name_en': 'en-US-AvaMultilingualNeural',
    'min_priority': 1, 'max_priority': 7,
    'silent_components': True,
    'video_notes_column': 'idiom_literal',
    'min_known_english_prompt': 1, 'max_known_english_prompt': 5,
    'types_allowed': IDIOM_TYPES,
    'pause_between_words_ms': 800,
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
    'slang_icon_max': -1,

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
        'color': "#666666",
    },
    'previous_sent': {
        'font_name': hanzi_font_path,
        'font_size': 18,
        'spacing': 6,
        'y': 75,
        'color': "#666666",
    },
    'footer_line': {
        'y': 100,
        'x': 10,
        'color': "#1E90FF",
        'width': 4,
    },

    'vocab_slide': {
        'chinese': {
            'y': 80,
            'n_lines_max': 1,
            },
        'video_notes': {
            'y': 220,
            'font_size': 28,
            'fill': "#333333",
            'spacing': 3,
            'n_lines_max': 6,
            'video_notes_slide_index': 1,
            },
        'english': {
            'y': 145,
            'n_lines_max': 1,
            },
        'sentence_chinese': {
            'y': 440,
            'font_size': 40,
            'n_lines_max': 1,
            },
        'sentence_pinyin': {
            'y': 500,
            'font_size': 35,
            'n_lines_max': 1,
            },
        'sentence_english': {
            'y': 550,
            'font_size': 35,
            'n_lines_max': 1,
            },
    },
}

# Non-vocab slide configs
subtitle = {
    'chinese': '成语,谚语,和比喻',
    'pinyin': 'chéng yǔ, yàn yǔ, hé bǐyù',
    'english': 'idioms, proverbs, and metaphors',
    }  # UPDATE ON NEW VIDEO
video_structure_tup = ('Chinese first, English second\nExample Chinese sentences', '先中文，后英文\n并附中文例句')
count_str_tup = ("{n_vocab_words} phrases", "{n_vocab_words}个词")
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
        'video_structure': video_structure_tup,
        'count_str': count_str_tup,
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
            'fill': "#333333",
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

        'y_top': 10,
        'y_bottom': 70,
        'x_top': 10,
        'spacing': 0,
        'font_size': 14,
        'fill': '#000000',
        'align': 'left',
        'col_space': 0,
        'col_space_big': 0,
        'definition_configs':{
            'chinese': {'x_offset': 0, 'x_max': 90, 'font_path': hanzi_font_path},
            'english': {'x_offset': None, 'x_max': 165, 'font_path': hanzi_font_path},
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
