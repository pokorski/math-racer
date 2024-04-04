from . import pl
from . import en

translation = {}
translation['pl'] = pl.Translation()
translation['en'] = en.Translation()

lang = 'pl'

def trans(text_name):
  return translation[lang].messages[text_name]

def trans_level(level_name):
  if level_name not in translation[lang].levels_messages:
    return level_name
  return translation[lang].levels_messages[level_name]

def trans_equations(equations_name):
  if equations_name not in translation[lang].equations_messages:
    return equations_name
  return translation[lang].equations_messages[equations_name]
