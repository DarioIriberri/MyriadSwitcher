rmdir /s /q build
rmdir /s /q ..\build
python setup_cx_freeze_x84.py build
xcopy ..\img build\exe.win32-2.7\img /e /i /h
xcopy ..\README build\exe.win32-2.7\README /e /i /h
copy ..\config\*.* build\exe.win32-2.7\ /y
xcopy ..\miners build\exe.win32-2.7\miners /e /i /h
xcopy ..\wallets build\exe.win32-2.7\wallets /e /i /h
rem copy ..\config\activeConfig build\exe.win32-2.7 /y
xcopy build ..\build /e /i /h
rmdir /s /q build
pause