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

def load_examples_data():
    return pd.read_csv('static/texts/lists/anomia_examples.csv')


def load_category_data():
    df_categories = pd.read_csv('static/texts/lists/anomia_categories.csv')
    return df_categories


def create_directories(data_settings):
    if not os.path.exists(data_settings['output_path_base']):
        os.mkdir(data_settings['output_path_base'])
    if not os.path.exists(data_settings['output_path']):
        os.mkdir(data_settings['output_path'])
    if not os.path.exists(data_settings['output_path_audio']):
        os.mkdir(data_settings['output_path_audio'])
    if not os.path.exists(data_settings['output_path_images']):
        os.mkdir(data_settings['output_path_images'])


def _single_tts_call(text, voice_name, output_file_name):
    communicate = Communicate(text, voice_name)
    communicate.save_sync(output_file_name)


def generate_and_zip_audio_files(voice_name, category, examples):
    if not os.path.exists(category):
        os.mkdir(category)

    start_time = time.time()
    for text_str in [category] + examples:
        print(time.time()-start_time, text_str)
        _single_tts_call(text_str, voice_name, f'{category}/{text_str}.mp3')

    current_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.make_archive(f"{category}_{current_datetime}", 'zip', category)


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
        title_audio_path = f"{data_settings['output_path_audio']}/{data_settings['category']}.mp3"
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
    combined.export(f"{data_settings['output_path_audio']}/combined.mp3", format="mp3")
    print(f'Audio duration: {combined.duration_seconds:.1f}s')

    # Add in static slide audio into dataframe of audio durations
    df_durations = pd.DataFrame(dict_audio_durations)
    return df_durations


def draw_resized_text_on_image(draw, text_settings, video_configs, is_centered=False):
    font = ImageFont.truetype(text_settings['font_path'], text_settings['font_size'])
    new_font_size = text_settings['font_size']
    font_size_too_big = determine_if_text_size_too_big(text_settings['text'], font, line_length=text_settings['max_line_length'])
    while font_size_too_big:
        if new_font_size <= 5:
            text_settings['text'] = text_settings['text'][:-1]
        else:
            new_font_size -= video_configs['decrease_font_step_size']
        font = ImageFont.truetype(text_settings['font_path'], new_font_size)
        font_size_too_big = determine_if_text_size_too_big(text_settings['text'], font, line_length=text_settings['max_line_length'])

    # Get longest line length
    longest_length = max([font.getlength(x) for x in text_settings['text'].split('\n')])
    if is_centered:
        text_settings['x'] = video_configs['bg_size'][0] / 2 - longest_length / 2
    draw.multiline_text(
        xy=(text_settings['x'], text_settings['y'])
        , text=text_settings['text'], font=font
        , fill=text_settings['fill'], spacing=text_settings['spacing'], align=text_settings['align']
        )
    

def draw_logo(draw, video_configs):
    logo_font = ImageFont.truetype(video_configs['logo']['font_name'], video_configs['logo']['font_size'])
    draw.text(
        xy=(video_configs['logo']['x'] - logo_font.getlength('My'), video_configs['logo']['y']),
        text='My',
        font=logo_font,
        fill=video_configs['logo']['color1'],
        align='right'
        )
    draw.text(
        xy=(video_configs['logo']['x'] - logo_font.getlength('Mandarin'), video_configs['logo']['y'] + video_configs['logo']['font_size']),
        text='Mandarin',
        font=logo_font,
        fill=video_configs['logo']['color2'],
        align='right'
        )
    draw.text(
        xy=(video_configs['logo']['x'] - logo_font.getlength('Database'), video_configs['logo']['y'] + 2*video_configs['logo']['font_size']),
        text='Database',
        font=logo_font,
        fill=video_configs['logo']['color1'],
        align='right'
        )
    

def draw_word_index(draw, video_configs, n_vocab, word_idx):
    word_index_font = ImageFont.truetype(video_configs['category_index']['font_name'], video_configs['category_index']['font_size'])
    word_index_part2_length = word_index_font.getlength(f"/{n_vocab}")
    word_index_length = word_index_font.getlength(f"{word_idx+1}/{n_vocab}")
    draw.text(
        text=f"/{n_vocab}",
        xy=(
            video_configs['category_index']['x'] - word_index_part2_length,
            video_configs['category_index']['y']
            ),
        font=word_index_font,
        fill=video_configs['category_index']['color2'],
        align='left'
    )
    draw.text(
        text=f"{word_idx}",
        xy=(
            video_configs['category_index']['x'] - word_index_length - 2,
            video_configs['category_index']['y']
            ),
        font=word_index_font,
        fill=video_configs['category_index']['color1'],
        align='left'
    )


def draw_vocab_list_whole_image(video_configs, df_categories, data_settings, df_filt):
    original_img = Image.new("RGB", video_configs['bg_size'], color=video_configs['bg_color'])
    draw = ImageDraw.Draw(original_img)
    draw_logo(draw, video_configs)
    draw_word_index(draw, video_configs, len(df_categories), data_settings['category_id'])

    title_text_settings = {}
    title_text_settings['chinese'] = {
        'text': data_settings['category'],
        'font_path': video_configs['font_path'],
        'font_size': video_configs['title_settings']['font_size']['chinese'],
        'y': video_configs['title_settings']['y'],
        'spacing': video_configs['title_settings']['spacing'],
        'align': video_configs['title_settings']['align'],
        'fill': video_configs['title_settings']['fill']['chinese'],
        'max_line_length': video_configs['max_line_length'],
    }
    title_text_settings['pinyin'] = {
        'text': data_settings['category_pinyin'],
        'font_path': video_configs['font_path'],
        'font_size': video_configs['title_settings']['font_size']['pinyin'],
        'y': video_configs['title_settings']['y'] + video_configs['title_settings']['font_size']['chinese'] + video_configs['title_settings']['spacing'],
        'spacing': video_configs['title_settings']['spacing'],
        'align': video_configs['title_settings']['align'],
        'fill': video_configs['title_settings']['fill']['chinese'],
        'max_line_length': video_configs['max_line_length'],
    }
    title_text_settings['english'] = {
        'text': data_settings['category_english'],
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
    combined_audio = AudioFileClip(f"{data_settings['output_path_audio']}/combined.mp3")
    clips_no_highlights = [ImageClip(no_hl_img_file_path, duration=combined_audio.duration).with_start(0)]
    video = CompositeVideoClip(clips_no_highlights, size=video_configs['bg_size'])
    video.audio = combined_audio
    video.duration = combined_audio.duration
    no_highlights_video_path = f"{data_settings['output_path']}/{data_settings['category']}_no_highlights.mp4"
    video.write_videofile(no_highlights_video_path, fps=24)


def create_video_with_highlights(df_durations, audio_settings, data_settings, video_configs):
    # Compute highlight durations
    highlight_start_ids = np.arange(3,42,4)
    highlight_end_ids = np.arange(5,42,4)
    dict_highlight_durations = defaultdict(list)
    for i_row, row in df_durations.iterrows():
        if i_row in highlight_start_ids:
            dict_highlight_durations['start_time'].append(row['start_time'] - audio_settings['pause_ms_within_word']/(2*1000))
        if i_row in highlight_end_ids:
            dict_highlight_durations['end_time'].append(row['end_time'] + audio_settings['pause_ms_within_word']/(2*1000))
    df_highlight_durations = pd.DataFrame(dict_highlight_durations)
    df_highlight_durations['duration'] = df_highlight_durations['end_time'] - df_highlight_durations['start_time']

    no_highlights_video_path = f"{data_settings['output_path']}/{data_settings['category']}_no_highlights.mp4"
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
    final_video.write_videofile(f"{data_settings['output_path']}/{data_settings['category']}.mp4", codec="libx264")
