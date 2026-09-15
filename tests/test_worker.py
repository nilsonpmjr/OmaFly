"""A fake compositor exercises the actual worker's stop/resume semantics."""
import json
import os
from pathlib import Path
import selectors
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from fruitfly.core import ROOT


class WorkerTests(unittest.TestCase):
    def test_disabled_worker_never_queries_or_ticks(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"hypr/test";path.mkdir(parents=True)
            server=socket.socket(socket.AF_UNIX);server.bind(str(path/".socket.sock"));server.listen()
            server.settimeout(.05);queries=[];stop=threading.Event()
            def serve():
                while not stop.is_set():
                    try:conn,_=server.accept()
                    except TimeoutError:continue
                    with conn:
                        command=conn.recv(1024).decode();queries.append(command)
                        payload=[{"name":"fake","x":-1200,"y":0,"width":1200,"height":800,
                                  "scale":1,"focused":True}] if command=="j/monitors" else {"x":-100,"y":100}
                        conn.sendall(json.dumps(payload).encode())
            thread=threading.Thread(target=serve);thread.start()
            env=dict(os.environ,PYTHONPATH=str(ROOT/"src"),XDG_RUNTIME_DIR=directory,HYPRLAND_INSTANCE_SIGNATURE="test")
            process=subprocess.Popen([sys.executable,"-m","fruitfly.worker"],stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
            sel=selectors.DefaultSelector();sel.register(process.stdout,selectors.EVENT_READ)
            buffer=b""
            def receive(kind,timeout=3):
                nonlocal buffer
                deadline=time.monotonic()+timeout
                while time.monotonic()<deadline:
                    if b"\n" not in buffer:
                        if not sel.select(max(0,deadline-time.monotonic())):break
                        data=os.read(process.stdout.fileno(),4096)
                        if not data:break
                        buffer+=data
                    while b"\n" in buffer:
                        line,buffer=buffer.split(b"\n",1);message=json.loads(line)
                        if message.get("type")==kind:return message
                raise AssertionError(f"No {kind} from worker")
            def send(command):
                process.stdin.write((json.dumps({"command":command})+"\n").encode());process.stdin.flush()
            try:
                time.sleep(.12);self.assertEqual(queries,[])
                send("enable");frame=receive("frame")
                self.assertEqual(frame["monitor"],"fake");self.assertLess(frame["x"],0)
                send("disable");state=receive("state");count=len(queries)
                time.sleep(.2);self.assertEqual(len(queries),count)
                send("disable");self.assertEqual(receive("state")["ticks"],state["ticks"])
                send("enable");self.assertTrue(receive("frame")["visible"])
                send("quit");self.assertEqual(process.wait(timeout=2),0)
            finally:
                if process.poll() is None:process.kill();process.wait()
                process.stdin.close();process.stdout.close();process.stderr.close();sel.close()
                stop.set();thread.join(timeout=1);server.close()


if __name__=="__main__":unittest.main()
