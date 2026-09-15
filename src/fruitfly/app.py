"""Event-driven tray supervisor. No polling timer when disabled."""
import json
import os
from pathlib import Path
import signal
import sys
import time
from shiboken6 import isValid

from PySide6.QtCore import QObject,QProcess,QProcessEnvironment,QSocketNotifier,QTimer
from PySide6.QtGui import QAction,QIcon
from PySide6.QtNetwork import QLocalServer,QLocalSocket
from PySide6.QtWidgets import QApplication,QMenu,QSystemTrayIcon

from .core import ROOT
from .__main__ import socket_path,request


class Supervisor(QObject):
    def __init__(self,app,renderer="software"):
        super().__init__();self.app=app;self.enabled=False;self.error=None
        self.renderer=renderer
        self.metrics={"ticks":0,"queries":0,"backend":"native-cpu","renderer":renderer}
        self.clients={};self.viewers=set();self.last_frame={"visible":False}
        self.worker_buffer=b"";self.closing=False;self.worker_ready=False
        self.dir=socket_path().parent
        self.dir.mkdir(mode=0o700,parents=True,exist_ok=True)
        if self.dir.stat().st_uid!=os.getuid():raise RuntimeError("Runtime directory has another owner")
        os.chmod(self.dir,0o700)
        self.server=QLocalServer(self)
        self.server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
        if not self.server.listen(str(socket_path())):
            raise RuntimeError("Control socket already exists; check running instance or stale socket")
        self.server.newConnection.connect(self.accept)
        self.tray=QSystemTrayIcon(self);self.menu=QMenu()
        self.toggle=QAction("Mosca ligada",self.menu);self.toggle.setCheckable(True)
        self.toggle.triggered.connect(lambda checked:self.set_enabled(checked,"menu"));self.menu.addAction(self.toggle)
        quit_action=self.menu.addAction("Encerrar");quit_action.triggered.connect(app.quit)
        self.tray.setContextMenu(self.menu);self.tray.activated.connect(self.activated)
        self.refresh_tray();self.tray.show()
        self.worker=QProcess(self);self.worker.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.worker.readyReadStandardOutput.connect(self.read_worker)
        self.worker.readyReadStandardError.connect(self.worker_stderr)
        self.worker.finished.connect(self.worker_finished)
        self.worker.started.connect(self.worker_started)
        self.worker.errorOccurred.connect(lambda _error:self.fail("Falha no processo neural") if self.enabled else None)
        self.overlay=QProcess(self)
        self.overlay.setProcessChannelMode(QProcess.ProcessChannelMode.ForwardedChannels)
        self.overlay.finished.connect(self.overlay_finished)
        self.overlay.errorOccurred.connect(lambda _error:self.fail("Falha no processo de sobreposição") if self.enabled else None)
        self.watchdog=QTimer(self);self.watchdog.setSingleShot(True);self.watchdog.setInterval(3000)
        self.watchdog.timeout.connect(lambda:self.fail("O cérebro deixou de responder"))
        # Wake Qt on signals without a periodic signal-polling timer.
        self.sig_r,self.sig_w=os.pipe2(os.O_NONBLOCK|os.O_CLOEXEC)
        self.old_wakeup=signal.set_wakeup_fd(self.sig_w)
        self.notifier=QSocketNotifier(self.sig_r,QSocketNotifier.Type.Read,self)
        self.notifier.activated.connect(self.signal_received)
        signal.signal(signal.SIGTERM,lambda *_:None)
        signal.signal(signal.SIGINT,lambda *_:None)
        app.aboutToQuit.connect(self.shutdown)

    def signal_received(self,*_):
        os.read(self.sig_r,4096);self.app.quit()

    def activated(self,reason):
        if reason==QSystemTrayIcon.ActivationReason.Trigger:self.set_enabled(not self.enabled,"icon")

    def refresh_tray(self):
        self.tray.setIcon(QIcon(str(ROOT/"assets"/("tray.svg" if self.enabled else "tray-off.svg"))))
        state="erro" if self.error else "ligada" if self.enabled else "desligada"
        self.tray.setToolTip(f"FruitFly: {state}"+(f"\n{self.error}" if self.error else ""))
        self.toggle.blockSignals(True);self.toggle.setChecked(self.enabled);self.toggle.blockSignals(False)

    def send_worker(self,command):
        if self.worker_ready:self.worker.write((json.dumps({"command":command})+"\n").encode())

    def worker_started(self):
        self.worker_ready=True
        self.send_worker("enable" if self.enabled else "disable")

    def set_enabled(self,value,source="tray"):
        value=bool(value)
        if value==self.enabled:return
        print(json.dumps({"event":"enabled","value":value,"source":source,"time":time.monotonic()}),flush=True)
        if value and not QSystemTrayIcon.isSystemTrayAvailable():
            self.error="Bandeja indisponível";self.refresh_tray();return
        self.enabled=value;self.error=None;self.refresh_tray()
        if value:
            env=QProcessEnvironment.systemEnvironment()
            env.insert("PYTHONPATH",str(ROOT/"src"));env.insert("PYTHONUNBUFFERED","1")
            if self.worker.state()==QProcess.ProcessState.NotRunning:
                self.worker.setProcessEnvironment(env)
                self.worker.start(sys.executable,["-m","fruitfly.worker"])
            else:self.send_worker("enable")
            if self.overlay.state()==QProcess.ProcessState.NotRunning:
                # A 64x64 image with rectangular clips needs no 3D scene graph.
                # Scope this to our overlay; do not change the desktop's renderer.
                env.insert("QT_QUICK_BACKEND",self.renderer)
                env.insert("FRUITFLY_SOCKET",str(socket_path()))
                env.insert("FRUITFLY_ASSETS",str(ROOT/"assets"))
                self.overlay.setProcessEnvironment(env)
                self.overlay.start("quickshell",["--no-duplicate","-p",str(ROOT/"ui/shell.qml")])
            self.watchdog.start()
        else:
            self.send_worker("disable");self.watchdog.stop()
            self.last_frame={"visible":False};self.broadcast(self.last_frame)
            # Removing the layer surface allows the compositor to recover direct scanout.
            if self.overlay.state()!=QProcess.ProcessState.NotRunning:self.overlay.terminate()

    def fail(self,message):
        if self.closing:return
        self.set_enabled(False,"error");self.error=message;self.refresh_tray()
        # A hung worker cannot be trusted to honour disable.
        if self.worker.state()!=QProcess.ProcessState.NotRunning:
            self.worker.kill()

    def worker_finished(self,*_):
        self.worker_ready=False
        if self.enabled:self.fail("O cérebro encerrou inesperadamente")

    def overlay_finished(self,*_):
        self.viewers.clear()
        if self.enabled:self.fail("A sobreposição encerrou inesperadamente")

    def worker_stderr(self):
        data=bytes(self.worker.readAllStandardError())
        if data:sys.stderr.write(data.decode(errors="replace"))

    def read_worker(self):
        self.worker_buffer+=bytes(self.worker.readAllStandardOutput())
        if len(self.worker_buffer)>65536:self.fail("Resposta excessiva do cérebro");return
        while b"\n" in self.worker_buffer:
            line,self.worker_buffer=self.worker_buffer.split(b"\n",1)
            try:message=json.loads(line)
            except ValueError:self.fail("Resposta inválida do cérebro");return
            kind=message.get("type")
            if kind=="error":self.fail(message.get("error","Erro no cérebro"));return
            if self.enabled:self.watchdog.start()
            if kind=="frame" and self.enabled:
                self.last_frame=message;self.broadcast(message)
            elif kind in {"metrics","state"}:
                self.metrics.update({k:v for k,v in message.items() if k not in {"type","enabled"}})

    def broadcast(self,payload):
        data=(json.dumps(payload,separators=(",",":"))+"\n").encode()
        for client in tuple(self.viewers):
            # Never accumulate old frames when a renderer stops reading.
            if client.bytesToWrite()>4096:continue
            client.write(data);client.flush()

    def accept(self):
        while self.server.hasPendingConnections():
            client=self.server.nextPendingConnection();self.clients[client]=b""
            client.readyRead.connect(lambda c=client:self.read_client(c))
            client.disconnected.connect(lambda c=client:self.drop_client(c))

    def drop_client(self,client):
        self.viewers.discard(client);self.clients.pop(client,None)
        if isValid(client):client.deleteLater()

    def read_client(self,client):
        self.clients[client]+=bytes(client.readAll())
        if len(self.clients[client])>8192:client.abort();return
        while b"\n" in self.clients.get(client,b""):
            line,self.clients[client]=self.clients[client].split(b"\n",1)
            try:command=json.loads(line).get("command")
            except (ValueError,AttributeError):client.abort();return
            if command=="subscribe":
                self.viewers.add(client)
                client.write((json.dumps(self.last_frame)+"\n").encode());client.flush();continue
            if command=="rendered":
                self.metrics["image_ready"]=True
                continue
            if command=="enable":self.set_enabled(True,"control")
            elif command=="disable":self.set_enabled(False,"control")
            elif command=="quit":QTimer.singleShot(0,self.app.quit)
            elif command!="status":
                client.write(b'{"error":"unknown command"}\n');client.disconnectFromServer();return
            payload={"enabled":self.enabled,"error":self.error,"metrics":self.metrics,
                     "stage":"alpha: fuga/exploração; dez respostas ainda não concluídas"}
            client.write((json.dumps(payload,ensure_ascii=False)+"\n").encode());client.flush()
            client.disconnectFromServer()

    def shutdown(self):
        self.closing=True;self.watchdog.stop();self.tray.hide()
        self.send_worker("quit")
        for process in [self.worker,self.overlay]:
            if process.state()!=QProcess.ProcessState.NotRunning:
                if process is self.overlay:process.terminate()
                if not process.waitForFinished(1000):process.kill();process.waitForFinished(1000)
        self.server.close()
        signal.set_wakeup_fd(self.old_wakeup);self.notifier.setEnabled(False)
        os.close(self.sig_r);os.close(self.sig_w)


def run():
    try:
        print(json.dumps(request("status"),ensure_ascii=False));return 0
    except (OSError,RuntimeError):pass
    renderer=os.environ.get("FRUITFLY_RENDERER","software")
    if renderer not in {"software","rhi"}:
        print("FRUITFLY_RENDERER deve ser software ou rhi",file=sys.stderr);return 2
    # Only remove a stale socket after a failed connection in our private runtime directory.
    path=socket_path()
    if path.exists() and path.is_socket() and path.stat().st_uid==os.getuid():
        QLocalServer.removeServer(str(path))
    app=QApplication([sys.argv[0]])
    app.setApplicationName("FruitFly");app.setQuitOnLastWindowClosed(False)
    supervisor=Supervisor(app,renderer)
    if not QSystemTrayIcon.isSystemTrayAvailable():
        supervisor.error="Bandeja indisponível; controle por CLI";supervisor.refresh_tray()
    return app.exec()
