import os

OUTPUT_BASE_PATH = 'output/lt_shorts/'

audio_settings = {
    'voice_name_zh': 'zh-CN-XiaoxiaoNeural',
    'audio_plan': 'cparts_ce_csent',
    'pause_ms_beginning': 100,
    'pause_ms_within': 250,
    'pause_ms_between': 600,
}

lt_shorts_categories = {
    '动物分类': {
        'chinese': '动物分类',
        'pinyin': 'dòngwù fēnlèi',
        'english': 'Animal Classification',
        'vocab_list': ['哺乳动物', '两栖动物', '爬行动物']
    },
    '动物分类2': {
        'chinese': '星球',
        'pinyin': 'xīng qiú',
        'english': 'planet',
        'vocab_list': ['地球', '火星', '金星', '水星', '木星', '土星', '天王星', '海王星', '冥王星']
    },
}

def load_data_settings(current_category_dict):
    data_settings = current_category_dict.copy()
    data_settings['output_path'] = os.path.join(
        OUTPUT_BASE_PATH,
        current_category_dict['chinese'].replace(' ', '_')
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


def create_directories(data_settings):
    if not os.path.exists(OUTPUT_BASE_PATH):
        os.mkdir(OUTPUT_BASE_PATH)
    if not os.path.exists(data_settings['output_path']):
        os.mkdir(data_settings['output_path'])
    if not os.path.exists(data_settings['output_path_audio']):
        os.mkdir(data_settings['output_path_audio'])
    if not os.path.exists(data_settings['output_path_images']):
        os.mkdir(data_settings['output_path_images'])


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
        'highlight_rect_y_buffer': 10,
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
            'x': 50,
            'y_gap': 30,
            'between_words_spacing': 30,
            'component_words_to_vocab_word_spacing': 16,
            'vocab_word_to_sentence_spacing': 20,
            'font_size': {'components': 32, 'vocab_word': 32, 'sentence': 32},
            'spacing': {'components': 5, 'sentence': 10},
            'fill': {'components': '#555555', 'vocab_word': '#000000', 'sentence': '#000000'},
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
            'y': 1110,
            'color1': "#3E78D6",
            'color2': "#2FDDFC",
        },

        'category_index': {
            'index_value': 1,
            'index_total': 100,
            'font_name': 'Arial Black',
            'font_size': 48,
            'x': 200,
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
    return video_configs
