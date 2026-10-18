"""Scoped, safe settings and cache handling for VocabAudio."""
from __future__ import annotations
import json, os, tempfile
from pathlib import Path

APP_DIR_NAME = 'VocabAudio'
DEFAULTS = {'theme':'light','accent':'us','gap':0.8,'speed':1.0,'repeat':1,'open_folder':True,'last_output_dir':''}

def data_dir() -> Path:
    home = os.environ.get('LOCALAPPDATA')
    if home:
        return Path(home) / APP_DIR_NAME
    return Path.home() / '.config' / APP_DIR_NAME

def safe_owned_path(path: Path) -> bool:
    """Allow cleanup only inside exact, private application data folder."""
    root=data_dir().resolve()
    path=Path(path).resolve()
    return path == root or root in path.parents

def load_settings():
    result=DEFAULTS.copy()
    try:
        obj=json.loads((data_dir()/'settings.json').read_text(encoding='utf-8'))
        if isinstance(obj,dict):
            for key in DEFAULTS:
                if key in obj and isinstance(obj[key], type(DEFAULTS[key])):
                    result[key]=obj[key]
    except (OSError, ValueError, TypeError):
        pass
    if result['theme'] not in ('dark','light'): result['theme']='light'
    if result['accent'] not in ('us','uk'): result['accent']='us'
    return result

def save_settings(d):
    root=data_dir();root.mkdir(parents=True,exist_ok=True)
    out={k:d.get(k,v) for k,v in DEFAULTS.items()}
    tmp=root/'settings.tmp'
    tmp.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(tmp,root/'settings.json')

def owned_files():
    root=data_dir()
    if not root.exists():return []
    return [p for p in root.rglob('*') if p.is_file() and safe_owned_path(p)]
