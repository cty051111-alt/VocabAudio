# Windows Release checklist

1. `python -m pytest -q` passes locally.
2. GitHub Actions `Build Windows no-Python EXE` completes on `windows-latest`.
3. Frozen `VocabAudio.exe --self-test` succeeds on the GitHub runner.
4. Download the Actions ZIP and test it manually on clean Windows PC that does NOT have Python installed.
5. Import a real seven-column DOCX and searchable PDF, verify extracted word order.
6. Generate a short MP3 using a permitted online pronunciation source. Verify actual audio, durations, speed and pauses.
7. Test failure reporting when there is no internet and when a word has no audio.
8. Check unsigned Windows SmartScreen behavior and basic antivirus compatibility.
9. Verify licence obligations for PyInstaller's bundled dependencies and third-party audio.
10. Push a `v*` Git tag to create a downloadable GitHub Release ZIP.

Do not describe the EXE as fully tested on end-user computers until steps 4–8 have been completed.
