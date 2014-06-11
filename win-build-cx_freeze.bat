rmdir /s /q build
python setup_cx_freeze.py build
rem xcopy  img build\exe.win32-2.7\img /e /i /h
rem xcopy  README build\exe.win32-2.7\README /e /i /h
rem copy  defaults.conf build\exe.win32-2.7\myriadSwitcher.conf /y
rem copy  activeConfig build\exe.win32-2.7 /y
pause