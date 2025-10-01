import pandas as pd
import datetime
import os
from constants import default_settings


def fill_default_settings(data_settings):
    for setting_key, setting_default in default_settings.items():
        if setting_key not in data_settings.keys():
            data_settings[setting_key] = setting_default
    data_settings['recording_name'] = f"{datetime.date.today().strftime("%m%d")}_{data_settings['recording_id']}_{data_settings['filename_suffix']}"
    return data_settings


def load_raw_data():
    cols_keep = [
        'id', 'chinese', 'pinyin', 'english',
        'type', 'priority', 'known', 'known_pinyin_prompt', 'known_english_prompt',
        'phonetic', 'category1', 'category2', 'quality',
        'word1', 'word1_english', 'word2', 'word2_english', 'word3', 'word3_english', 'word4', 'word4_english',
        'sentence', 'sentence_pinyin', 'sentence_english', 'date', 'cat1', 'per', 'adu']
    sheet_url = 'https://docs.google.com/spreadsheets/d/1pw9EAIvtiWenPDBFBIf7pwTh0FvIbIR0c3mY5gJwlDk/edit#gid=0'
    sheet_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    df = pd.read_csv(sheet_url)[cols_keep]
    df = df.dropna(subset=['chinese', 'english'])
    df['known_english_prompt'] = df['known_english_prompt'].fillna(6)
    df['known_pinyin_prompt'] = df['known_pinyin_prompt'].fillna(6)
    df['quality'] = df['quality'].fillna(6)
    df['per'] = df['per'].fillna(5)
    df['adu'] = df['adu'].fillna(5)
    df['date'] = df['date'].fillna('2025-01-02')
    return df


def check_dups(df):
    # Check for duplicates. fix if there are any
    df_dups = df['chinese'].value_counts()
    df_dups = df_dups[df_dups > 1]
    df_dups = df[df['chinese'].isin(df_dups.index)].sort_values(['chinese'])
    return df_dups

def _filter_by_recording_type(df, recording_id):
    """Filter the DataFrame based on the recording type."""
    if recording_id in ['004', '005', '010', '014', '016', 'chinese_only_word_twice']:
        return df.dropna(subset=['chinese', 'pinyin', 'english'])
    elif recording_id in ['001', '009', '002', '012', '015', 'cn_only_sent', 'ce_wordsent', 'ec_csent']:
        return df.dropna(subset=['sentence', 'sentence_english'])
    elif recording_id == '006':
        return df.dropna(subset=['word1', 'word1_english', 'word2', 'word2_english'])
    elif recording_id in ['ceword_components_cesent', 'ceword_components_csent']:
        return df.dropna(subset=['word1', 'word1_english', 'word2', 'word2_english', 'sentence'])
    elif recording_id == '007':
        return df[df['date'] >= '2025-07-15'].dropna(subset=['sentence', 'sentence_english'])
    elif recording_id == '008':
        return df[df['date'] >= '2025-07-15']
    else:
        raise ValueError(f"Invalid recording ID: {recording_id}")
    

def _filter_df(df, col_name, val, operator_str):
    if operator_str == '>=':
        return df[df[col_name] >= val]
    elif operator_str == '<=':
        return df[df[col_name] <= val]
    else:
        raise ValueError(f"Unknown operator_str: {operator_str}")


def filter_df_to_vocab_of_interest(df, data_settings):
    if data_settings['different_file_name'] is not None:
        df_filt = pd.read_csv(data_settings['different_file_name'])
        if data_settings['custom_filters'] is not None:
            for custom_filters_dict in data_settings['custom_filters']:
                df_filt = _filter_df(df_filt, **custom_filters_dict)
        cols_to_strip = ['chinese', 'pinyin', 'english', 'sentence', 'sentence_pinyin', 'sentence_english']
        for col_name in cols_to_strip:
            df_filt[col_name] = [x.strip() for x in df_filt[col_name]]

    else:
        df_filt = df[
                (df['priority'] <= data_settings['max_priority']) &
                (df['priority'] >= data_settings['min_priority']) &
                (df['known_english_prompt'] >= data_settings['min_known_english_prompt']) &
                (df['known_english_prompt'] <= data_settings['max_known_english_prompt']) &
                (df['known_pinyin_prompt'] >= data_settings['min_known_pinyin_prompt']) &
                (df['known_pinyin_prompt'] <= data_settings['max_known_pinyin_prompt']) &
                (df['quality'] <= data_settings['min_combo_quality']) &
                (df['adu'] >= data_settings['min_adu']) &
                (df['per'] >= data_settings['min_per']) &
                (df['date'] >= data_settings['min_date']) &
                (df['type'].isin(data_settings['types_allowed'])) &
                (df['chinese'].str.contains(data_settings['contains_character']) if data_settings['contains_character'] is not None else True) &
                (df['category1'].isin(data_settings['categories_allowed']) if data_settings['categories_allowed'] is not None else True) &
                (df['category2'].isin(data_settings['categories2_allowed']) if data_settings['categories2_allowed'] is not None else True) &
                (df['cat1'].isin(data_settings['cat1_values_allowed']) if data_settings['cat1_values_allowed'] is not None else True) &
                (~df['chinese'].isin(data_settings['exclude_words']) if data_settings['exclude_words'] is not None else True)
            ]
        df_filt = _filter_by_recording_type(df_filt, data_settings['recording_id'])
                                            
    df_filt = (df_filt
        .sort_values(data_settings['sort_keys'], ascending=data_settings['sort_asc'])
        .reset_index(drop=True)
        .head(data_settings['max_count'])
        )
    return df_filt


def pinyin_to_tones(pinyin):
    """Convert pinyin to tones."""
    pinyin = pinyin.replace('ā', 'a1').replace('á', 'a2').replace('ǎ', 'a3').replace('à', 'a4')
    pinyin = pinyin.replace('ē', 'e1').replace('é', 'e2').replace('ě', 'e3').replace('è', 'e4')
    pinyin = pinyin.replace('ī', 'i1').replace('í', 'i2').replace('ǐ', 'i3').replace('ì', 'i4')
    pinyin = pinyin.replace('ō', 'o1').replace('ó', 'o2').replace('ǒ', 'o3').replace('ò', 'o4')
    pinyin = pinyin.replace('ū', 'u1').replace('ú', 'u2').replace('ǔ', 'u3').replace('ù', 'u4')
    pinyin = pinyin.replace('ü', 'v1').replace('ǘ', 'v2').replace('ǚ', 'v3').replace('ǜ', 'v4')
    tones = []
    for pinyin_oneword in pinyin.split():
        tone = '1'  # Default tone
        for i in range(1, 5):
            if f'{i}' in pinyin_oneword:
                tone = str(i)
                break
        tones.append(tone)
    return tones


def delete_previous_attempt_files(project_artifacts_folder):
    if os.path.exists(f"{project_artifacts_folder}/audio_durations_all.csv"):
        os.remove(f"{project_artifacts_folder}/audio_durations_all.csv")
    if os.path.exists(f"{project_artifacts_folder}/audio_durations_vocab_only.csv"):
        os.remove(f"{project_artifacts_folder}/audio_durations_vocab_only.csv")
    if os.path.exists(f"{project_artifacts_folder}/video.mp4"):
        os.remove(f"{project_artifacts_folder}/video.mp4")
    if os.path.exists(f"{project_artifacts_folder}/audio.mp3"):
        os.remove(f"{project_artifacts_folder}/audio.mp3")
