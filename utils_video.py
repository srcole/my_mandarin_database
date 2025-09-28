import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip

def create_component_words_text(row):
    component_words_text = f"{row['word1']}: {row['word1_english']}\n{row['word2']}: {row['word2_english']}"
    if not pd.isna(row['word3']):
        component_words_text += f"\n{row['word3']}: {row['word3_english']}"
    if not pd.isna(row['word4']):
        component_words_text += f"\n{row['word4']}: {row['word4_english']}"
    return component_words_text


def determine_if_text_size_too_big(text: str, font: ImageFont.ImageFont, line_length: int):
    new_lines = ['']
    for original_line in text.split('\n'):
        words_split = original_line.split(' ')
        for word_idx, word in enumerate(words_split):
            test_line = f'{new_lines[-1]} {word}'.strip()
            if word_idx == 0 and new_lines[-1] != '':
                new_lines.append(word)
            elif font.getlength(test_line) <= line_length:
                new_lines[-1] = test_line
            else:
                return True
    return False


def draw_text_and_save_clip(img, draw, clips, text_settings, video_configs, current_image_file_path):
    # Determine if text size is too big, if so, reduce font size until it fits
    new_font_size = text_settings['font_size']
    font = ImageFont.truetype(text_settings['font_path'], new_font_size)
    font_size_too_big = determine_if_text_size_too_big(text_settings['text'], font, line_length=video_configs['bg_size'][0]-video_configs['max_line_length_buffer_size'])
    while font_size_too_big:
        new_font_size -= video_configs['decrease_font_step_size']
        print(f'reduced font size to {new_font_size}')
        font = ImageFont.truetype(text_settings['font_path'], new_font_size)
        font_size_too_big = determine_if_text_size_too_big(text_settings['text'], font, line_length=video_configs['bg_size'][0]-video_configs['max_line_length_buffer_size'])

    # Get longest line length
    longest_length = max([font.getlength(x) for x in text_settings['text'].split('\n')])
    draw.multiline_text(
        xy=(video_configs['bg_size'][0]/2 - longest_length/2, text_settings['y'])
        , text=text_settings['text'], font=font
        , fill=text_settings['fill'], spacing=text_settings['spacing'], align=text_settings['align']
        )
    
    # Save clip if needed
    if text_settings['save_clip']:
        img_file_path = f"{current_image_file_path}{text_settings['img_file_suffix']}.png"
        img.save(img_file_path)
        my_img = ImageClip(img_file_path, duration=text_settings['duration']).with_start(text_settings['timestamp_start'])
        clips.append(my_img)
    return img, draw, clips


def combine_clips_with_audio_to_create_video(clips, nonvocab_slides, project_artifacts_folder):
    # Add duration and start time to each clip
    clips_all = clips.copy()
    for cs_name, cs_set in nonvocab_slides.items():
        image_with_duration = ImageClip(f'{project_artifacts_folder}/{cs_name}.png', duration=cs_set['duration']).with_start(cs_set['start'])
        if cs_set['clip_index'] >= 0:
            clips_all.insert(cs_set['clip_index'], image_with_duration)
        else:
            clips_all.append(image_with_duration)
    print(f"Number of clips: {len(clips_all)}")

    # Compare durations of audio and video
    audio = AudioFileClip(f"{project_artifacts_folder}/audio.mp3")
    all_clips_duration = sum(clip.duration for clip in clips_all)
    audio_video_duration_diff = audio.duration - all_clips_duration
    print(f"audio: {audio.duration:.3f}s, video: {all_clips_duration:.3f}s; difference: {audio_video_duration_diff:.3f}s")
    if audio_video_duration_diff > 0.3:
        raise ValueError('Difference between audio and video durations too high.')

    # Create final video file, if doesn't already exist
    video_file_name = f"{project_artifacts_folder}/video.mp4"
    if os.path.exists(video_file_name):
        print(f"Video already exists: {video_file_name}, skipping...")
    else:
        video = CompositeVideoClip(clips_all, size=(1280,720))
        audio = AudioFileClip(f"{project_artifacts_folder}/audio.mp3")
        video.audio = audio
        video.duration = audio.duration
        video.write_videofile(video_file_name, fps=24)


def create_icon_from_slide(icon_configs, video_configs, project_artifacts_folder):
    # Create solid color background
    img = Image.new(
        "RGB",
        (video_configs['bg_size'][0] + icon_configs['border_width']*2, video_configs['bg_size'][1] + icon_configs['border_width']*2),
        color=icon_configs['border_color_hex']
    )

    # Put the desired slide in the middle of the background
    overlay_image = Image.open(f"{project_artifacts_folder}/slides/{icon_configs['word']}{icon_configs['file_suffix']}.png")
    if overlay_image.mode != 'RGBA':
        overlay_image = overlay_image.convert('RGBA')
    img.paste(overlay_image, (icon_configs['border_width'], icon_configs['border_width']), overlay_image)
    return img


def draw_word_index(draw, video_configs, n_vocab, word_idx):
    word_index_font = ImageFont.truetype(video_configs['word_index']['font_name'], video_configs['word_index']['font_size'])
    word_index_part2_length = word_index_font.getlength(f"/{n_vocab}")
    word_index_length = word_index_font.getlength(f"{word_idx+1}/{n_vocab}")
    draw.text(
        text=f"/{n_vocab}",
        xy=(
            video_configs['bg_size'][0] - video_configs['word_index']['x'] - word_index_part2_length,
            video_configs['word_index']['y']
            ),
        font=word_index_font,
        fill=video_configs['word_index']['color2'],
        align='left'
    )
    draw.text(
        text=f"{word_idx+1}",
        xy=(
            video_configs['bg_size'][0] - video_configs['word_index']['x'] - word_index_length - 2,
            video_configs['word_index']['y']
            ),
        font=word_index_font,
        fill=video_configs['word_index']['color1'],
        align='left'
    )


def draw_logo(draw, video_configs):
    logo_font = ImageFont.truetype(video_configs['logo']['font_name'], video_configs['logo']['font_size'])
    draw.text(
        xy=(video_configs['bg_size'][0] - video_configs['logo']['x'] - logo_font.getlength('My'), video_configs['bg_size'][1] - video_configs['logo']['y'] - 2*video_configs['logo']['font_size']),
        text='My',
        font=logo_font,
        fill=video_configs['logo']['color1'],
        align='right'
        )
    draw.text(
        xy=(video_configs['bg_size'][0] - video_configs['logo']['x'] - logo_font.getlength('Mandarin'), video_configs['bg_size'][1] - video_configs['logo']['y'] - video_configs['logo']['font_size']),
        text='Mandarin',
        font=logo_font,
        fill=video_configs['logo']['color2'],
        align='right'
        )
    draw.text(
        xy=(video_configs['bg_size'][0] - video_configs['logo']['x'] - logo_font.getlength('Database'), video_configs['bg_size'][1] - video_configs['logo']['y']),
        text='Database',
        font=logo_font,
        fill=video_configs['logo']['color1'],
        align='right'
        )


def draw_previous_word(draw, video_configs, previous_word):
    if previous_word != '':
        draw.multiline_text(
            xy=(video_configs['previous_word']['x'], video_configs['bg_size'][1] - video_configs['previous_word']['y']),
            text=previous_word,
            font=ImageFont.truetype(video_configs['previous_word']['font_name'], video_configs['previous_word']['font_size']),
            fill=video_configs['previous_word']['color'],
            align='left'
            )


def draw_previous_sent(draw, video_configs, previous_sent):
    if previous_sent != '':
        sent_font = ImageFont.truetype(video_configs['previous_sent']['font_name'], video_configs['previous_sent']['font_size'])
        longest_length = max([sent_font.getlength(x) for x in previous_sent.split('\n')])
        draw.multiline_text(
            xy=(video_configs['bg_size'][0]/2 - longest_length/2, video_configs['bg_size'][1] - video_configs['previous_sent']['y']),
            text=previous_sent,
            font=sent_font,
            fill=video_configs['previous_word']['color'],
            align='center'
            )


# Change component word font size if more than 2 components
def compute_components_font_size(row, orig_component_font_size):
    if not pd.isna(row['word4']):
        return orig_component_font_size * .5
    elif not pd.isna(row['word3']):
        return orig_component_font_size * .75
    else:
        return orig_component_font_size


def compute_text_dict_from_row(recording_id, row):
    if recording_id == 'ceword_components_cesent':
        texts_dict = {
        'chinese': {
            'text': f"{row['chinese']} ({row['pinyin']})",
            'save_clip': True,
            'duration': row['start_english'] - row['start'],
            'timestamp_start': row['start'],
            },
        'component_words': {'text': create_component_words_text(row),
            'save_clip': True,
            'duration': row['start_english'] - row['start'],
            'timestamp_start': row['start'],
            },
        'english': {'text': row['english'],
            'save_clip': True,
            'duration': row['start_english'] - row['start'],
            'timestamp_start': row['start'],
            },
        'sentence_chinese': {'text': row['sentence'],
            'save_clip': False},
        'sentence_pinyin': {'text': row['sentence_pinyin'],
            'save_clip': True,
            'duration': row['start_english'] - row['start'],
            'timestamp_start': row['start'],
            },
        'sentence_english': {'text': row['sentence_english'],
            'save_clip': True,
            'duration': row['start_english'] - row['start'],
            'timestamp_start': row['start'],
            },
    }

    elif recording_id == 'ecword':
        texts_dict = {
        'english': {'text': row['english'],
            'save_clip': True,
            'duration': row['start_chinese'] - row['start'],
            'timestamp_start': row['start'],
            },
        'chinese': {
            'text': f"{row['chinese']}\n{row['pinyin']}",
            'save_clip': True,
            'duration': row['end'] - row['start_chinese'],
            'timestamp_start': row['start_chinese'],
            },
    }

    elif recording_id == 'cword2x':
        texts_dict = {
        'english': {'text': row['english'],
            'save_clip': False,
            },
        'chinese': {
            'text': f"{row['chinese']}\n{row['pinyin']}",
            'save_clip': True,
            'duration': row['end'] - row['start'],
            'timestamp_start': row['start'],
            },
    }

    elif recording_id == 'ceword_csent':
        texts_dict = {
        'chinese': {
            'text': f"{row['chinese']} ({row['pinyin']})",
            'save_clip': True,
            'duration': row['start_english'] - row['start'],
            'timestamp_start': row['start'],
            },
        'english': {'text': row['english'],
            'save_clip': True,
            'duration': row['start_sent'] - row['start_english'],
            'timestamp_start': row['start_english'],
            },
        'sentence_chinese': {'text': row['sentence'],
            'save_clip': False},
        'sentence_pinyin': {'text': row['sentence_pinyin'],
            'save_clip': False,
            },
        'sentence_english': {'text': row['sentence_english'],
            'save_clip': True,
            'duration': row['end'] - row['start_sent'],
            'timestamp_start': row['start_sent'],
            },
    }

    else:
        raise ValueError(f'recording_id not found: {recording_id}')
    return texts_dict


def draw_vocab_based_on_format(recording_id, row, video_configs, current_image_file_path, img, draw, clips):
    # Fill in default settings for each text item
    texts_dict = compute_text_dict_from_row(recording_id, row)
    for text_id in texts_dict.keys():
        texts_dict[text_id]['img_file_suffix'] = f'_{text_id}'
        for config_key, config_value in video_configs['vocab_slide'][text_id].items():
            if config_key not in texts_dict[text_id].keys():
                texts_dict[text_id][config_key] = config_value

    # Draw line between word and sentence
    if recording_id in ['ceword_csent', 'ceword_components_cesent']:
        draw.line([
            (video_configs['sentence_line']['x'], video_configs['sentence_line']['y']),
            (video_configs['bg_size'][0] - video_configs['sentence_line']['x'], video_configs['sentence_line']['y'])],
            fill=video_configs['sentence_line']['color'],
            width=video_configs['sentence_line']['width'],
            joint=None)
    
    # Decrease component size if 3+ components
    if recording_id in ['ceword_components_cesent']:
        texts_dict['component_words']['font_size'] = compute_components_font_size(
            row, texts_dict['component_words']['font_size'])

    # Draw texts
    for _, text_dict in texts_dict.items():
        img, draw, clips = draw_text_and_save_clip(
            img, draw, clips, text_dict, video_configs, current_image_file_path)
        

def generate_intro_slide(video_configs, intro_configs, subtitle_text_configs, audio_filler_variables):
    # Initialize image
    img = Image.new("RGB", video_configs['bg_size'], color=video_configs['bg_color'])
    draw = ImageDraw.Draw(img)

    # Define 2 sets of text to write in english and chinese
    intro_texts_dict = [
        {'text': f'{intro_configs['channel_title'][0]}\n{intro_configs['video_number'][0]}\n{intro_configs['video_name'][0]}',
        'text_chinese': f'{intro_configs['channel_title'][1]}\n{intro_configs['video_number'][1]}\n{intro_configs['video_name'][1]}',
        'font': ImageFont.truetype(intro_configs['text_configs'][0]['font_name'], intro_configs['text_configs'][0]['font_size']),
        },
        {'text': f'{intro_configs['video_structure'][0]}\n{intro_configs['count_str'][0].format(n_vocab_words=audio_filler_variables['n_vocab'])}\n{intro_configs['duration_str'][0].format(audio_duration_minutes=audio_filler_variables['audio_duration_minutes'])}\n{intro_configs['feedback'][0]}',
        'text_chinese': f'{intro_configs['video_structure'][1]}\n{intro_configs['count_str'][1].format(n_vocab_words=audio_filler_variables['n_vocab'])}\n{intro_configs['duration_str'][1].format(audio_duration_minutes=audio_filler_variables['audio_duration_minutes'])}\n{intro_configs['feedback'][1]}',
        'font': ImageFont.truetype(intro_configs['text_configs'][1]['font_name'], intro_configs['text_configs'][1]['font_size']),
        },
    ]

    # Write titles in english and chinese
    for i_ts, text_settings in enumerate(intro_texts_dict):
        intro_texts_dict[i_ts]['length'] = max([text_settings['font'].getlength(x) for x in text_settings['text'].split('\n')])
        intro_texts_dict[i_ts]['length_chinese'] = max([text_settings['font'].getlength(x) for x in text_settings['text_chinese'].split('\n')])

        draw.text(
            xy=(video_configs['bg_size'][0]/4 - intro_texts_dict[i_ts]['length']/2, intro_configs['text_configs'][i_ts]['y']),
            text=intro_texts_dict[i_ts]['text'],
            font=intro_texts_dict[i_ts]['font'],
            fill=intro_configs['text_configs'][i_ts]['fill'],
            spacing=intro_configs['text_configs'][i_ts]['spacing'],
            align=intro_configs['text_configs'][i_ts]['align'],
            )
        
        draw.text(
            xy=(video_configs['bg_size'][0]*3/4 - intro_texts_dict[i_ts]['length_chinese']/2, intro_configs['text_configs'][i_ts]['y']),
            text=intro_texts_dict[i_ts]['text_chinese'],
            font=intro_texts_dict[i_ts]['font'],
            fill=intro_configs['text_configs'][i_ts]['fill'],
            spacing=intro_configs['text_configs'][i_ts]['spacing'],
            align=intro_configs['text_configs'][i_ts]['align'],
            )
        
    # Write audio subtitles
    intro_audio_text = f'{intro_configs['chinese']}\n{intro_configs['pinyin']}\n{intro_configs['english']}'
    intro_audio_text_len = max([subtitle_text_configs['font'].getlength(x) for x in intro_audio_text.split('\n')])
    draw.text(
        xy=(video_configs['bg_size'][0]/2 - intro_audio_text_len/2, subtitle_text_configs['y']),
        text=intro_audio_text,
        font=subtitle_text_configs['font'],
        fill=subtitle_text_configs['fill'],
        spacing=subtitle_text_configs['spacing'],
        align=subtitle_text_configs['align'],
        )
    return img


def generate_word_list_slide(video_configs, word_list_configs, subtitle_text_configs, df_audio_durations_words_only):
    # Derive more configs
    word_list_configs['definition_configs']['pinyin']['x_offset'] = word_list_configs['definition_configs']['chinese']['x_offset'] + word_list_configs['definition_configs']['chinese']['x_max'] + word_list_configs['col_space']
    word_list_configs['definition_configs']['english']['x_offset'] = word_list_configs['definition_configs']['pinyin']['x_offset'] + word_list_configs['definition_configs']['pinyin']['x_max'] + word_list_configs['col_space']
    word_list_configs['xchange'] = word_list_configs['definition_configs']['english']['x_offset'] + word_list_configs['definition_configs']['english']['x_max'] + word_list_configs['col_space_big']
    word_list_configs['ychange'] = word_list_configs['font_size'] + word_list_configs['spacing']

    # Initialize parameters
    n_offsets = 0
    last_y_offset_idx = 0
    cur_y_offset = word_list_configs['y_top']
    cur_x_offset = word_list_configs['x_top']

    # Initialize image
    img = Image.new("RGB", video_configs['bg_size'], color=video_configs['bg_color'])
    draw = ImageDraw.Draw(img)
    for idx, row in df_audio_durations_words_only.iterrows():
        for def_part, dp_settings in word_list_configs['definition_configs'].items():
            new_font_size = word_list_configs['font_size']
            font = ImageFont.truetype(dp_settings['font_path'], new_font_size)
            font_size_too_big = determine_if_text_size_too_big(row[def_part], font, line_length=dp_settings['x_max'])
            while font_size_too_big:
                new_font_size -= 2
                print(f'"{row[def_part]}" reduced font size to {new_font_size}')
                font = ImageFont.truetype(dp_settings['font_path'], new_font_size)
                font_size_too_big = determine_if_text_size_too_big(row[def_part], font, line_length=dp_settings['x_max'])
            
            # Compute current X and Y positions
            y_pos_v1 = (cur_y_offset + word_list_configs['ychange']*(idx - last_y_offset_idx))
            
            if y_pos_v1 > (video_configs['bg_size'][1] - word_list_configs['ychange'] - word_list_configs['y_bottom']):
                n_offsets += 1
                last_y_offset_idx = idx
                cur_y_offset = word_list_configs['y_top']
                cur_x_offset += word_list_configs['xchange']

            x_pos = cur_x_offset + dp_settings['x_offset']
            y_pos_v2 = cur_y_offset + word_list_configs['ychange']*(idx - last_y_offset_idx)
            
            draw.text(
                xy=(x_pos, y_pos_v2), text=row[def_part], font=font
                , fill=word_list_configs['fill'], spacing=0, align=word_list_configs['align']
                )
            
    subtitle_text = f'{word_list_configs['chinese']}\n{word_list_configs['pinyin']}\n{word_list_configs['english']}'
    subtitle_text_len = max([subtitle_text_configs['font'].getlength(x) for x in subtitle_text.split('\n')])
    draw.text(
        xy=(video_configs['bg_size'][0]/2 - subtitle_text_len/2, subtitle_text_configs['y']),
        text=subtitle_text,
        font=subtitle_text_configs['font'],
        fill=subtitle_text_configs['fill'],
        spacing=subtitle_text_configs['spacing'],
        align=subtitle_text_configs['align'],
        )
    return img


def generate_outro_slide(video_configs, outro_configs, subtitle_text_configs, df_audio_durations_words_only):
    # Derive more configs
    outro_configs['definition_configs']['pinyin']['x_offset'] = outro_configs['definition_configs']['chinese']['x_offset'] + outro_configs['definition_configs']['chinese']['x_max'] + outro_configs['col_space']
    outro_configs['definition_configs']['english']['x_offset'] = outro_configs['definition_configs']['pinyin']['x_offset'] + outro_configs['definition_configs']['pinyin']['x_max'] + outro_configs['col_space']
    outro_configs['xchange'] = outro_configs['definition_configs']['english']['x_offset'] + outro_configs['definition_configs']['english']['x_max'] + outro_configs['col_space_big']
    outro_configs['ychange'] = outro_configs['font_size'] + outro_configs['spacing']

    # Initialize parameters
    n_offsets = 0
    last_y_offset_idx = 0
    cur_y_offset = outro_configs['y_top']
    cur_x_offset = outro_configs['x_top']

    # Initialize image
    img = Image.new("RGB", video_configs['bg_size'], color=video_configs['bg_color'])
    draw = ImageDraw.Draw(img)
    for idx, row in df_audio_durations_words_only.iterrows():
        for def_part, dp_settings in outro_configs['definition_configs'].items():
            new_font_size = outro_configs['font_size']
            font = ImageFont.truetype(dp_settings['font_path'], new_font_size)
            font_size_too_big = determine_if_text_size_too_big(row[def_part], font, line_length=dp_settings['x_max'])
            while font_size_too_big:
                new_font_size -= 2
                print(f'"{row[def_part]}" reduced font size to {new_font_size}')
                font = ImageFont.truetype(dp_settings['font_path'], new_font_size)
                font_size_too_big = determine_if_text_size_too_big(row[def_part], font, line_length=dp_settings['x_max'])
            
            # Compute current X and Y positions
            y_pos_v1 = (cur_y_offset + outro_configs['ychange']*(idx - last_y_offset_idx))
            
            if y_pos_v1 > (video_configs['bg_size'][1] - outro_configs['ychange'] - outro_configs['y_bottom']):
                n_offsets += 1
                last_y_offset_idx = idx
                cur_y_offset = outro_configs['y_top']
                cur_x_offset += outro_configs['xchange']

            x_pos = cur_x_offset + dp_settings['x_offset']
            y_pos_v2 = cur_y_offset + outro_configs['ychange']*(idx - last_y_offset_idx)
            
            draw.text(
                xy=(x_pos, y_pos_v2), text=row[def_part], font=font
                , fill=outro_configs['fill'], spacing=0, align=outro_configs['align']
                )
            
    subtitle_text = f'{outro_configs['chinese']}\n{outro_configs['pinyin']}\n{outro_configs['english']}'
    subtitle_text_len = max([subtitle_text_configs['font'].getlength(x) for x in subtitle_text.split('\n')])
    draw.text(
        xy=(video_configs['bg_size'][0]/2 - subtitle_text_len/2, subtitle_text_configs['y']),
        text=subtitle_text,
        font=subtitle_text_configs['font'],
        fill=subtitle_text_configs['fill'],
        spacing=subtitle_text_configs['spacing'],
        align=subtitle_text_configs['align'],
        )
    return img
