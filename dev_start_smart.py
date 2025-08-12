#!/usr/bin/env python3
"""
Iniciador de desarrollo con auto-reload inteligente
Excluye la carpeta tests/ para evitar reinicios innecesarios
"""
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import signal

class SmartReloadHandler(FileSystemEventHandler):
    """Handler que reinicia el servidor solo cuando es necesario"""
    
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_restart = 0
        self.restart_delay = 1  # 1 segundo de delay entre reinicios
        
    def should_restart(self, event_path):
        """Determina si un cambio debe causar reinicio"""
        
        # Excluir carpetas específicas
        exclude_patterns = [
            'tests/',
            '__pycache__/',
            '.git/',
            'logs/',
            'node_modules/',
            '.vscode/',
            'patches/'
        ]
        
        # Excluir tipos de archivos
        exclude_extensions = [
            '.pyc',
            '.pyo',
            '.log',
            '.tmp',
            '.swp',
            '.DS_Store'
        ]
        
        # Verificar patrones de exclusión
        for pattern in exclude_patterns:
            if pattern in event_path:
                return False
                
        # Verificar extensiones
        for ext in exclude_extensions:
            if event_path.endswith(ext):
                return False
        
        # Solo archivos Python y templates
        valid_extensions = ['.py', '.html', '.js', '.css', '.json', '.yaml', '.yml']
        return any(event_path.endswith(ext) for ext in valid_extensions)
    
    def on_modified(self, event):
        if not event.is_directory and self.should_restart(event.src_path):
            current_time = time.time()
            if current_time - self.last_restart > self.restart_delay:
                print(f"🔄 Reiniciando por cambio en: {event.src_path}")
                self.last_restart = current_time
                self.restart_callback()

class DevServer:
    """Servidor de desarrollo con auto-reload inteligente"""
    
    def __init__(self):
        self.process = None
        self.observer = None
        
    def start_flask(self):
        """Inicia el proceso de Flask"""
        if self.process:
            self.stop_flask()
            
        print("🚀 Iniciando servidor Flask...")
        
        # Ejecutar el archivo principal SIN debug mode
        env = os.environ.copy()
        env['FLASK_DEBUG'] = '0'  # Desactivar auto-reload de Flask
        
        self.process = subprocess.Popen(
            [sys.executable, 'dev_start_simple.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("✅ Servidor iniciado")
        
    def stop_flask(self):
        """Detiene el proceso de Flask"""
        if self.process:
            print("🛑 Deteniendo servidor...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            
    def setup_watcher(self):
        """Configura el observador de archivos"""
        event_handler = SmartReloadHandler(self.restart_server)
        
        self.observer = Observer()
        
        # Observar carpetas principales
        watch_paths = [
            'clientes/',
            'app.py',
            'gunicorn_patch.py',
            'dev_start.py'
        ]
        
        for path in watch_paths:
            if os.path.exists(path):
                self.observer.schedule(event_handler, path, recursive=True)
                print(f"👀 Observando: {path}")
        
        self.observer.start()
        print("✅ Observador de archivos iniciado (excluyendo tests/)")
        
    def restart_server(self):
        """Reinicia el servidor Flask"""
        self.stop_flask()
        time.sleep(0.5)  # Breve pausa
        self.start_flask()
        
    def run(self):
        """Ejecuta el servidor con auto-reload inteligente"""
        print("🧪 DEV SERVER CON AUTO-RELOAD INTELIGENTE")
        print("📁 Excluye: tests/, __pycache__/, logs/, .git/")
        print("=" * 50)
        
        try:
            self.start_flask()
            self.setup_watcher()
            
            # Mantener el script corriendo
            while True:
                time.sleep(1)
                if self.process and self.process.poll() is not None:
                    print("❌ Proceso Flask terminó inesperadamente")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Cerrando servidor...")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Limpia recursos"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.stop_flask()
        print("✅ Limpieza completada")

if __name__ == "__main__":
    server = DevServer()
    server.run()
