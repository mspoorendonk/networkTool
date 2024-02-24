rem Compile, package and copy the project
rem The && between the commands makes sure that the process stops when an error is encountered
"pyinstaller.exe" --noconfirm "networktool.spec" && "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "inno setup script.iss" && copy /Y "Output\Networktool setup.exe" "G:\My Drive\networktool"
