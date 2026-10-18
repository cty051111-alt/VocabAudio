import subprocess
from pathlib import Path
from unittest.mock import patch
import vocab_core as core

def test_repeat_range_validation(tmp_path):
    with __import__('pytest').raises(ValueError,match='重复次数'):
        core.render_audio(['acquire'],tmp_path/'a.mp3',repeat=6)

def test_repeat_output_uses_each_clip_twice(tmp_path, monkeypatch):
    # This test uses a fake executable and checks concat lists rather than making network calls.
    paths=[]
    class FakeProcess:
        returncode=0
        stderr=''
    def fake_run(cmd,**kw):
        if '-f' in cmd and 'concat' in cmd:
            manifest=Path(cmd[cmd.index('-i')+1]).read_text()
            assert manifest.count("file '")==4
        Path(cmd[-1]).write_bytes(b'mock'+b' '*600)
        return FakeProcess()
    monkeypatch.setattr(core,'fetch_clip',lambda word,dest,*a,**k:Path(dest).write_bytes(b'a'*600))
    monkeypatch.setattr(core,'ffmpeg_executable',lambda:'/bin/true')
    monkeypatch.setattr(core.subprocess,'run',fake_run)
    words,fail=core.render_audio(['acquire','adopt'],tmp_path/'result.mp3',repeat=2)
    assert words==['acquire','adopt'] and not fail
