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


def stitch_audios(audio_settings, data_settings, example_words, df_vocab_list, part_number=1):
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
    
    elif audio_settings['audio_plan'] == 'cparts_ce_csent':

        def add_new_audio(combined, audio_segment, audio_name, current_start_time):
            combined += audio_segment
            dict_audio_durations['audio_name'].append(audio_name)
            dict_audio_durations['duration'].append(audio_segment.duration_seconds)
            dict_audio_durations['start_time'].append(current_start_time)
            current_start_time += audio_segment.duration_seconds
            dict_audio_durations['end_time'].append(current_start_time)
            return combined, current_start_time
        

        current_start_time = 0
        combined = AudioSegment.silent(duration=1)  # start with 1ms silence to avoid empty audio error

        # beginning pause
        combined, current_start_time = add_new_audio(
            combined, AudioSegment.silent(duration=audio_settings['pause_ms_beginning']), 'pause_beginning', current_start_time)

        # title
        title_audio_path = f"{data_settings['output_path_audio']}/{data_settings['chinese']}.mp3"
        combined, current_start_time = add_new_audio(combined, AudioSegment.from_mp3(title_audio_path), data_settings['chinese'], current_start_time)

        # words
        for current_vocab_idx, current_vocab in df_vocab_list.iterrows():
            # inter-word pause
            combined, current_start_time = add_new_audio(
                combined, AudioSegment.silent(duration=audio_settings['pause_ms_between']), 'inter_word_pause', current_start_time)
            
            # components
            for component_id in ['word1', 'word2', 'word3', 'word4']:
                if not pd.isna(current_vocab[component_id]):
                    component_audio_path = f"{data_settings['output_path_audio']}/{current_vocab[component_id]}.mp3"
                    combined, current_start_time = add_new_audio(
                        combined, AudioSegment.from_mp3(component_audio_path), f'vocab_word_{current_vocab_idx}_{component_id}', current_start_time)
                    
                    # within-word pause
                    combined, current_start_time = add_new_audio(
                        combined, AudioSegment.silent(duration=audio_settings['pause_ms_within']), 'within_word_pause', current_start_time)
            
            # vocab word chinese
            combined, current_start_time = add_new_audio(
                combined, AudioSegment.from_mp3(f"{data_settings['output_path_audio']}/{current_vocab['chinese']}.mp3"), f'vocab_word_{current_vocab_idx}_chinese', current_start_time)
            
            # within-word pause
            combined, current_start_time = add_new_audio(
                combined, AudioSegment.silent(duration=audio_settings['pause_ms_within']), 'within_word_pause', current_start_time)
            
            # vocab word english
            combined, current_start_time = add_new_audio(
                combined, AudioSegment.from_mp3(f"{data_settings['output_path_audio']}/{current_vocab['english']}.mp3"), f'vocab_word_{current_vocab_idx}_english', current_start_time)

            # within-word pause
            combined, current_start_time = add_new_audio(
                combined, AudioSegment.silent(duration=audio_settings['pause_ms_within']), 'within_word_pause', current_start_time)
            
            # sentence
            combined, current_start_time = add_new_audio(
                combined, AudioSegment.from_mp3(f"{data_settings['output_path_audio']}/{current_vocab['sentence']}.mp3"), f'vocab_word_{current_vocab_idx}_sentence', current_start_time)

    # export the combined audio file
    if 'current_part' in data_settings.keys():
        part_suffix = f"_part{data_settings['current_part']}"
    else:
        part_suffix = ''
    combined.export(f"{data_settings['output_path_audio']}/!combined{part_suffix}.mp3", format="mp3")
    print(f'Audio duration: {combined.duration_seconds:.1f}s')

    # Add in static slide audio into dataframe of audio durations
    df_durations = pd.DataFrame(dict_audio_durations)
    return df_durations


def draw_lt_vocab_list_whole_image(video_configs, data_settings, df_vocab_list):
    original_img = Image.new("RGB", video_configs['bg_size'], color=(255, 255, 255))
    draw = ImageDraw.Draw(original_img, 'RGBA')
    draw_logo(draw, video_configs)

    title_text_settings = {}
    title_text_settings['chinese'] = {
        'text': data_settings['chinese'],
        'font_path': video_configs['font_path'],
        'font_size': video_configs['title_settings']['font_size']['chinese'],
        'y': video_configs['title_settings']['y'],
        'spacing': video_configs['title_settings']['spacing'],
        'align': video_configs['title_settings']['align'],
        'fill': video_configs['title_settings']['fill']['chinese'],
        'max_line_length': video_configs['max_line_length'],
    }
    title_text_settings['pinyin'] = {
        'text': data_settings['pinyin'],
        'font_path': video_configs['font_path'],
        'font_size': video_configs['title_settings']['font_size']['pinyin'],
        'y': video_configs['title_settings']['y'] + video_configs['title_settings']['font_size']['chinese'] + video_configs['title_settings']['spacing'],
        'spacing': video_configs['title_settings']['spacing'],
        'align': video_configs['title_settings']['align'],
        'fill': video_configs['title_settings']['fill']['chinese'],
        'max_line_length': video_configs['max_line_length'],
    }
    title_text_settings['english'] = {
        'text': data_settings['english'],
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
    
    original_img.save(f"{data_settings['output_path_images']}/title_only.png")

    # Write part number, if applicable
    if 'current_part' in data_settings:
        part_text_settings = {
            'text': f"Part\n{data_settings['current_part']}/{data_settings['n_parts']}",
            'font_path': 'Arial Black',
            'font_size': 32,
            'x': video_configs['bg_size'][0] - 115,
            'y': 80 - 40,
            'spacing': 4,
            'align': 'center',
            'fill': '#000000',
            'max_line_length': 300,
        }
        draw.circle(
            [video_configs['bg_size'][0] - 80, 80, 300, 300],
            outline="#000000",
            width=4,
            radius=60,
            fill=(255, 255, 255, 200),
        )
        draw_resized_text_on_image(draw, part_text_settings, video_configs, is_centered=False)
        original_img.save(f"{data_settings['output_path_images']}/title_only.png")

    # 5. Words
    for i_row, row in df_vocab_list.iterrows():            
        # Components
        if not pd.isna(row['word4']):
            n_components = 4
        elif not pd.isna(row['word3']):
            n_components = 3
        else:
            n_components = 2

        components_text = '\n'.join([f"{row[component_id]}: {row[f'{component_id}_english']}" for component_id in ['word1', 'word2', 'word3', 'word4'] if not pd.isna(row[component_id])])
        if i_row == 0:
            components_y = video_configs['words_settings']['y']
        else:
            components_y = sentence_y + (3 * video_configs['words_settings']['font_size']['sentence']) + (2 * video_configs['words_settings']['spacing']['sentence']) + video_configs['words_settings']['between_words_spacing']

        # Create binding rectangle highlight
        rect_width = video_configs['bg_size'][0] - 2*video_configs['words_settings']['x'] + 2*video_configs['highlight_rect_x_buffer']
        rect_height = (
            video_configs['highlight_rect_y_buffer'] + 
            ((3 * video_configs['words_settings']['font_size']['sentence']) + (2 * video_configs['words_settings']['spacing']['sentence'])) +
            (video_configs['words_settings']['vocab_word_to_sentence_spacing'] + video_configs['words_settings']['font_size']['vocab_word']) +
            (n_components * (video_configs['words_settings']['spacing']['components'] + video_configs['words_settings']['font_size']['components'])) + video_configs['words_settings']['component_words_to_vocab_word_spacing'] - video_configs['words_settings']['spacing']['components']
        )
        rect_x = video_configs['words_settings']['x'] - video_configs['highlight_rect_x_buffer']
        rect_y = components_y - video_configs['highlight_rect_y_buffer']

        draw.rectangle(
            [rect_x, rect_y, rect_x + rect_width, rect_y + rect_height],
            outline="#000000",
            fill=(255, 255, 0, 50),
            width=4
        )

        text_settings = {
            'text': components_text,
            'font_path': video_configs['font_path'],
            'font_size': video_configs['words_settings']['font_size']['components'],
            'x': None,
            'y': components_y,
            'spacing': video_configs['words_settings']['spacing']['components'],
            'align': 'center',
            'fill': video_configs['words_settings']['fill']['components'],
            'max_line_length': video_configs['max_line_length'],
        }
        draw_resized_text_on_image(draw, text_settings, video_configs, is_centered=True)
        original_img.save(f"{data_settings['output_path_images']}/vocab_word_{i_row}_component_only.png")
        
        # Vocab word
        vocab_word_text = f"{row['chinese']} ({row['pinyin']}): {row['english']}"
        non_components_y = components_y + (n_components * (video_configs['words_settings']['spacing']['components'] + video_configs['words_settings']['font_size']['components'])) + video_configs['words_settings']['component_words_to_vocab_word_spacing'] - video_configs['words_settings']['spacing']['components']
        text_settings = {
            'text': vocab_word_text,
            'font_path': video_configs['font_path'],
            'font_size': video_configs['words_settings']['font_size']['vocab_word'],
            'x': None,
            'y': non_components_y,
            'spacing': 0,
            'align': 'center',
            'fill': video_configs['words_settings']['fill']['vocab_word'],
            'max_line_length': video_configs['max_line_length'],
        }
        draw_resized_text_on_image(draw, text_settings, video_configs, is_centered=True)
        original_img.save(f"{data_settings['output_path_images']}/vocab_word_{i_row}_full.png")
        
        # Sentence
        vocab_word_text = f"{row['sentence']}\n{row['sentence_pinyin']}\n{row['sentence_english']}"
        font = ImageFont.truetype(video_configs['font_path'], video_configs['words_settings']['font_size']['vocab_word'])
        sentence_y = non_components_y + video_configs['words_settings']['vocab_word_to_sentence_spacing'] + video_configs['words_settings']['font_size']['vocab_word']
        text_settings = {
            'text': vocab_word_text,
            'font_path': video_configs['font_path'],
            'font_size': video_configs['words_settings']['font_size']['sentence'],
            'x': None,
            'y': sentence_y,
            'spacing': video_configs['words_settings']['spacing']['sentence'],
            'align': 'center',
            'fill': video_configs['words_settings']['fill']['sentence'],
            'max_line_length': video_configs['bg_size'][0] - 100,
        }
        draw_resized_text_on_image(draw, text_settings, video_configs, is_centered=True)
        original_img.save(f"{data_settings['output_path_images']}/vocab_word_{i_row}_sentence.png")
    return f"{data_settings['output_path_images']}/vocab_word_{i_row}_sentence.png"


def create_video_with_concat_images(df_durations, df_vocab_list, data_settings):

    # Computer starts and durations of each slide
    tup_starts_ends = [(
        'title_only', 0, df_durations[df_durations['audio_name'] == 'inter_word_pause']['end_time'].values[0]
    )]
    for current_vocab_idx, current_vocab in df_vocab_list.iterrows():
        current_vocab_word_chinese_durations = df_durations[df_durations['audio_name'] == f'vocab_word_{current_vocab_idx}_chinese'].reset_index(drop=True).loc[0]
        current_vocab_word_sentence_durations = df_durations[df_durations['audio_name'] == f'vocab_word_{current_vocab_idx}_sentence'].reset_index(drop=True).loc[0]
        # components
        tup_starts_ends.append(
            (f'vocab_word_{current_vocab_idx}_component_only',
            tup_starts_ends[-1][2],
            current_vocab_word_chinese_durations['start_time'])
        )
        # full vocab word
        tup_starts_ends.append(
            (f'vocab_word_{current_vocab_idx}_full',
            tup_starts_ends[-1][2],
            current_vocab_word_sentence_durations['start_time'])
        )
        # add_sentence
        tup_starts_ends.append(
            (f'vocab_word_{current_vocab_idx}_sentence',
            tup_starts_ends[-1][2],
            current_vocab_word_sentence_durations['end_time'])
        )

    # For each clip, get the image
    clips = []
    for clip_name, start_time, end_time in tup_starts_ends:
        img_file_path = f"{data_settings['output_path_images']}/{clip_name}.png"
        duration = end_time - start_time
        print(f'Adding clip: {img_file_path} for duration {duration:.1f}s')
        clips.append(ImageClip(img_file_path, duration=duration).with_start(start_time))

    if 'current_part' in data_settings.keys():
        part_suffix = f"_part{data_settings['current_part']}"
    else:
        part_suffix = ''
    audio_for_video = AudioFileClip(f"{data_settings['output_path_audio']}/!combined{part_suffix}.mp3")
    audio_duration = audio_for_video.duration
    print(f'Final audio duration: {audio_duration:.3f}s')
    final_video = CompositeVideoClip(clips)
    print(f'Final video duration before audio set: {final_video.duration:.3f}s')
    final_video.audio = audio_for_video
    final_video.write_videofile(f"{data_settings['output_path']}/{data_settings['chinese']}_video{part_suffix}.mp4", fps=24)
