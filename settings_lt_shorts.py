import os

audio_settings = {
    'voice_name_zh': 'zh-CN-XiaoxiaoNeural',
    'audio_plan': 'ctitle_c2word',
    'pause_ms_beginning': 150,
    'pause_ms_within_word': 200,
    'pause_ms_between': 500,
}


def load_data_settings(df_categories, chosen_category):
    data_settings = {
        'category': chosen_category,
        'output_path_base': 'output/anomia_shorts/'
    }
    data_settings['output_path'] = os.path.join(
        data_settings['output_path_base'],
        data_settings['category'].replace(' ', '_')
    )
    data_settings['output_path_audio'] = os.path.join(
        data_settings['output_path'],
        'audio_files'
    )
    data_settings['output_path_images'] = os.path.join(
        data_settings['output_path'],
        'images'
    )

    this_category = df_categories[df_categories['chinese'] == data_settings['category']].iloc[0]
    data_settings['category_pinyin'] = this_category['pinyin']
    data_settings['category_english'] = this_category['english']
    data_settings['category_id'] = this_category['id']
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
            'y': 70,
            'spacing': 18,
            'align': 'center',
            'font_size': {'chinese': 70, 'pinyin': 50, 'english': 50},
            'fill': {'chinese': '#000000', 'pinyin': '#222222', 'english': '#222222'},
        },

        'words_settings': {
            'x': {'chinese': 50, 'pinyin': 185, 'english': 440},
            'max_line_length_buffer_size': {'chinese': 15, 'pinyin': 30, 'english': 60},
            'max_line_length': {},
            'y_gap': 50,
            'spacing': 40,
            'font_size': {'chinese': 32, 'pinyin': 32, 'english': 32},
            'align': {'chinese': 'left', 'pinyin': 'left', 'english': 'left'},
            'fill': {'chinese': '#000000', 'pinyin': '#000000', 'english': '#000000'},
        },

        'horizontal_line': {
            'y_gap': 40,
            'x': 10,
            'color': "#1E90FF",
            'width': 10,
        },

        'bottom_line': {
            'y_gap': 20,
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
    video_configs['words_settings']['max_line_length']['chinese'] = video_configs['words_settings']['x']['pinyin'] - video_configs['words_settings']['x']['chinese'] - video_configs['words_settings']['max_line_length_buffer_size']['chinese']
    video_configs['words_settings']['max_line_length']['pinyin'] = video_configs['words_settings']['x']['english'] - video_configs['words_settings']['x']['pinyin'] - video_configs['words_settings']['max_line_length_buffer_size']['pinyin']
    video_configs['words_settings']['max_line_length']['english'] = BG_SIZE[0] - video_configs['words_settings']['x']['english'] - video_configs['words_settings']['max_line_length_buffer_size']['english']
    return video_configs