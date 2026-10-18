import json
from pathlib import Path
import settings_store as store

def test_settings_round_trip(monkeypatch, tmp_path):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    assert store.load_settings()['theme'] == 'light'
    config = dict(store.DEFAULTS, theme='dark', accent='uk', repeat=3)
    store.save_settings(config)
    assert store.load_settings()['theme'] == 'dark'
    assert store.load_settings()['repeat'] == 3

def test_settings_corrupted_file_uses_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    folder = store.data_dir();folder.mkdir(parents=True)
    (folder/'settings.json').write_text('not json',encoding='utf-8')
    assert store.load_settings()['accent'] == 'us'

def test_safe_path(monkeypatch,tmp_path):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    assert store.safe_owned_path(store.data_dir()/'settings.json')
    assert not store.safe_owned_path(tmp_path/'some_wordlist.pdf')
