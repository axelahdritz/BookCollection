from spellchecker import SpellChecker
import json

def spell_it_correctly(lang, dic_file_name_path):
    if lang == 'eng':
        spell = SpellChecker()
    else:
        spell = SpellChecker(language=None, case_sensitive=False)
        spell.word_frequency.load_dictionary(dic_file_name_path)

def create_dictionary(txt_file_path, dic_file_name_path):
    spell = SpellChecker(language=None, case_sensitive=False)
    spell.word_frequency.load_text_file(txt_file_path)
    spell.export(dic_file_name_path, gzipped=True)
    return dic_file_name_path