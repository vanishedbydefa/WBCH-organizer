# Release build notes

PyInstaller command used to build the Windows executable:

pyinstaller --noconfirm --onefile --console --icon "Q:/edit/icon.png" --name "WBCH-organizer" --clean "Q:/programs/WBCH-organizer/main.py"

Release workflow:
- GitHub Actions builds the exe automatically on published releases
- The workflow also uploads the artifact and attaches the EXE to the GitHub release
- If an icon file exists at the project root or in an assets folder, it is used automatically

How to trigger a release build from the CLI:
- Create a GitHub tag: `git tag v1.0.0`
- Push the tag: `git push origin v1.0.0`
- Or create a release via GitHub CLI: `gh release create v1.0.0 --generate-notes`
- If you want to trigger the workflow manually without a new tag, use: `gh workflow run release-build.yml`

Notes:
- Build output is generated in the dist folder
- The generated EXE is named WBCH-organizer.exe
- Manual workflow trigger is available via the Actions tab