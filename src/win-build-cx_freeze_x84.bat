rmdir /s /q build
rmdir /s /q ..\build
python setup_cx_freeze_x84.py build
xcopy ..\img build\exe.win32-2.7\img /e /i /h
xcopy ..\README build\exe.win32-2.7\README /e /i /h
copy ..\config\defaults.conf build\exe.win32-2.7\myriadSwitcher.conf /y
copy ..\config\activeConfig build\exe.win32-2.7 /y
xcopy build ..\build /e /i /h
rmdir /s /q build
pause