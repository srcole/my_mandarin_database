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
    '行星': {
        'chinese': '行星',
        'pinyin': 'xíng xīng',
        'english': 'planet',
        'vocab_list': [
            ['水星', '金星', '地球'],
            ['火星', '木星', '土星'],
            ['天王星', '海王星', '冥王星']
            ]
    },
    '动物': {
        'chinese': '动物',
        'pinyin': 'dòng wù',
        'english': 'animals',
        'vocab_list': [
            ['猫头鹰', '老鹰', '猎鹰'],
            ['天鹅', '火烈鸟', '孔雀'],
            ['母鸡', '公鸡', '企鹅']
            ]
    },



    '啮齿动物': {
        'chinese': '啮齿动物',
        'pinyin': 'niè chǐ dòng wù',
        'english': 'rodents',
        'vocab_list': [
            ['仓鼠', '豚鼠', '松鼠'],
            ['田鼠', '袋鼠', '花栗鼠']
            ]
    },
    '昆虫': {
        'chinese': '昆虫',
        'pinyin': 'kūn chóng',
        'english': 'insects',
        'vocab_list': [
            ['臭虫', '吸血虫', '放屁虫'],
            ['甲虫', '白蚁', '毛毛虫'],
            ]
    },
    '野生动物': {
        'chinese': '野生动物',
        'pinyin': 'yě shēng dòng wù',
        'english': 'wild animals',
        'vocab_list': [
            ['斑马', '无尾熊', '狗熊'],
            ['长颈鹿', '熊猫', '羊驼'],
            ['黑猩猩', '大猩猩', '美洲虎'],
            ['山羊', '郊狼', '野牛'],
            ['龙猫', '鸭嘴兽', '眼镜蛇'],
            ['浣熊', '河狸', '水牛'],
            ['河马', '海象', '犀牛']
            ]
    },
    '爬行动物': {
        'chinese': '爬行动物',
        'pinyin': 'pá xíng dòng wù',
        'english': 'reptiles',
        'vocab_list': ['壁虎', '变色龙', '响尾蛇']
    },
    '狗品种': {
        'chinese': '狗品种',
        'pinyin': 'gǒu pǐn zhǒng',
        'english': 'dog breeds',
        'vocab_list': [
            ['柴犬', '金毛', '斗牛犬'],
            ['贵宾犬', '博美', '比熊'],
            ['边境牧羊犬', '德国牧羊犬', '母狗']
            ]
    },
    '水生动物': {
        'chinese': '水生动物',
        'pinyin': 'shuǐ shēng dòng wù',
        'english': 'acquatic animals',
        'vocab_list': [
            ['水母', '龙虾', '八爪鱼'],
            ['食人鱼', '河豚', '海豚']
            ]
    },
    '宠物': {
        'chinese': '宠物',
        'pinyin': 'chǒng wù',
        'english': 'pets',
        'vocab_list': [
            ['兽医', '绝育', '项圈'],
            ['毛皮', '翻肚皮', '抚摸'],
            ['流浪狗', '铲屎官', '舔毛']
            ]
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
            'y': 1130,
            'color1': "#3E78D6",
            'color2': "#2FDDFC",
        },
    }
    video_configs['horizontal_line']['y'] = video_configs['title_settings']['y'] + \
        video_configs['title_settings']['font_size']['chinese']+ \
        video_configs['title_settings']['font_size']['pinyin'] + \
        video_configs['title_settings']['font_size']['english'] + \
        video_configs['horizontal_line']['y_gap'] + \
        2*video_configs['title_settings']['spacing']

    video_configs['bottom_line']['y'] = video_configs['logo']['y'] - \
        video_configs['bottom_line']['y_gap']

    video_configs['words_settings']['y'] = video_configs['horizontal_line']['y'] + \
        video_configs['words_settings']['y_gap']
    return video_configs
