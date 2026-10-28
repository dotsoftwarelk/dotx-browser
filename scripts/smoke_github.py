"""Optional live GitHub public-search UI check; requires network and available rate limit."""
import os,tempfile
os.environ['XDG_DATA_HOME']=tempfile.mkdtemp(prefix='dotx-github-')
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QDialog,QLineEdit,QPushButton,QListWidget,QLabel
from dotx.__main__ import Browser
app=QApplication([]); app.setOrganizationName('dotsoftwarelk-test'); app.setApplicationName('DOTX-github-test')
w=Browser(); result={'ok':False,'message':'timeout'}
def start():
    dialogs=[x for x in app.topLevelWidgets() if isinstance(x,QDialog) and x.windowTitle()=='GitHub public search']
    if not dialogs: return
    d=dialogs[0]; d.findChild(QLineEdit).setText('repo:dotsoftwarelk/dotx-browser')
    next(b for b in d.findChildren(QPushButton) if b.text()=='Search').click()
    def check():
        values=d.findChild(QListWidget)
        if values.count():
            result['ok']='dotsoftwarelk/dotx-browser' in values.item(0).text()
            result['message']=values.item(0).text(); d.accept()
        else:
            msgs=[label.text() for label in d.findChildren(QLabel)]
            if any('failed' in x.lower() or 'rate limit reached' in x.lower() or 'unavailable' in x.lower() for x in msgs):
                result['message']='; '.join(msgs); d.reject()
            else: QTimer.singleShot(250,check)
    QTimer.singleShot(250,check)
    QTimer.singleShot(20000,d.reject)
QTimer.singleShot(0,start)
w.github_search()
import shiboken6
shiboken6.delete(w)
if not result['ok']: raise SystemExit('FAIL: '+result['message'])
print('PASS: Qt UI, asynchronous live GitHub public search:',result['message'].splitlines()[0])
