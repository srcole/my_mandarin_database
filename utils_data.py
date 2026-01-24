import pandas as pd
import numpy as np
import datetime
import os
from constants import default_settings
from collections import defaultdict


def fill_default_settings(data_settings):
    for setting_key, setting_default in default_settings.items():
        if setting_key not in data_settings.keys():
            data_settings[setting_key] = setting_default
    data_settings['recording_name'] = f"{datetime.date.today().strftime("%m%d")}_{data_settings['recording_id']}_{data_settings['filename_suffix']}"
    return data_settings


def load_raw_data(truly_load_data=True):
    if not truly_load_data:
        df = pd.read_csv('static/latest_data.csv')
        print('!!!!!!!! WARNING: not truly loading data !!!!!!!!')
    else:
        cols_keep = [
            'id', 'chinese', 'pinyin', 'english',
            'type', 'priority', 'category1', 'category2', 'cat_v3', 'cat2_v3', 'cat3_v3', 'hsk_level',
            'known', 'known_pinyin_prompt', 'known_english_prompt',
            'quality', 'word1', 'word1_english', 'word2', 'word2_english', 'word3', 'word3_english', 'word4', 'word4_english',
            'voice_zh', 'voice_en', 'video_notes',
            'sentence', 'sentence_pinyin', 'sentence_english',
            'date', 'source1', 'source2', 'funny', 'per', 'adu', 'slang', 'phonetic']
        with open('static/mmd_url.txt', 'r') as file:
            sheet_url = file.read()
        sheet_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
        df = pd.read_csv(sheet_url)[cols_keep]
        df = df.dropna(subset=['chinese', 'english'])
        df['known_english_prompt'] = df['known_english_prompt'].fillna(6)
        df['known_pinyin_prompt'] = df['known_pinyin_prompt'].fillna(6)
        df['hsk_level'] = df['hsk_level'].fillna('MISSING')
        df['quality'] = df['quality'].fillna(6)
        df['per'] = df['per'].fillna(5)
        df['adu'] = df['adu'].fillna(5)
        df['slang'] = df['slang'].fillna(5)
        df['date'] = df['date'].fillna('2025-01-02')
        df['sentence'] = df['sentence'].replace('-', np.nan)
        df.to_csv('static/latest_data.csv', index=False)
    return df


def check_dups(df):
    # Check for duplicates. fix if there are any
    df_dups = df['chinese'].value_counts()
    df_dups = df_dups[df_dups > 1]
    df_dups = df[df['chinese'].isin(df_dups.index)].sort_values(['chinese'])
    return df_dups

def _filter_by_recording_type(df, recording_id):
    """Filter the DataFrame based on the recording type."""
    if recording_id in ['004', '005', '010', '014', '016', 'chinese_only_word_twice', 'cec']:
        return df.dropna(subset=['chinese', 'pinyin', 'english'])
    elif recording_id in ['001', '009', '002', '012', '015', 'cn_only_sent', 'ce_wordsent', 'ec_csent', 'ce_csent', 'cce_cecsent']:
        return df.dropna(subset=['sentence', 'sentence_english'])
    elif recording_id == '006':
        return df.dropna(subset=['word1', 'word1_english', 'word2', 'word2_english'])
    elif recording_id in ['ceword_components_cesent', 'ceword_components_csent', 'ec_csent_scombo']:
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
    

def _extract_components_to_video_notes(row):
    if pd.isna(row['word1']):
        return row['video_notes']
    components = []
    for i in range(1, 5):
        if pd.notna(row[f'word{i}']):
            components.append(f'{row[f'word{i}']}: {row[f'word{i}_english']}')
    video_notes_components = '\n'.join(components)
    if len(row['video_notes']) > 0:
        return row['video_notes'] + '\n--------------------\n' + video_notes_components
    else:
        return video_notes_components


def filter_df_to_vocab_of_interest(df, data_settings):
    if data_settings['different_file_name'] is not None:
        df_filt = pd.read_csv(data_settings['different_file_name'])
        if data_settings['custom_filters'] is not None:
            for custom_filters_dict in data_settings['custom_filters']:
                df_filt = _filter_df(df_filt, **custom_filters_dict)
        cols_to_strip = ['chinese', 'pinyin', 'english', 'sentence', 'sentence_pinyin', 'sentence_english']
        for col_name in cols_to_strip:
            if col_name in df_filt.columns:
                df_filt[col_name] = [x.strip() for x in df_filt[col_name]]

        if data_settings['recording_id'] in ['cconvo']:
            df_filt['video_notes'] = [f'Speaker {s}' for s in df_filt['speaker']]

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
                (df['date'] < data_settings['max_date']) &
                (df['type'].isin(data_settings['types_allowed'])) &
                (df['chinese'].str.contains(data_settings['contains_character']) if data_settings['contains_character'] is not None else True) &
                (df['category1'].isin(data_settings['categories_allowed']) if data_settings['categories_allowed'] is not None else True) &
                (df['category2'].isin(data_settings['categories2_allowed']) if data_settings['categories2_allowed'] is not None else True) &
                (~df['category1'].isin(data_settings['categories_not_allowed']) if data_settings['categories_not_allowed'] is not None else True) &
                (~df['category2'].isin(data_settings['categories2_not_allowed']) if data_settings['categories2_not_allowed'] is not None else True) &
                (df['cat_v3'].isin(data_settings['cat_v3_allowed']) if data_settings['cat_v3_allowed'] is not None else True) &
                (df['cat2_v3'].isin(data_settings['cat2_v3_allowed']) if data_settings['cat2_v3_allowed'] is not None else True) &
                (~df['cat_v3'].isin(data_settings['cat_v3_not_allowed']) if data_settings['cat_v3_not_allowed'] is not None else True) &
                (~df['cat2_v3'].isin(data_settings['cat2_v3_not_allowed']) if data_settings['cat2_v3_not_allowed'] is not None else True) &
                (df['source1'].isin(data_settings['source1_values_allowed']) if data_settings['source1_values_allowed'] is not None else True) &
                (df['hsk_level'].isin(data_settings['hsk_levels_allowed']) if data_settings['hsk_levels_allowed'] is not None else True) &
                (~df['chinese'].isin(data_settings['exclude_words']) if data_settings['exclude_words'] is not None else True)
            ]
        df_filt = _filter_by_recording_type(df_filt, data_settings['recording_id'])
   
    if data_settings['sort_keys'] is not None and data_settings['sort_asc'] is not None:
        df_filt = df_filt.sort_values(data_settings['sort_keys'], ascending=data_settings['sort_asc'])
    if data_settings['silent_components']:
        df_filt['video_notes'] = df_filt['video_notes'].fillna('')
        df_filt['video_notes'] = df_filt.apply(_extract_components_to_video_notes, axis=1)
    df_filt = (df_filt
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


def delete_previous_attempt_files(project_artifacts_folder, data_settings):
    if os.path.exists(f"{project_artifacts_folder}/audio_durations_all.csv"):
        os.remove(f"{project_artifacts_folder}/audio_durations_all.csv")
    if os.path.exists(f"{project_artifacts_folder}/audio_durations_vocab_only.csv"):
        os.remove(f"{project_artifacts_folder}/audio_durations_vocab_only.csv")
    if os.path.exists(data_settings['video_path']):
        os.remove(data_settings['video_path'])
    if os.path.exists(data_settings['audio_path']):
        os.remove(data_settings['audio_path'])


def create_or_load_character_appearances():
    character_appearances_path = 'static/character_appearances.csv'
    if os.path.exists(character_appearances_path):
        print(f"Loading character appearances from {character_appearances_path}")
        df_character_appearances = pd.read_csv(character_appearances_path)
    else:
        print(f"Computing character appearances...")
        df_all_vocab = pd.read_csv('static/latest_data.csv')
        types_allowed = [
            'combo', 'proper noun', 'two word', 'suffix', 'no combo', 'prefix', 'single char', 'slang', 'abbreviation'
        ]
        cols_keep = ['chinese', 'pinyin', 'english', 'priority', 'hsk_level']
        df_all_vocab = df_all_vocab[
            (df_all_vocab['type'].isin(types_allowed)) & 
            (df_all_vocab['adu'] >= 3) &
            (df_all_vocab['per'] >= 3)
            ].reset_index(drop=True)
        df_all_vocab['hsk_level'] = None

        df_all_hsk = pd.read_csv('static/hsk/hsk_1to6_sent.csv', index_col=0)
        hsk_levels_allowed = [1, 2, 3, 4]
        df_all_hsk = df_all_hsk[df_all_hsk['hsk_level'].isin(hsk_levels_allowed)].reset_index(drop=True)
        df_all_hsk['priority'] = 4

        df_all = pd.concat([df_all_vocab[cols_keep], df_all_hsk[cols_keep]]).reset_index(drop=True)
        df_all = df_all.drop_duplicates(subset=['chinese']).reset_index(drop=True)

        dict_character_appearances = defaultdict(list)
        for _, row in df_all.iterrows():
            for char in row['chinese']:
                dict_character_appearances['character'].append(char)
                dict_character_appearances['word'].append(row['chinese'])
                dict_character_appearances['priority'].append(row['priority'])
                dict_character_appearances['hsk_level'].append(row['hsk_level'])
        df_character_appearances = pd.DataFrame(dict_character_appearances)
        df_character_appearances.to_csv('static/character_appearances.csv', index=False)
    return df_character_appearances
