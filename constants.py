from datetime import date

WORD_TYPES = ['word', 'prefix', 'suffix', 'abbreviation', 'multi_word', 'verb_ending']
PHRASE_TYPES = ['phrase', 'speak_phrase', 'saying', 'idiom', 'modal particle']
SENT_TYPES = ['sentence']
PROPER_NOUN_TYPES = ['proper noun']
IDIOM_TYPES = ['idiom']
ALL_TYPES = WORD_TYPES + PHRASE_TYPES + SENT_TYPES + PROPER_NOUN_TYPES
NON_SENTENCE_TYPES = WORD_TYPES + PHRASE_TYPES + PROPER_NOUN_TYPES
default_settings = {
    'min_priority': 1, 'max_priority': 4,
    'min_known_english_prompt': 1, 'max_known_english_prompt': 6,
    'min_known_pinyin_prompt': 1, 'max_known_pinyin_prompt': 6,
    'sort_keys': ['cat_v3', 'cat2_v3', 'category1', 'category2', 'pinyin'],
    'sort_asc': [True, True, True, True, True],
    'types_allowed': ALL_TYPES,
    'min_combo_quality': 10,
    'categories_allowed': None,
    'categories_not_allowed': None,
    'categories2_allowed': None,
    'categories2_not_allowed': None,
    'cat_v3_allowed': None,
    'cat_v3_not_allowed': None,
    'cat2_v3_allowed': None,
    'cat2_v3_not_allowed': None,
    'source1_values_allowed': None,
    'types_allowed_str': '',
    'min_adu': 3,
    'min_per': 3,
    'min_date': '2025-01-01',
    'max_date': '2095-01-01',
    'filename_suffix': '',
    'contains_character': None,
    'exclude_words': None,
    'max_count': 1000000,
    'different_file_name': None,
    'custom_filters': None,
    'pause_between_words_ms': 800,
    'pause_start_ms': 200,
    'hsk_levels_allowed': None,
    'voice_name_zh': 'zh-CN-XiaoxiaoNeural',
    'voice_name_en': 'en-US-AvaMultilingualNeural',
    'voice_name_zh_backups': {
        'v2': 'zh-CN-XiaoxiaoNeural'
        },
    'voice_name_en_backups': {
        'v2': 'en-US-MichelleNeural'
        },
    'silent_components': False,
}

default_video_configs = {
    'bg_size': (1280, 720),
    'bg_color': 'white',
    'text_color': 'black',
    'max_line_length_buffer_size': 60,
    'decrease_font_step_size': 1,

    'slang_icon_max': 2,
    'slang_icon_xy': (40, 40),

    'phonetic_icon_max': 2,
    'phonetic_icon_xy': (40, 40),
}
