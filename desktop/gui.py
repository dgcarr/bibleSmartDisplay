"""Qt desktop UI. Network and serial operations always run in a worker."""
import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QTime, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QSpinBox, QTimeEdit,
    QCheckBox, QColorDialog, QFileDialog, QMessageBox, QSystemTrayIcon, QMenu,
    QStyle, QWizard, QWizardPage)
from . import core, scheduler
from .i18n import LANGUAGES, translator, system_language


class Worker(QThread):
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, action):
        super().__init__()
        self.action = action

    def run(self):
        try:
            self.action()
            self.done.emit('Done')
        except Exception as exc:
            self.failed.emit(str(exc))


class Settings(QWidget):
    def __init__(self, data, tr):
        super().__init__()
        self.trtext = tr
        self.data = data
        form = QFormLayout(self)
        self.language = QComboBox()
        for code, name in LANGUAGES.items():
            self.language.addItem(name, code)
        self.language.setCurrentIndex(self.language.findData((system_language() if data.get('language', 'auto') == 'auto' else data['language'])))
        form.addRow(tr('Language'), self.language)
        self.model = QComboBox()
        for model in core.engine.MODELS:
            status = tr('Tested on Ubuntu') if model == 'usbpcmonitor-3.5' else tr('Experimental — hardware untested')
            self.model.addItem(f'{model} ({status})', model)
        self.model.setCurrentIndex(self.model.findData(data['model']))
        form.addRow(tr('Model'), self.model)
        self.port = QComboBox()
        form.addRow(tr('USB device'), self.port)
        refresh = QPushButton(tr('Refresh devices'))
        refresh.clicked.connect(self.refresh)
        form.addRow(refresh)
        self.colour = QLineEdit(data['color'])
        form.addRow(tr('Text colour'), self.colour)
        pick = QPushButton(tr('Choose colour'))
        pick.clicked.connect(self.pick_colour)
        form.addRow(pick)
        self.brightness = QSpinBox()
        self.brightness.setRange(0, 100)
        self.brightness.setValue(data['brightness'])
        form.addRow(tr('Brightness'), self.brightness)
        self.version = QLineEdit(data['translation'])
        form.addRow(tr('Translation code'), self.version)
        self.font = QLineEdit(data['font'])
        form.addRow(tr('Font'), self.font)
        font = QPushButton(tr('Choose font'))
        font.clicked.connect(self.pick_font)
        form.addRow(font)
        self.time = QTimeEdit(QTime.fromString(data['time'], 'HH:mm'))
        self.time.setDisplayFormat('HH:mm')
        form.addRow(tr('Daily update time'), self.time)
        self.schedule = QCheckBox(tr('Enable daily updates'))
        self.schedule.setChecked(data['scheduled'])
        form.addRow(self.schedule)
        self.startup = QCheckBox(tr('Start at login'))
        self.startup.setChecked(data['startup'])
        form.addRow(self.startup)
        self.refresh()

    def refresh(self):
        previous = self.port.currentData()
        self.port.clear()
        self.port.addItem('—', None)
        for p in core.engine.list_ports.comports():
            self.port.addItem(f'{p.device} — {p.description}', dict(port=p.device, identity=core.identity(p)))
        desired = previous or dict(port=self.data['port'], identity=self.data['identity'])
        matches = []
        for i in range(1, self.port.count()):
            candidate = self.port.itemData(i)
            if (desired['identity'] and desired['identity'] == candidate['identity']) or (not desired['identity'] and desired['port'] == candidate['port']):
                matches.append(i)
        if len(matches) == 1:
            self.port.setCurrentIndex(matches[0])

    def pick_colour(self):
        value = QColorDialog.getColor(QColor(self.colour.text()), self)
        if value.isValid():
            self.colour.setText(value.name())

    def pick_font(self):
        path, _ = QFileDialog.getOpenFileName(self, self.trtext('Choose font'), '', 'Fonts (*.ttf *.otf *.ttc)')
        if path:
            self.font.setText(path)

    def values(self):
        device = self.port.currentData() or dict(port='', identity=None)
        return core.validate(dict(self.data, **device, model=self.model.currentData(), color=self.colour.text(),
            brightness=self.brightness.value(), translation=self.version.text(), font=self.font.text(),
            time=self.time.time().toString('HH:mm'), scheduled=self.schedule.isChecked(),
            startup=self.startup.isChecked(), language=self.language.currentData()))


class Window(QMainWindow):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.data = core.load(root)
        self.t = translator((system_language() if self.data.get('language', 'auto') == 'auto' else self.data['language']))
        self.setWindowTitle('Bible Smart Display')
        self.worker = None
        self.allow_close = False
        self.connected = False
        self.settings = Settings(self.data, self.t)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.addWidget(self.settings)
        self.status = QLabel(self.t('Ready'))
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview)
        for labels in [('Save settings', 'Preview', 'Test screen'), ('Update now', 'USB help', 'Fix Linux USB access'), ('Remove automatic setup', 'Open logs')]:
            row = QHBoxLayout()
            for label in labels:
                if label == 'Fix Linux USB access' and not sys.platform.startswith('linux'):
                    continue
                button = QPushButton(self.t(label))
                button.clicked.connect(lambda checked=False, key=label: self.action(key))
                row.addWidget(button)
            layout.addLayout(row)
        self.setCentralWidget(body)
        self.tray = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon), self)
        self.tray.setToolTip('Bible Smart Display')
        menu = QMenu(self)
        for label in ('Settings', 'Update now', 'Restore saved verse', 'Pause/resume scheduled updates', 'Open logs', 'Quit'):
            action = menu.addAction(self.t(label))
            action.triggered.connect(lambda checked=False, key=label: self.action(key))
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.show_settings() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(5000)
        self.resize(660, 800)

    def show_settings(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def error(self, message):
        self.status.setText(self.t('Operation failed'))
        box = QMessageBox(QMessageBox.Icon.Warning, self.t('Operation failed'), self.t(message), parent=self)
        box.setDetailedText(message)
        box.exec()

    def work(self, action, done=None):
        if self.worker and self.worker.isRunning():
            return
        self.status.setText(self.t('Working…'))
        self.centralWidget().setEnabled(False)
        self.worker = Worker(action)
        self.worker.done.connect(lambda _: self.complete(done))
        self.worker.failed.connect(self.failed)
        self.worker.start()

    def complete(self, callback):
        self.centralWidget().setEnabled(True)
        self.status.setText(self.t('Done'))
        path = self.root / 'preview.png'
        if path.exists():
            self.preview.setPixmap(QPixmap(str(path)).scaled(480, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        if callback:
            callback()

    def failed(self, message):
        self.centralWidget().setEnabled(True)
        self.error(message)

    def persist(self, data):
        # Save first so a newly loaded OS job sees these settings immediately.
        old = core.load(self.root)
        core.save(self.root, data)
        try:
            scheduler.configure(self.root, data)
        except Exception:
            core.save(self.root, old)
            try:
                scheduler.configure(self.root, old)
            except Exception:
                pass
            raise

    def action(self, label):
        try:
            if label == 'Settings':
                self.show_settings()
            elif label == 'Quit':
                if self.worker and self.worker.isRunning():
                    return
                text = self.t('Scheduled updates remain enabled after quitting.') if self.data['scheduled'] else self.t('Quit the app?')
                if QMessageBox.question(self, self.t('Quit'), text) == QMessageBox.StandardButton.Yes:
                    self.allow_close = True
                    QApplication.quit()
            elif label == 'Open logs':
                self.root.mkdir(parents=True, exist_ok=True)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.root)))
            elif label == 'USB help':
                QDesktopServices.openUrl(QUrl('https://github.com/dgcarr/bibleSmartDisplay/blob/main/README.md#usb-drivers'))
            elif label == 'Fix Linux USB access':
                data = self.settings.values()
                port = Path(core.resolve(data)).resolve()
                if not str(port).startswith(('/dev/ttyACM', '/dev/ttyUSB')) or not port.is_char_device():
                    raise ValueError('Select a USB serial device first.')
                text = self.t('Administrator authentication will allow your current session to access the selected USB port. Reconnects may require this again.')
                if QMessageBox.question(self, self.t('Allow access to this USB device?'), text) == QMessageBox.StandardButton.Yes:
                    from .permissions import repair
                    self.work(lambda: repair(data, port))
            elif label in ('Save settings', 'Pause/resume scheduled updates', 'Remove automatic setup'):
                data = self.settings.values() if label == 'Save settings' else dict(self.data)
                if label == 'Pause/resume scheduled updates':
                    data['scheduled'] = not data['scheduled']
                if label == 'Remove automatic setup':
                    data.update(scheduled=False, startup=False)
                if data['scheduled']:
                    core.resolve(data)
                def saved():
                    self.data = data
                    self.settings.schedule.setChecked(data['scheduled'])
                    self.settings.startup.setChecked(data['startup'])
                    self.status.setText(self.t('Settings saved'))
                    if data.get('language') != self.t_language:
                        QMessageBox.information(self, self.t('Language'), self.t('Restart the app to apply the interface language.'))
                self.work(lambda: self.persist(data), saved)
            else:
                mode = {'Preview': 'preview', 'Test screen': 'test', 'Update now': 'update', 'Restore saved verse': 'restore'}[label]
                data = self.settings.values()
                self.work(lambda: core.run(self.root, data, mode))
        except Exception as exc:
            self.error(str(exc))

    @property
    def t_language(self):
        return system_language() if self.settings.data.get('language', 'auto') == 'auto' else self.settings.data['language']

    def poll(self):
        if (self.worker and self.worker.isRunning()) or not (self.root / 'settings.json').exists():
            return
        try:
            self.data = core.load(self.root)
            core.resolve(self.data)
            if not self.connected:
                self.connected = True
                if (self.root / 'last-verse.json').exists():
                    data = dict(self.data)
                    self.work(lambda: core.run(self.root, data, 'restore'))
        except ValueError:
            self.connected = False
            self.status.setText(self.t('Screen disconnected'))

    def closeEvent(self, event):
        if not self.allow_close and QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
            event.ignore()
        elif self.worker and self.worker.isRunning():
            event.ignore()
        else:
            event.accept()


class TestPage(QWizardPage):
    def __init__(self, window):
        super().__init__()
        self.passed = False
        self.window = window
        self.setTitle(window.t('Test the connection'))
        self.setSubTitle(window.t('Send a test image before enabling automatic updates.'))
        layout = QVBoxLayout(self)
        self.label = QLabel(window.t('Ready'))
        layout.addWidget(self.label)
        button = QPushButton(window.t('Test screen'))
        button.clicked.connect(self.test)
        layout.addWidget(button)
        help_button = QPushButton(window.t('USB help'))
        help_button.clicked.connect(lambda: window.action('USB help'))
        layout.addWidget(help_button)
        if sys.platform.startswith('linux'):
            fix = QPushButton(window.t('Fix Linux USB access'))
            fix.clicked.connect(lambda: window.action('Fix Linux USB access'))
            layout.addWidget(fix)

    def initializePage(self):
        self.passed = False
        self.completeChanged.emit()

    def isComplete(self):
        return self.passed

    def test(self):
        try:
            data = self.window.settings.values()
            self.label.setText(self.window.t('Working…'))
            def success():
                self.passed = True
                self.label.setText(self.window.t('Done'))
                self.completeChanged.emit()
            self.window.work(lambda: core.run(self.window.root, data, 'test'), success)
        except Exception as exc:
            self.window.error(str(exc))


class SetupWizard(QWizard):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.setWindowModality(Qt.WindowModality.WindowModal)
        t = window.t
        self.setWindowTitle('Bible Smart Display')
        for which, label in [(QWizard.WizardButton.NextButton, 'Next'), (QWizard.WizardButton.BackButton, 'Back'), (QWizard.WizardButton.FinishButton, 'Finish'), (QWizard.WizardButton.CancelButton, 'Cancel')]:
            self.setButtonText(which, t(label))
        settings = window.settings
        form = settings.layout()
        rows = [form.takeRow(0) for _ in range(form.rowCount())]
        def page(title, description, indices):
            result = QWizardPage()
            result.setTitle(t(title))
            result.setSubTitle(t(description))
            layout = QFormLayout(result)
            for index in indices:
                row = rows[index]
                label = row.labelItem.widget() if row.labelItem else None
                field = row.fieldItem.widget()
                if label:
                    layout.addRow(label, field)
                else:
                    layout.addRow(field)
            return result
        self.addPage(page('Welcome — connect your screen', 'Choose the exact model and USB port. Untested models are experimental.', range(4)))
        self.addPage(page('Appearance and Bible translation', 'Choose a Bible Gateway version code, such as CSB, NIV or RVR1960.', range(4, 10)))
        self.addPage(TestPage(window))
        self.addPage(page('Automatic updates', 'Updates run while you are logged in, even after quitting this window.', range(10, 13)))
        settings.schedule.setChecked(True)
        settings.startup.setChecked(True)
        self.resize(650, 480)

    def accept(self):
        try:
            data = self.window.settings.values()
            def saved():
                self.window.data = data
                self.restore(data)
                super(SetupWizard, self).accept()
            self.window.work(lambda: self.window.persist(data), saved)
        except Exception as exc:
            self.window.error(str(exc))

    def restore(self, data):
        old = self.window.settings
        self.window.settings = Settings(data, self.window.t)
        self.window.centralWidget().layout().replaceWidget(old, self.window.settings)
        old.deleteLater()

    def reject(self):
        if self.window.worker and self.window.worker.isRunning():
            return
        self.restore(self.window.data)
        super().reject()


def start(root, tray=False, smoke=False):
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName('Bible Smart Display')
    app.setQuitOnLastWindowClosed(not QSystemTrayIcon.isSystemTrayAvailable())
    window = Window(root)
    if not tray or not QSystemTrayIcon.isSystemTrayAvailable() or not (root / 'settings.json').exists():
        window.show()
    if smoke:
        QTimer.singleShot(500, app.quit)
    elif not (root / 'settings.json').exists():
        window.wizard = SetupWizard(window)
        window.wizard.show()
        try:
            legacy = scheduler.legacy_jobs()
            if legacy:
                QMessageBox.information(window, window.t('Existing schedule detected'), window.t('Review older schedules to avoid duplicate updates. They have not been changed.') + '\n\n' + legacy)
        except OSError:
            pass
    return app.exec()
