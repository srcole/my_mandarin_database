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


def draw_vocab_list_whole_image(video_configs, data_settings, df_filt):
    original_img = Image.new("RGB", video_configs['bg_size'], color=video_configs['bg_color'])
    draw = ImageDraw.Draw(original_img)
    draw_logo(draw, video_configs)

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
            'text': f"Part\n{data_settings['current_part']}/{data_settings['n_parts']}",
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
    

def create_video_with_highlights(df_durations, audio_settings, data_settings, video_configs):
    # Compute highlight durations
    highlight_start_ids = [1+x for x in df_durations[df_durations['audio_path']=='inter_word_pause'].index.tolist()]
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
