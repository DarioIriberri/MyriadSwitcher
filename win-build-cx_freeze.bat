rmdir /s /q build
python setup_cx_freeze.py build
xcopy  img build\exe.win32-2.7\img /e /i /h
xcopy  README build\exe.win32-2.7\README /e /i /h
copy  defaults.conf build\exe.win32-2.7\myriadSwitcher.conf /y
copy  activeConfig build\exe.win32-2.7 /y
pause