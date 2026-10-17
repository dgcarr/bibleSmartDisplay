"""Graphical Linux per-user installation; no shell interpolation."""
import shutil
import subprocess
from .system import host_environment
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from .i18n import system_language, install_qt_translation

TEXT = {
 'en': ('Install Bible Smart Display?', 'Install for this user and add an application-menu shortcut?', 'Installation complete'),
 'zh': ('安装 Bible Smart Display？', '为当前用户安装并添加应用菜单快捷方式？', '安装完成'),
 'es': ('¿Instalar Bible Smart Display?', '¿Instalar para este usuario y añadir un acceso al menú de aplicaciones?', 'Instalación completada'),
 'fr': ('Installer Bible Smart Display ?', 'Installer pour cet utilisateur et ajouter un raccourci au menu des applications ?', 'Installation terminée'),
}


def install():
    app = QApplication.instance() or QApplication([])
    qt_translation = install_qt_translation(app, system_language())
    title, question, complete = TEXT[system_language()]
    if QMessageBox.question(None, title, question) != QMessageBox.StandardButton.Yes:
        return 0
    source = Path(sys.executable).resolve().parent
    target = Path.home() / '.local/opt/bibleSmartDisplay'
    if source == target:
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(target.name + '.new')
    shutil.rmtree(staging, ignore_errors=True)
    shutil.copytree(source, staging)
    old = target.with_name(target.name + '.old')
    shutil.rmtree(old, ignore_errors=True)
    if target.exists():
        target.rename(old)
    staging.rename(target)
    applications = Path.home() / '.local/share/applications'
    applications.mkdir(parents=True, exist_ok=True)
    exe = str(target / 'BibleSmartDisplay').replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
    (applications / 'biblesmartdisplay.desktop').write_text('[Desktop Entry]\nType=Application\nName=Bible Smart Display\nExec="' + exe + '"\nIcon=video-display\nTerminal=false\nCategories=Utility;\n')
    QMessageBox.information(None, title, complete)
    subprocess.Popen([str(target / 'BibleSmartDisplay')], start_new_session=True, env=host_environment())
    return 0
