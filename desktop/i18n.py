"""Small explicit translation catalogue; IDs are the English source strings."""
import locale
LANGUAGES = {'en': 'English', 'zh': '简体中文', 'es': 'Español', 'fr': 'Français'}
# Keep rows aligned: English, Simplified Chinese, Spanish, French.
ROWS = [
('Settings', '设置', 'Configuración', 'Réglages'),
('Language', '语言', 'Idioma', 'Langue'),
('Model', '型号', 'Modelo', 'Modèle'),
('USB device', 'USB 设备', 'Dispositivo USB', 'Périphérique USB'),
('Refresh devices', '刷新设备', 'Actualizar dispositivos', 'Actualiser les périphériques'),
('Text colour', '文字颜色', 'Color del texto', 'Couleur du texte'),
('Choose colour', '选择颜色', 'Elegir color', 'Choisir la couleur'),
('Brightness', '亮度', 'Brillo', 'Luminosité'),
('Translation code', '圣经译本代码', 'Código de traducción', 'Code de traduction'),
('Font', '字体', 'Fuente', 'Police'),
('Choose font', '选择字体', 'Elegir fuente', 'Choisir une police'),
('Daily update time', '每日更新时间', 'Hora de actualización', 'Heure de mise à jour'),
('Enable daily updates', '启用每日更新', 'Activar actualizaciones diarias', 'Activer les mises à jour quotidiennes'),
('Start at login', '登录时启动', 'Iniciar al iniciar sesión', 'Démarrer à la connexion'),
('Save settings', '保存设置', 'Guardar configuración', 'Enregistrer les réglages'),
('Preview', '预览', 'Vista previa', 'Aperçu'),
('Test screen', '测试屏幕', 'Probar pantalla', 'Tester l’écran'),
('Update now', '立即更新', 'Actualizar ahora', 'Actualiser maintenant'),
('Restore saved verse', '恢复已保存经文', 'Restaurar versículo guardado', 'Restaurer le verset enregistré'),
('Pause/resume scheduled updates', '暂停/恢复定时更新', 'Pausar/reanudar actualizaciones', 'Suspendre/reprendre les mises à jour'),
('Open logs', '打开日志', 'Abrir registros', 'Ouvrir les journaux'),
('Quit', '退出', 'Salir', 'Quitter'),
('Remove automatic setup', '移除自动设置', 'Eliminar configuración automática', 'Supprimer la configuration automatique'),
('USB help', 'USB 帮助', 'Ayuda USB', 'Aide USB'),
('Fix Linux USB access', '修复 Linux USB 权限', 'Corregir acceso USB en Linux', 'Corriger l’accès USB sous Linux'),
('Next', '下一步', 'Siguiente', 'Suivant'),
('Back', '上一步', 'Atrás', 'Précédent'),
('Finish', '完成', 'Finalizar', 'Terminer'),
('Cancel', '取消', 'Cancelar', 'Annuler'),
('Welcome — connect your screen', '欢迎 — 请连接屏幕', 'Bienvenido: conecta la pantalla', 'Bienvenue — branchez votre écran'),
('Choose the exact model and USB port. Untested models are experimental.', '请选择准确型号和 USB 端口。未经测试的型号为实验性支持。', 'Elige el modelo exacto y el puerto USB. Los modelos no probados son experimentales.', 'Choisissez le modèle exact et le port USB. Les modèles non testés sont expérimentaux.'),
('Appearance and Bible translation', '外观和圣经译本', 'Aspecto y traducción bíblica', 'Apparence et traduction biblique'),
('Choose a Bible Gateway version code, such as CSB, NIV or RVR1960.', '输入 Bible Gateway 译本代码，例如 CSB、NIV 或 CUVS。', 'Introduce un código de Bible Gateway, como CSB, NIV o RVR1960.', 'Saisissez un code Bible Gateway, par exemple CSB, NIV ou LSG.'),
('Test the connection', '测试连接', 'Probar conexión', 'Tester la connexion'),
('Send a test image before enabling automatic updates.', '启用自动更新前，请发送测试图像。', 'Envía una imagen de prueba antes de activar las actualizaciones.', 'Envoyez une image de test avant d’activer les mises à jour.'),
('Automatic updates', '自动更新', 'Actualizaciones automáticas', 'Mises à jour automatiques'),
('Updates run while you are logged in, even after quitting this window.', '登录期间，即使关闭此窗口，仍会进行更新。', 'Las actualizaciones funcionan durante la sesión, incluso al cerrar esta ventana.', 'Les mises à jour fonctionnent pendant votre session, même après fermeture de cette fenêtre.'),
('Ready', '就绪', 'Listo', 'Prêt'),
('Working…', '处理中…', 'Procesando…', 'Traitement…'),
('Done', '完成', 'Completado', 'Terminé'),
('Settings saved', '设置已保存', 'Configuración guardada', 'Réglages enregistrés'),
('Screen disconnected', '屏幕已断开', 'Pantalla desconectada', 'Écran déconnecté'),
('Screen missing or ambiguous. Select its USB port in Settings.', '屏幕缺失或无法唯一识别。请在设置中选择 USB 端口。', 'Pantalla ausente o ambigua. Selecciona su puerto USB en Configuración.', 'Écran absent ou ambigu. Choisissez son port USB dans les réglages.'),
('Operation failed', '操作失败', 'Error de operación', 'Échec de l’opération'),
('Technical details', '技术详情', 'Detalles técnicos', 'Détails techniques'),
('Experimental — hardware untested', '实验性 — 硬件未经测试', 'Experimental: hardware no probado', 'Expérimental — matériel non testé'),
('Tested on Ubuntu', '已在 Ubuntu 上测试', 'Probado en Ubuntu', 'Testé sous Ubuntu'),
('Scheduled updates remain enabled after quitting.', '退出后定时更新仍然启用。', 'Las actualizaciones programadas siguen activas al salir.', 'Les mises à jour programmées restent actives après fermeture.'),
('Quit the app?', '退出应用？', '¿Salir de la aplicación?', 'Quitter l’application ?'),
('Existing schedule detected', '检测到现有计划任务', 'Se detectó una programación existente', 'Programmation existante détectée'),
('Review older schedules to avoid duplicate updates. They have not been changed.', '请检查旧计划任务以避免重复更新。未修改这些任务。', 'Revisa las programaciones anteriores para evitar duplicados. No se han modificado.', 'Vérifiez les anciennes programmations pour éviter les doublons. Elles n’ont pas été modifiées.'),
('Allow access to this USB device?', '允许访问此 USB 设备？', '¿Permitir acceso a este dispositivo USB?', 'Autoriser l’accès à ce périphérique USB ?'),
('Administrator authentication will allow your current session to access the selected USB port. Reconnects may require this again.', '管理员认证将允许当前会话访问所选 USB 端口。重新连接后可能需要再次授权。', 'La autenticación de administrador permitirá acceder al puerto USB seleccionado en esta sesión. Puede ser necesario repetirlo al reconectar.', 'L’authentification administrateur autorisera l’accès au port USB choisi pour cette session. Une reconnexion peut nécessiter une nouvelle autorisation.'),
('Restart the app to apply the interface language.', '请重启应用以应用界面语言。', 'Reinicia la aplicación para aplicar el idioma.', 'Redémarrez l’application pour appliquer la langue.'),
('Automatic setup removed', '自动设置已移除', 'Configuración automática eliminada', 'Configuration automatique supprimée'),
]
CATALOG = {code: {row[0]: row[i] for row in ROWS} for i, code in enumerate(LANGUAGES)}


def system_language():
    try:
        from PySide6.QtCore import QLocale
        value = QLocale.system().name().lower().split('_')[0]
    except ImportError:
        value = (locale.getlocale()[0] or 'en').lower().split('_')[0]
    return value if value in LANGUAGES else 'en'


def translator(language):
    return lambda text: CATALOG.get(language, CATALOG['en']).get(text, text)


def install_qt_translation(app, language):
    from PySide6.QtCore import QLibraryInfo, QTranslator
    translator_object = QTranslator(app)
    suffix = 'zh_CN' if language == 'zh' else language
    translator_object.load('qtbase_' + suffix, QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
    app.installTranslator(translator_object)
    return translator_object
