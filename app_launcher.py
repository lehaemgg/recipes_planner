import os
import sys
import subprocess
import webbrowser
import time
import socket
from threading import Thread

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def run_server(port):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodplanner.settings')
    
    # Get the directory where the exe is located
    if getattr(sys, 'frozen', False):
        app_dir = sys._MEIPASS
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(app_dir)
    
    # Run Django server
    subprocess.run([
        sys.executable, 'manage.py', 'runserver', 
        f'127.0.0.1:{port}', '--noreload'
    ], creationflags=subprocess.CREATE_NO_WINDOW)

if __name__ == '__main__':
    port = find_free_port()
    
    # Start server in background
    server_thread = Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    # Open browser
    webbrowser.open(f'http://127.0.0.1:{port}')
    
    # Keep the process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass