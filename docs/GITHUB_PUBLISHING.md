# Publish on GitHub / GitHub 发布步骤

The source ZIP is ready to upload. A GitHub repository must first be created by its owner.

## Easiest method (no Git required)
1. Sign in to GitHub, click **New repository**.
2. Repository name: `VocabAudio`; description: `Turn vocabulary lists from PDF/Word into pronunciation MP3s | PDF/Word 词汇表转朗读音频`.
3. Choose **Public**. **Do not** select 'Add a README' or 'Add a license' (both are included).
4. Extract `VocabAudio_GitHub_Source_v1.1.0.zip`.
5. In the new repository, choose **uploading an existing file** and drag in the **contents** of the extracted folder. GitHub's web uploader may not preserve nested folders easily; for reliable full-folder upload use Git commands below instead.
6. Commit as `Initial public release v1.1.0`.
7. Open **Releases → Draft a new release**, create tag `v1.1.0`, paste `RELEASE_NOTES_v1.1.0.md`, and attach the source ZIP if desired.

## Recommended: git command line

```powershell
cd "PATH_TO_EXTRACTED_REPO"
git init
git add .
git commit -m "Initial public release v1.1.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/VocabAudio.git
git push -u origin main
```

GitHub will require account authorization via your local Git credential manager. Do **not** share personal access tokens or passwords in chat. GitHub's Actions page should show the offline test workflow after the first push.

## Important
The source ZIP does not contain any dictionary audio, private user files or a compiled EXE. First public release should be labelled **Source release — requires Python**. No third-party sound recordings are licensed by the MIT LICENSE in this repository. See `docs/RELEASE_CHECKLIST.md` for remaining external-service verification.
