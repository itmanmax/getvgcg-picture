@echo off
REM 检查requirements.txt是否存在
IF NOT EXIST requirements.txt (
    echo requirements.txt not found. Please make sure it is in the same directory as this batch file.
    exit /b
)

REM 检查是否已经安装了所有依赖
pip freeze > temp_requirements.txt
FOR /F "tokens=*" %%I IN (requirements.txt) DO (
    FINDSTR /M /C:"%%I" temp_requirements.txt > nul
    IF ERRORLEVEL 1 (
        echo Dependency %%I is not installed. Installing...
        pip install %%I
    )
)
DEL temp_requirements.txt

REM 启动Python脚本
python pictureget.py