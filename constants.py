from datetime import date

WORD_TYPES = ['combo', 'no combo', 'two word', 'prefix', 'single char', 'suffix', 'abbreviation']
PHRASE_TYPES = ['phrase', 'part sent', 'phrase_save', 'speak_phrase', 'saying', 'idiom', 'slang', 'signs', 'signs_uncommon']
SENT_TYPES = ['sentence']
PROPER_NOUN_TYPES = ['proper noun']
IDIOM_TYPES = ['idiom']
ALL_TYPES = WORD_TYPES + PHRASE_TYPES + SENT_TYPES + PROPER_NOUN_TYPES + IDIOM_TYPES
default_settings = {
    'min_priority': 1, 'max_priority': 4,
    'min_known_english_prompt': 1, 'max_known_english_prompt': 6,
    'min_known_pinyin_prompt': 1, 'max_known_pinyin_prompt': 6,
    'sort_keys': ['category1', 'category2', 'pinyin'],
    'sort_asc': [True, True, True],
    'types_allowed': ALL_TYPES,
    'min_combo_quality': 6,
    'categories_allowed': None,
    'categories2_allowed': None,
    'cat1_values_allowed': None,
    'types_allowed_str': '',
    'min_adu': 1,
    'min_per': 1,
    'min_date': '2025-01-01',
    'filename_suffix': '',
    'contains_character': None,
    'exclude_words': None,
    'max_count': 1000000,
}
