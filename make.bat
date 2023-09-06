python -m venv env
call .\env\Scripts\activate.bat
pip install -r .\requirements.txt 

powershell -command "Start-BitsTransfer -Source https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip -Destination ffmpeg.zip"
powershell -command "Expand-Archive ffmpeg.zip ffmpeg"
move .\ffmpeg\ffmpeg* .\ffmpeg\ffmpeg
pyinstaller Kino2Web.spec
pause 