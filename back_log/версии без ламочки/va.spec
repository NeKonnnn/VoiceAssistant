# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['va.py'],
    pathex=[],
    binaries=[],
    datas=[('F:/voice_assistant/VoiceAssistant/icons', 'icons'), ('F:/voice_assistant/VoiceAssistant/model_small', 'model_small'), ('F:/voice_assistant/VoiceAssistant/silero_models', 'silero_models'), ('F:/voice_assistant/VoiceAssistant/commands', 'commands'), ('F:/voice_assistant/VoiceAssistant/configurations', 'configurations'), ('F:/voice_assistant/VoiceAssistant/voice_assistant_gui', 'voice_assistant_gui'), ('F:/voice_assistant/VoiceAssistant/microphone_new.py', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='va',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['F:\\voice_assistant\\VoiceAssistant\\icons\\my_icon.ico'],
)
