Unicode True
!define APP_NAME "InEar SNITCH"
!define APP_EXE "InEarSnitch.exe"
!define INSTALL_DIR "$PROGRAMFILES64\InEar SNITCH"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "${INSTALLER_NAME}"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "Software\InEarSnitch" "Install_Dir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "InEar SNITCH (required)"
  SectionIn RO
  SetOutPath "$INSTDIR"
  File /r "dist\InEarSnitch\*.*"

  ; Desktop shortcut
  CreateShortcut "$DESKTOP\InEar SNITCH.lnk" "$INSTDIR\${APP_EXE}"

  ; Start Menu
  CreateDirectory "$SMPROGRAMS\InEar SNITCH"
  CreateShortcut "$SMPROGRAMS\InEar SNITCH\InEar SNITCH.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\InEar SNITCH\Uninstall.lnk" "$INSTDIR\uninstall.exe"

  ; How to open guide
  File "..\HOW_TO_OPEN_WINDOWS.txt"
  Rename "$INSTDIR\HOW_TO_OPEN_WINDOWS.txt" "$INSTDIR\⚠️ HOW TO OPEN.txt"
  CreateShortcut "$SMPROGRAMS\InEar SNITCH\⚠️ HOW TO OPEN.lnk" "$INSTDIR\⚠️ HOW TO OPEN.txt"

  WriteUninstaller "uninstall.exe"
  WriteRegStr HKLM "Software\InEarSnitch" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\InEarSnitch" "DisplayName" "InEar SNITCH"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\InEarSnitch" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\InEarSnitch" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\InEarSnitch" "Publisher" "InEar SNITCH"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\uninstall.exe"
  RMDir /r "$INSTDIR"
  Delete "$DESKTOP\InEar SNITCH.lnk"
  RMDir /r "$SMPROGRAMS\InEar SNITCH"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\InEarSnitch"
  DeleteRegKey HKLM "Software\InEarSnitch"
SectionEnd
