set appname=Veler
C:\Users\User\AppData\Roaming\Python\Python310\Scripts\pyinstaller.exe .\src\%appname%.py --onefile --noconsole --add-data "img;img"
rmdir /s /q .\build\
move .\dist\%appname%.exe .
rmdir /s /q .\dist\
del %appname%.spec