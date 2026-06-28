; Stock Signal Bot - NSIS Installer Script
; Packages the PyInstaller-built EXE into a Windows installer.
; Requires: build_windows.py run first to create dist/StockBot.exe
;
; Build: makensis setup\installer.nsi
; Requires: NSIS (https://nsis.sourceforge.io/)

Unicode True

!define PRODUCT_NAME "Stock Signal Bot"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "StockBot"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "..\dist\StockBot_Setup.exe"
InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"
RequestExecutionLevel admin

; Pages
Page components
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

; Section: Main Application (required)
Section "Stock Signal Bot" SEC_MAIN
    SectionIn RO

    SetOutPath "$INSTDIR"

    ; Package the standalone executable (built by build_windows.py)
    File "..\dist\StockBot.exe"

    ; Create Start Menu shortcut
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Stock Signal Bot.lnk" "$INSTDIR\StockBot.exe"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"

    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Registry for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

; Section: Desktop Shortcut (optional)
Section "Create Desktop Shortcut" SEC_DESKTOP
    CreateShortCut "$DESKTOP\Stock Signal Bot.lnk" "$INSTDIR\StockBot.exe"
SectionEnd

; Uninstaller
Section "Uninstall"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\*.*"
    RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
    Delete "$DESKTOP\Stock Signal Bot.lnk"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
SectionEnd
