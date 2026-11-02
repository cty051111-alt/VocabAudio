# VocabAudio 2.1 Beta validation (2026-11-02)

- Local Windows x64 / Python 3.13: 21 automated tests passed, including real offline OCR with socket access blocked, image validation, clipboard import, editable OCR review, append, cancellation, and theme switching.
- Real Qt windows rendered and visually inspected in light and dark themes; original plugin UI reference reviewed from the user's October 19 workspace.
- Source runtime self-test passed: real offline OCR, both UI themes and FFmpeg execution.
- Live pronunciation smoke check: apple and banana both downloaded and were combined into a 101189-byte MP3 with two repetitions and 400 ms gaps. This does not guarantee service availability for other words or future requests.
- Frozen Windows EXE: build and offline runtime verification are performed by scripts/build_windows.py before it creates the release ZIP. Presence of a ZIP produced by that successful script and its self-test.txt report is the verification record. Do not interpret this document alone as proof that a build passed.
- The user-supplied error screenshot was also recognized locally: both English exception text and Chinese error text were extracted. Personal vocabulary photos and handwriting have not yet been evaluated. Automatic scan-PDF OCR is outside this upgrade.
- GitHub Actions status is separate from local validation. No CI result or published release is claimed here.
