import pandas as pd
from collections import defaultdict
import os
from gtts import gTTS
from edge_tts import list_voices, Communicate
from moviepy import AudioFileClip
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from collections import defaultdict
import time
from utils_data import pinyin_to_tones


def single_tts_call(text, voice_name, output_file_name):
    if voice_name in ['en', 'zh']:
        single_gtts_call(text, voice_name, output_file_name)
    else:
        communicate = Communicate(text, voice_name)
        communicate.save_sync(output_file_name)


def single_gtts_call(content_str, lang_name, slow_mode, new_file_path):
    if lang_name == 'zh_slow':
        slow_mode = True
        lang_name = 'zh'
    else:
        slow_mode = False
    gTTS(content_str, lang=lang_name, slow=slow_mode).save(new_file_path)


def create_tts_file(content_str, lang_name, last_timestamp, chinese_char, recording_id):

    new_file_path = f"output/tts/{lang_name}/{content_str.replace('/', '-')}.mp3"
    if not os.path.exists(new_file_path):
        # Delete final row file, if exists, since will have to rewrite it
        row_file_path = f"output/rows/{recording_id}/{chinese_char}.mp3"
        if os.path.exists(row_file_path):
            os.remove(row_file_path)
        
        try:
            single_tts_call(content_str, lang_name, new_file_path)
        except:
            print(f"!!!!!!! FAILURE, wait 52 seconds, {lang_name}, {content_str} !!!!!!!")
            time.sleep(52)
            try:
                single_tts_call(content_str, lang_name, new_file_path)
            except:
                print(f"!!!!!!!!!! FAILURE AGAIN, wait 278 seconds, {lang_name}, {content_str} !!!!!!!!!!")
                time.sleep(278)
                single_tts_call(content_str, lang_name, new_file_path)
        print(f"{(time.time()-last_timestamp):.3f}s, {lang_name}, {content_str}")
    else:
        print(f"{(time.time()-last_timestamp):.3f}s, ALREADY EXISTS, {lang_name}, {content_str}")


def create_tts_files_for_one_vocab_word(row, data_settings):
    create_tts_file(content_str=row['chinese'], lang_name=data_settings['voice_name_zh'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
    create_tts_file(content_str=row['english'], lang_name=data_settings['voice_name_en'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
    
    if data_settings['recording_id'] in ['001', '007', '009', 'ceword_components_cesent', 'ce_wordsent', 'cword_cecomponent_cesent_notes', 'ceword_components_csent']:
        create_tts_file(content_str=row['sentence'], lang_name=data_settings['voice_name_zh'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
        create_tts_file(content_str=row['sentence_english'], lang_name=data_settings['voice_name_en'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
    
    if data_settings['recording_id'] in ['002', '011', '012', '015', 'cn_only_sent', 'ec_csent']:
        create_tts_file(content_str=row['sentence'], lang_name=data_settings['voice_name_zh'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
    
    if data_settings['recording_id'] in ['ceword_components_cesent', '006', 'ceword_components_csent']:
        create_tts_file(content_str=row['word1'], lang_name=data_settings['voice_name_zh'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
        create_tts_file(content_str=row['word2'], lang_name=data_settings['voice_name_zh'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
        create_tts_file(content_str=row['word1_english'], lang_name=data_settings['voice_name_en'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
        create_tts_file(content_str=row['word2_english'], lang_name=data_settings['voice_name_en'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
        if not pd.isna(row['word3']):
            create_tts_file(content_str=row['word3'], lang_name=data_settings['voice_name_zh'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
            create_tts_file(content_str=row['word3_english'], lang_name=data_settings['voice_name_en'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
        if not pd.isna(row['word4']):
            create_tts_file(content_str=row['word4'], lang_name=data_settings['voice_name_zh'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
            create_tts_file(content_str=row['word4_english'], lang_name=data_settings['voice_name_en'], last_timestamp=time.time(), chinese_char=row['chinese'], recording_id=data_settings['recording_id'])
    

def compute_pinyin_and_create_recordings(df_words):
    # Make pinyin audio, if needed
    pinyin_tones = ['1', '2', '3', '4']
    for tone_str in pinyin_tones:
        single_tts_call(tone_str, 'en', False, f"output/english/{tone_str}.mp3")

    # Compute pinyin tones for each character
    df_words['pinyin_tones'] = df_words['pinyin'].apply(pinyin_to_tones)
    return df_words


def load_one_audio_from_path(mp3_path):
    try:
        audio = AudioSegment.from_mp3(mp3_path)
    except CouldntDecodeError:
        os.remove(mp3_path)
        print(f"!!!!!!! DELETED CORRUPTED FILE {mp3_path} !!!!!!!")
        raise ValueError(f"Corrupted file {mp3_path}, deleted. Please rerun the cell above to regenerate it.")
    return audio


def load_audio(row, data_settings):
    pause_100ms = AudioSegment.silent(duration=100)
    pause_300ms = AudioSegment.silent(duration=300)
    pause_500ms = AudioSegment.silent(duration=500)
    pause_between_words = AudioSegment.silent(duration=data_settings['pause_between_words_ms'])

    dict_audio_durations = defaultdict(list)
    chinese_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['chinese'].replace('/', '-')}.mp3")
    english_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['english'].replace('/', '-')}.mp3")
    
    if data_settings['recording_id'] in ['001', '007', '009', 'ce_wordsent']:
        sent_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['sentence']}.mp3")
        sent_english_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['sentence_english']}.mp3")
        combined = chinese_audio + pause_500ms + chinese_audio + pause_500ms + english_audio + pause_500ms + sent_audio + pause_500ms + sent_english_audio + pause_500ms + sent_audio + pause_between_words

        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])
        dict_audio_durations['sentence'].append(row['sentence'])
        dict_audio_durations['sentence_pinyin'].append(row['sentence_pinyin'])
        dict_audio_durations['sentence_english'].append(row['sentence_english'])

        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_chinese_slow'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_english'].append(english_audio.duration_seconds)
        dict_audio_durations['d_sent'].append(sent_audio.duration_seconds)
        dict_audio_durations['d_sent_english'].append(sent_english_audio.duration_seconds)

        dict_audio_durations['rel_start_chinese'].append(0)
        dict_audio_durations['rel_start_english'].append(dict_audio_durations['rel_start_chinese'][-1] + dict_audio_durations['d_chinese'][-1] + dict_audio_durations['d_chinese_slow'][-1] + 1)
        dict_audio_durations['rel_start_sent'].append(dict_audio_durations['rel_start_english'][-1] + dict_audio_durations['d_english'][-1] + 0.5)
        dict_audio_durations['rel_start_sent_english'].append(dict_audio_durations['rel_start_sent'][-1] + dict_audio_durations['d_sent'][-1] + 0.5)

        dict_audio_durations['sum_theory'].append(dict_audio_durations['rel_start_sent_english'][-1] + dict_audio_durations['d_sent_english'][-1] + dict_audio_durations['d_sent'][-1] + 0.5 + data_settings['pause_between_words_ms']/1000)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    elif data_settings['recording_id'] in ['002', '011']:
        sent_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['sentence']}.mp3")
        combined = chinese_audio + pause_500ms + chinese_audio + pause_500ms + english_audio + pause_500ms + sent_audio + pause_500ms + sent_audio + pause_between_words

    elif data_settings['recording_id'] in ['004', '008', '010', '014']:
        combined = chinese_audio + pause_500ms + chinese_audio + pause_500ms + english_audio + pause_between_words

        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])
        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_chinese_slow'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_english'].append(english_audio.duration_seconds)

        dict_audio_durations['rel_start_chinese'].append(0)
        dict_audio_durations['rel_start_english'].append(dict_audio_durations['rel_start_chinese'][-1] + dict_audio_durations['d_chinese'][-1] + dict_audio_durations['d_chinese_slow'][-1] + 1)
        dict_audio_durations['sum_theory'].append(dict_audio_durations['rel_start_english'][-1] + dict_audio_durations['d_english'][-1] + data_settings['pause_between_words_ms']/1000)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    elif data_settings['recording_id'] in ['016']:
        combined = english_audio + pause_500ms + chinese_audio + pause_300ms + chinese_audio + pause_between_words

        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])
        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_chinese_slow'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_english'].append(english_audio.duration_seconds)

        dict_audio_durations['rel_start_english'].append(0)
        dict_audio_durations['rel_start_chinese'].append(dict_audio_durations['rel_start_english'][-1] + dict_audio_durations['d_english'][-1] + .5)
        dict_audio_durations['sum_theory'].append(dict_audio_durations['rel_start_chinese'][-1] + dict_audio_durations['d_chinese'][-1] + dict_audio_durations['d_chinese_slow'][-1] + 0.3 + data_settings['pause_between_words_ms']/1000)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    elif data_settings['recording_id'] == '005':
        tones_audio = AudioSegment.silent(duration=0)
        for pinyin_tone in row['pinyin_tones']:
            tones_audio += load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{pinyin_tone}.mp3")
            tones_audio += pause_100ms

        combined = chinese_audio + pause_500ms + tones_audio + pause_500ms + chinese_audio + pause_500ms + english_audio + pause_between_words

    elif data_settings['recording_id'] == '006':
        word1_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word1']}.mp3")
        word1e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word1_english']}.mp3")
        word2_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word2']}.mp3")
        word2e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word2_english']}.mp3")
        if not pd.isna(row['word3']):
            word3_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word3']}.mp3")
            word3e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word3_english']}.mp3")
        if not pd.isna(row['word4']):
            word4_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word4']}.mp3")
            word4e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word4_english']}.mp3")

        component_words_audio = word1_audio + pause_100ms + word1e_audio + pause_500ms + word2_audio + pause_100ms + word2e_audio
        if not pd.isna(row['word3']):
            component_words_audio += pause_500ms + word3_audio + pause_100ms + word3e_audio
        if not pd.isna(row['word4']):
            component_words_audio += pause_500ms + word4_audio + pause_100ms + word4e_audio
        combined = chinese_audio + pause_500ms + component_words_audio + pause_500ms + chinese_audio + pause_500ms + english_audio + pause_between_words

        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])
        dict_audio_durations['word1'].append(row['word1'] if not pd.isna(row['word1']) else '')
        dict_audio_durations['word1_english'].append(row['word1_english'] if not pd.isna(row['word1_english']) else '')
        dict_audio_durations['word2'].append(row['word2'] if not pd.isna(row['word2']) else '')
        dict_audio_durations['word2_english'].append(row['word2_english'] if not pd.isna(row['word2_english']) else '')
        dict_audio_durations['word3'].append(row['word3'] if not pd.isna(row['word3']) else '')
        dict_audio_durations['word3_english'].append(row['word3_english'] if not pd.isna(row['word3_english']) else '')
        dict_audio_durations['word4'].append(row['word4'] if not pd.isna(row['word4']) else '')
        dict_audio_durations['word4_english'].append(row['word4_english'] if not pd.isna(row['word4_english']) else '')
        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_component_words'].append(component_words_audio.duration_seconds)
        dict_audio_durations['d_chinese_slow'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_english'].append(english_audio.duration_seconds)

        dict_audio_durations['rel_start_chinese'].append(0)
        dict_audio_durations['rel_start_component_words'].append(dict_audio_durations['rel_start_chinese'][-1] + dict_audio_durations['d_chinese'][-1] + 0.5)
        dict_audio_durations['rel_start_english'].append(dict_audio_durations['rel_start_component_words'][-1] + dict_audio_durations['d_component_words'][-1] + dict_audio_durations['d_chinese_slow'][-1] + 1)

        dict_audio_durations['sum_theory'].append(dict_audio_durations['rel_start_english'][-1] + dict_audio_durations['d_english'][-1] + data_settings['pause_between_words_ms']/1000)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    elif data_settings['recording_id'] in ['ceword_components_cesent']:
        sent_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['sentence']}.mp3")
        sent_english_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['sentence_english']}.mp3")
        word1_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word1']}.mp3")
        word1e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word1_english']}.mp3")
        word2_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word2']}.mp3")
        word2e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word2_english']}.mp3")
        if not pd.isna(row['word3']):
            word3_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word3']}.mp3")
            word3e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word3_english']}.mp3")
        if not pd.isna(row['word4']):
            word4_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word4']}.mp3")
            word4e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word4_english']}.mp3")

        component_words_audio = word1_audio + pause_100ms + word1e_audio + pause_500ms + word2_audio + pause_100ms + word2e_audio
        if not pd.isna(row['word3']):
            component_words_audio += pause_500ms + word3_audio + pause_100ms + word3e_audio
        if not pd.isna(row['word4']):
            component_words_audio += pause_500ms + word4_audio + pause_100ms + word4e_audio
        combined = chinese_audio + pause_500ms + component_words_audio + pause_500ms + chinese_audio + pause_500ms + english_audio + pause_500ms + sent_audio + pause_500ms + sent_english_audio + pause_between_words


        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])
        dict_audio_durations['sentence'].append(row['sentence'])
        dict_audio_durations['sentence_pinyin'].append(row['sentence_pinyin'])
        dict_audio_durations['sentence_english'].append(row['sentence_english'])
        dict_audio_durations['word1'].append(row['word1'] if not pd.isna(row['word1']) else '')
        dict_audio_durations['word1_english'].append(row['word1_english'] if not pd.isna(row['word1_english']) else '')
        dict_audio_durations['word2'].append(row['word2'] if not pd.isna(row['word2']) else '')
        dict_audio_durations['word2_english'].append(row['word2_english'] if not pd.isna(row['word2_english']) else '')
        dict_audio_durations['word3'].append(row['word3'] if not pd.isna(row['word3']) else '')
        dict_audio_durations['word3_english'].append(row['word3_english'] if not pd.isna(row['word3_english']) else '')
        dict_audio_durations['word4'].append(row['word4'] if not pd.isna(row['word4']) else '')
        dict_audio_durations['word4_english'].append(row['word4_english'] if not pd.isna(row['word4_english']) else '')
        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_component_words'].append(component_words_audio.duration_seconds)
        dict_audio_durations['d_chinese_slow'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_english'].append(english_audio.duration_seconds)
        dict_audio_durations['d_sent'].append(sent_audio.duration_seconds)
        dict_audio_durations['d_sent_english'].append(sent_english_audio.duration_seconds)

        dict_audio_durations['rel_start_chinese'].append(0)
        dict_audio_durations['rel_start_component_words'].append(dict_audio_durations['rel_start_chinese'][-1] + dict_audio_durations['d_chinese'][-1] + 0.5)
        dict_audio_durations['rel_start_english'].append(dict_audio_durations['rel_start_component_words'][-1] + dict_audio_durations['d_component_words'][-1] + dict_audio_durations['d_chinese_slow'][-1] + 1)
        dict_audio_durations['rel_start_sent'].append(dict_audio_durations['rel_start_english'][-1] + dict_audio_durations['d_english'][-1] + 0.5)
        dict_audio_durations['rel_start_sent_english'].append(dict_audio_durations['rel_start_sent'][-1] + dict_audio_durations['d_sent'][-1] + 0.5)

        dict_audio_durations['sum_theory'].append(dict_audio_durations['rel_start_sent_english'][-1] + dict_audio_durations['d_sent_english'][-1] + data_settings['pause_between_words_ms']/1000)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    elif data_settings['recording_id'] in ['ceword_components_csent']:
        sent_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['sentence']}.mp3")
        word1_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word1']}.mp3")
        word1e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word1_english']}.mp3")
        word2_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word2']}.mp3")
        word2e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word2_english']}.mp3")
        if not pd.isna(row['word3']):
            word3_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word3']}.mp3")
            word3e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word3_english']}.mp3")
        if not pd.isna(row['word4']):
            word4_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_zh']}/{row['word4']}.mp3")
            word4e_audio = load_one_audio_from_path(f"output/tts/{data_settings['voice_name_en']}/{row['word4_english']}.mp3")

        component_words_audio = word1_audio + pause_100ms + word1e_audio + pause_500ms + word2_audio + pause_100ms + word2e_audio
        if not pd.isna(row['word3']):
            component_words_audio += pause_500ms + word3_audio + pause_100ms + word3e_audio
        if not pd.isna(row['word4']):
            component_words_audio += pause_500ms + word4_audio + pause_100ms + word4e_audio
        combined = chinese_audio + pause_500ms + component_words_audio + pause_500ms + chinese_audio + pause_500ms + english_audio + pause_500ms + sent_audio + pause_between_words


        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])
        dict_audio_durations['sentence'].append(row['sentence'])
        dict_audio_durations['sentence_pinyin'].append(row['sentence_pinyin'])
        dict_audio_durations['sentence_english'].append(row['sentence_english'])
        dict_audio_durations['word1'].append(row['word1'] if not pd.isna(row['word1']) else '')
        dict_audio_durations['word1_english'].append(row['word1_english'] if not pd.isna(row['word1_english']) else '')
        dict_audio_durations['word2'].append(row['word2'] if not pd.isna(row['word2']) else '')
        dict_audio_durations['word2_english'].append(row['word2_english'] if not pd.isna(row['word2_english']) else '')
        dict_audio_durations['word3'].append(row['word3'] if not pd.isna(row['word3']) else '')
        dict_audio_durations['word3_english'].append(row['word3_english'] if not pd.isna(row['word3_english']) else '')
        dict_audio_durations['word4'].append(row['word4'] if not pd.isna(row['word4']) else '')
        dict_audio_durations['word4_english'].append(row['word4_english'] if not pd.isna(row['word4_english']) else '')
        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_component_words'].append(component_words_audio.duration_seconds)
        dict_audio_durations['d_chinese_slow'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_english'].append(english_audio.duration_seconds)
        dict_audio_durations['d_sent'].append(sent_audio.duration_seconds)

        dict_audio_durations['rel_start_chinese'].append(0)
        dict_audio_durations['rel_start_component_words'].append(dict_audio_durations['rel_start_chinese'][-1] + dict_audio_durations['d_chinese'][-1] + 0.5)
        dict_audio_durations['rel_start_english'].append(dict_audio_durations['rel_start_component_words'][-1] + dict_audio_durations['d_component_words'][-1] + dict_audio_durations['d_chinese_slow'][-1] + 1)
        dict_audio_durations['rel_start_sent'].append(dict_audio_durations['rel_start_english'][-1] + dict_audio_durations['d_english'][-1] + 0.5)

        dict_audio_durations['sum_theory'].append(dict_audio_durations['rel_start_sent'][-1] + dict_audio_durations['d_sent'][-1] + 1)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    elif data_settings['recording_id'] in ['012', 'ec_csent']:
        sent_audio = AudioSegment.from_mp3(f"output/tts/{data_settings['voice_name_zh']}/{row['sentence']}.mp3")
        combined = english_audio + pause_500ms + chinese_audio + pause_500ms + sent_audio + pause_between_words

        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])
        dict_audio_durations['sentence'].append(row['sentence'])
        dict_audio_durations['sentence_pinyin'].append(row['sentence_pinyin'])
        dict_audio_durations['sentence_english'].append(row['sentence_english'])

        dict_audio_durations['d_english'].append(english_audio.duration_seconds)
        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_sent'].append(sent_audio.duration_seconds)

        dict_audio_durations['rel_start_english'].append(0)
        dict_audio_durations['rel_start_chinese'].append(dict_audio_durations['rel_start_english'][-1] + dict_audio_durations['d_english'][-1] + 0.5)
        dict_audio_durations['rel_start_sent'].append(dict_audio_durations['rel_start_chinese'][-1] + dict_audio_durations['d_chinese'][-1] + 0.5)
        dict_audio_durations['sum_theory'].append(dict_audio_durations['rel_start_sent'][-1] + dict_audio_durations['d_sent'][-1] + data_settings['pause_between_words_ms']/1000)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    elif data_settings['recording_id'] in ['ec_csent']:
        sent_audio = AudioSegment.from_mp3(f"output/tts/{data_settings['voice_name_zh']}/{row['sentence']}.mp3")
        combined = chinese_audio + pause_500ms + english_audio + pause_500ms + sent_audio + pause_between_words

        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])
        dict_audio_durations['sentence'].append(row['sentence'])
        dict_audio_durations['sentence_pinyin'].append(row['sentence_pinyin'])
        dict_audio_durations['sentence_english'].append(row['sentence_english'])

        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_english'].append(english_audio.duration_seconds)
        dict_audio_durations['d_sent'].append(sent_audio.duration_seconds)

        dict_audio_durations['rel_start_chinese'].append(0)
        dict_audio_durations['rel_start_english'].append(dict_audio_durations['rel_start_chinese'][-1] + dict_audio_durations['d_chinese'][-1] + 0.5)
        dict_audio_durations['rel_start_sent'].append(dict_audio_durations['rel_start_english'][-1] + dict_audio_durations['d_english'][-1] + 0.5)
        dict_audio_durations['sum_theory'].append(dict_audio_durations['rel_start_sent'][-1] + dict_audio_durations['d_sent'][-1] + data_settings['pause_between_words_ms']/1000)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    elif data_settings['recording_id'] in ['015', 'cn_only_sent']:
        sent_audio = AudioSegment.from_mp3(f"output/tts/{data_settings['voice_name_zh']}/{row['sentence']}.mp3")
        combined = chinese_audio + pause_300ms + sent_audio + pause_between_words

        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])
        dict_audio_durations['sentence'].append(row['sentence'])
        dict_audio_durations['sentence_pinyin'].append(row['sentence_pinyin'])
        dict_audio_durations['sentence_english'].append(row['sentence_english'])

        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds)
        dict_audio_durations['d_sent'].append(sent_audio.duration_seconds)

        dict_audio_durations['rel_start_chinese'].append(0)
        dict_audio_durations['rel_start_sent'].append(dict_audio_durations['rel_start_chinese'][-1] + dict_audio_durations['d_chinese'][-1] + 0.3)
        dict_audio_durations['sum_theory'].append(dict_audio_durations['rel_start_sent'][-1] + dict_audio_durations['d_sent'][-1] + data_settings['pause_between_words_ms']/1000)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    elif data_settings['recording_id'] == 'chinese_only_word_twice':
        sent_audio = AudioSegment.from_mp3(f"output/tts/{data_settings['voice_name_zh']}/{row['sentence']}.mp3")
        combined = chinese_audio + pause_300ms + chinese_audio + pause_between_words

        dict_audio_durations['chinese'].append(row['chinese'])
        dict_audio_durations['pinyin'].append(row['pinyin'])
        dict_audio_durations['english'].append(row['english'])

        dict_audio_durations['d_chinese'].append(chinese_audio.duration_seconds + chinese_audio.duration_seconds + 0.3)

        dict_audio_durations['rel_start_chinese'].append(0)
        dict_audio_durations['sum_theory'].append(dict_audio_durations['d_chinese'][-1] + data_settings['pause_between_words_ms']/1000)
        dict_audio_durations['combined'].append(combined.duration_seconds)

    else:
        raise ValueError(f"Invalid recording_id: {data_settings['recording_id']}")
    
    if 'video_notes' in row.keys():
        dict_audio_durations['video_notes'].append(row['video_notes'])
    
    df_audio_durations = pd.DataFrame(dict_audio_durations)
    return combined, df_audio_durations


def compute_start_times_for_clips(df_durations, recording_settings):
    # Compute columns for video timestamps
    df_durations['end'] = df_durations['combined'].cumsum()
    df_durations['start'] = df_durations['end'] - df_durations['combined']
    if recording_settings['recording_id'] in ['004', '008', '010', '014', '016']:
        df_durations['start_chinese'] = df_durations['start'] + df_durations['rel_start_chinese']
        df_durations['start_english'] = df_durations['start'] + df_durations['rel_start_english']
    elif recording_settings['recording_id'] in ['ceword_components_cesent']:
        df_durations['start_chinese'] = df_durations['start'] + df_durations['rel_start_chinese']
        df_durations['start_component_words'] = df_durations['start'] + df_durations['rel_start_component_words']
        df_durations['start_english'] = df_durations['start'] + df_durations['rel_start_english']
        df_durations['start_sent'] = df_durations['start'] + df_durations['rel_start_sent']
        df_durations['start_sent_english'] = df_durations['start'] + df_durations['rel_start_sent_english']
    elif recording_settings['recording_id'] in ['ceword_components_csent']:
        df_durations['start_chinese'] = df_durations['start'] + df_durations['rel_start_chinese']
        df_durations['start_component_words'] = df_durations['start'] + df_durations['rel_start_component_words']
        df_durations['start_english'] = df_durations['start'] + df_durations['rel_start_english']
        df_durations['start_sent'] = df_durations['start'] + df_durations['rel_start_sent']
    elif recording_settings['recording_id'] == '006':
        df_durations['start_chinese'] = df_durations['start'] + df_durations['rel_start_chinese']
        df_durations['start_component_words'] = df_durations['start'] + df_durations['rel_start_component_words']
        df_durations['start_english'] = df_durations['start'] + df_durations['rel_start_english']
    elif recording_settings['recording_id'] in ['001', 'ce_wordsent']:
        df_durations['start_chinese'] = df_durations['start'] + df_durations['rel_start_chinese']
        df_durations['start_english'] = df_durations['start'] + df_durations['rel_start_english']
        df_durations['start_sent'] = df_durations['start'] + df_durations['rel_start_sent']
        df_durations['start_sent_english'] = df_durations['start'] + df_durations['rel_start_sent_english']
    elif recording_settings['recording_id'] in ['012', 'ec_csent', 'ceword_csent']:
        df_durations['start_english'] = df_durations['start'] + df_durations['rel_start_english']
        df_durations['start_chinese'] = df_durations['start'] + df_durations['rel_start_chinese']
        df_durations['start_sent'] = df_durations['start'] + df_durations['rel_start_sent']
    elif recording_settings['recording_id'] in ['015', 'cn_only_sent']:
        df_durations['start_sent'] = df_durations['start'] + df_durations['rel_start_sent']
    else:
        print('VIDEO NOT MADE FOR RECORDING ID', recording_settings['recording_id'])
    return df_durations


def combine_audio_files_and_compute_durations(df_words, data_settings, making_video=True):
    dfs_audio_durations = []
    for i_row, row in df_words.iterrows():
        start_time = time.time()
        new_folder_path = f"output/rows/{data_settings['recording_id']}"
        new_file_path = f"{new_folder_path}/{row['chinese']}.mp3"
        os.makedirs(new_folder_path, exist_ok=True)

        # Only compute if making video or does not exist
        if making_video or (not os.path.exists(new_file_path)):
            combined, df_audio_durations_onerow = load_audio(row, data_settings)
            dfs_audio_durations.append(df_audio_durations_onerow)
            combined.export(new_file_path, format="mp3")
            print(f"{(time.time()-start_time):.2f} seconds, recid{data_settings['recording_name']}, row {i_row}, {row['chinese']}")
        else:
            print(f"{(time.time()-start_time):.2f} seconds, recid{data_settings['recording_name']}, row {i_row}, {row['chinese']} ALREADY EXISTS")

    # Add in static slide audio into dataframe of audio durations
    df_durations = pd.concat(dfs_audio_durations, ignore_index=True)
    return df_durations


def generate_nonvocab_audio_and_compute_durations(data_settings, df_vocab_audio_durations, nonvocab_slides, project_artifacts_folder):
    # Fill nonvocab audio recordings with data from vocab, if needed
    # Define audio variables
    audio_filler_variables = {
        'audio_duration_minutes': df_vocab_audio_durations['combined'].sum() / 60,
        'n_vocab': len(df_vocab_audio_durations),
    }

    # Fill text for audio recordings
    for nv_name, nv_settings in nonvocab_slides.items():
        if 'chinese' not in nv_settings.keys():
            nonvocab_slides[nv_name]['chinese'] = nv_settings['chinese_unfill'].format(**audio_filler_variables)
            nonvocab_slides[nv_name]['pinyin'] = nv_settings['pinyin_unfill'].format(**audio_filler_variables)
            nonvocab_slides[nv_name]['english'] = nv_settings['english_unfill'].format(**audio_filler_variables)

    # Generate non-vocab recording
    for nv_name, nv_settings in nonvocab_slides.items():
        # Generate audio if not already exists
        nv_settings['file_path'] = f"{project_artifacts_folder}/{nv_settings['chinese']}.mp3"
        if not os.path.exists(nv_settings['file_path']):
            single_tts_call(nv_settings['chinese'], data_settings['voice_name_zh'], nv_settings['file_path'])
            print(f'Generated {nv_settings['chinese']}')
        else:
            print(f'{nv_name} audio already generated: {nv_settings['chinese']}')

        # Insert audio duration into `df_vocab_audio_durations`
        if nv_settings['change_index'] is None:
            nv_settings['change_index'] = len(df_vocab_audio_durations)

        df_vocab_audio_durations.loc[nv_settings['change_index']] = pd.Series({
            'chinese': nv_settings['chinese'],
            'pinyin': nv_settings['pinyin'],
            'english': nv_settings['english'],
            'combined': AudioFileClip(nv_settings['file_path']).duration + nv_settings['pause_ms']/1000,
            'nonvocab_file_path': nv_settings['file_path'],
            'nonvocab_pause_ms': nv_settings['pause_ms'],
            'nonvocab_key': nv_name,
            })

    # Fix indices after adding in non-vocab audio
    df_vocab_audio_durations.index = df_vocab_audio_durations.index + 1
    df_vocab_audio_durations = df_vocab_audio_durations.sort_index().reset_index(drop=True)

    # Compute timestamps for starting each clip
    df_vocab_audio_durations['end'] = df_vocab_audio_durations['combined'].cumsum()
    df_vocab_audio_durations['start'] = df_vocab_audio_durations['end'] - df_vocab_audio_durations['combined']
    if data_settings['recording_id'] in ['004', '008', '010', '014', '016']:
        df_vocab_audio_durations['start_chinese'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_chinese']
        df_vocab_audio_durations['start_english'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_english']
    elif data_settings['recording_id'] in ['ceword_components_cesent']:
        df_vocab_audio_durations['start_chinese'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_chinese']
        df_vocab_audio_durations['start_component_words'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_component_words']
        df_vocab_audio_durations['start_english'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_english']
        df_vocab_audio_durations['start_sent'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_sent']
        df_vocab_audio_durations['start_sent_english'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_sent_english']
    elif data_settings['recording_id'] in ['ceword_components_csent']:
        df_vocab_audio_durations['start_chinese'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_chinese']
        df_vocab_audio_durations['start_component_words'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_component_words']
        df_vocab_audio_durations['start_english'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_english']
        df_vocab_audio_durations['start_sent'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_sent']
    elif data_settings['recording_id'] == '006':
        df_vocab_audio_durations['start_chinese'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_chinese']
        df_vocab_audio_durations['start_component_words'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_component_words']
        df_vocab_audio_durations['start_english'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_english']
    elif data_settings['recording_id'] == '001':
        df_vocab_audio_durations['start_chinese'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_chinese']
        df_vocab_audio_durations['start_english'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_english']
        df_vocab_audio_durations['start_sent'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_sent']
        df_vocab_audio_durations['start_sent_english'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_sent_english']
    elif data_settings['recording_id'] in ['ec_csent', '012']:
        df_vocab_audio_durations['start_english'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_english']
        df_vocab_audio_durations['start_chinese'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_chinese']
        df_vocab_audio_durations['start_sent'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_sent']
    elif data_settings['recording_id'] == '015':
        df_vocab_audio_durations['start_sent'] = df_vocab_audio_durations['start'] + df_vocab_audio_durations['rel_start_sent']
    elif data_settings['recording_id'] in ['chinese_only_word_twice']:
        pass
    else:
        raise ValueError(f"Unsupported recording id {data_settings['recording_id']}")
    
    # Save durations dataframe with static audio as a csv
    df_vocab_audio_durations.to_csv(f"{project_artifacts_folder}/audio_durations_all.csv", index=False)

    # Update nonvocab_slide settings info with duration and start
    for _, row in df_vocab_audio_durations.iterrows():
        if not pd.isna(row['nonvocab_key']):
        # if row['nonvocab_key'] is not None:
            nonvocab_slides[row['nonvocab_key']]['duration'] = row['combined']
            nonvocab_slides[row['nonvocab_key']]['start'] = row['start']
    return df_vocab_audio_durations, audio_filler_variables, nonvocab_slides


def create_final_audio_from_each_word_and_nonvocab(df_vocab_audio_durations, project_artifacts_folder, data_settings):
    start_time = time.time()
    # Construct list of individual audio files
    all_audio_files = []
    for _, row in df_vocab_audio_durations.iterrows():
        if row['nonvocab_file_path'] is not None:
            all_audio_files.append(AudioSegment.from_mp3(row['nonvocab_file_path']))
            all_audio_files.append(AudioSegment.silent(duration=row['nonvocab_pause_ms']))
        else:
            # vocab
            all_audio_files.append(AudioSegment.from_mp3(f"output/rows/{data_settings['recording_id']}/{row['chinese']}.mp3"))

    # Construct and export whole audio file
    audio_concat = all_audio_files[0]
    for audio in all_audio_files[1:]:
        audio_concat += audio
    audio_concat.export(f"{project_artifacts_folder}/audio.mp3", format="mp3")
    print(f"{(time.time()-start_time):.2f}s, {project_artifacts_folder}/audio.mp3")


def create_dataframe_edge_tts_voices():
    # voices = await list_voices()
    voices = list_voices()
    voices = sorted(voices, key=lambda voice: voice["ShortName"])
    dict_voice_list = defaultdict(list)
    for voice in voices:
        dict_voice_list['name'].append(voice['ShortName'])
        dict_voice_list['language'].append(voice['ShortName'].split('-')[0])
        dict_voice_list['country'].append(voice['ShortName'].split('-')[1])
        dict_voice_list['gender'].append(voice['Gender'])
        dict_voice_list['content_categories'].append(", ".join(voice["VoiceTag"]["ContentCategories"]))
        dict_voice_list['personalities'].append(", ".join(voice["VoiceTag"]["VoicePersonalities"]))
    df_voice_list = pd.DataFrame(dict_voice_list)
    # print(len(df_voice_list))
    # df_voice_list[df_voice_list['language']=='zh'].to_csv('static/edge-tts_zh_options.csv')
    # df_voice_list.head()
    return df_voice_list


def generate_example_recordings_from_all_edge_tts_voices(
        example_sent, language, filter_gender=None, filter_country=None, filter_personality=None):
    tts_example_path = f"output/tts/compare/{example_sent}"
    if not os.path.exists(tts_example_path):
        os.mkdir(tts_example_path)

    zh_favs = [
        'Female_Deep, Confident, Casual_XiaoyuMultilingualNeural', # use this one
        'Female_Friendly, Casual, Gentle_XiaobeiNeural',
        'Female_Warm, Animated, Bright_XiaoxiaoDialectsNeural',
        'Male_Casual, Confident, Warm_YunjieNeural',
    ]
    en_fem_favs = [
        'Female_casual, youthful, approachable_NancyMultilingualNeural',
        'Female_Cheerful, Warm, Gentle, Friendly_AdaMultilingualNeural',
        'Female_Crisp, Bright, Clear_NatashaNeural.mp3',
        'Female_Deep, Resonant_NovaTurboMultilingualNeural',
        'Female_Empathetic, Formal, Sincere_CoraMultilingualNeural',
        'Female_formal, confident, mature_SerenaMultilingualNeural',
        'Female_nan_EmilyNeural',
        'Female_nan_LunaNeural',
        'Female_nan_MollyNeural',
        'Female_nan_ShimmerTurboMultilingualNeural',
        'Female_Pleasant, Friendly, Caring_AvaMultilingualNeural', # use this one for now
    ]

    df_tts = pd.read_csv(f'edge-tts_{language}_options.csv', index_col=0)
    df_tts['personalities'] = df_tts['personalities'].fillna('NONE')

    if filter_gender is not None:
        df_tts = df_tts[df_tts['gender'].isin(filter_gender)]
    if filter_country is not None:
        df_tts = df_tts[df_tts['country'].isin(filter_country)]
    if filter_personality is not None:
        df_tts = df_tts[df_tts['personalities'].str.contains(filter_personality)]
    df_tts = df_tts[(~df_tts['name'].str.contains('DragonHD'))].reset_index(drop=True)

    start_time = time.time()
    for _, row in df_tts.iterrows():
        audio_path = f"{tts_example_path}/{row['gender']}_{row['country']}_{row['personalities']}_{row['name'].split('-')[-1].split(':')[0]}.mp3"
        if not os.path.exists(audio_path):
            communicate = Communicate(example_sent, row['name'])
            communicate.save_sync(audio_path)
            print(f"{(time.time() - start_time):.3f}s, {row['name']}")
        else:
            print(f"{(time.time() - start_time):.3f}s, ALREADY GENERATED, {row['name']}")
