from __future__ import annotations
import ast, shutil, subprocess, sys
from pathlib import Path
from . import config
from .database import now

ALLOWED_TEXT={'.py','.pyw','.c','.h','.cpp','.hpp','.ino','.java','.js','.ts','.html','.css','.json','.yaml','.yml','.toml','.md','.txt','.ps1','.sql'}

def inside(path: Path, root: Path) -> bool:
    try: path.resolve().relative_to(root.resolve()); return True
    except ValueError: return False

class ProjectTools:
    def __init__(self, root=config.WORKSPACE): self.root=root.resolve(); self.root.mkdir(parents=True,exist_ok=True)
    def resolve(self, raw):
        p=Path(raw.strip().strip('"')).expanduser()
        if not p.is_absolute(): p=self.root/p
        p=p.resolve()
        if not inside(p,self.root): raise ValueError('Por seguridad, la ruta debe estar dentro del workspace de ARIST.')
        return p
    def scan(self):
        found=[]
        for p in self.root.rglob('*'):
            if p.is_file() and not any(x in {'.git','.venv','venv','__pycache__','node_modules','backups'} for x in p.parts):
                found.append(p.relative_to(self.root).as_posix())
                if len(found)>=250: break
        return found
    def read(self, raw, max_chars=30000):
        p=self.resolve(raw)
        if not p.is_file() or p.suffix.lower() not in ALLOWED_TEXT: raise ValueError('Archivo inexistente o extensión no habilitada para lectura.')
        return p, p.read_text(encoding='utf-8',errors='replace')[:max_chars]
    def write_with_backup(self, raw, content):
        p=self.resolve(raw)
        if p.suffix.lower() not in ALLOWED_TEXT: raise ValueError('Extensión no habilitada para escritura.')
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():
            backup=config.BACKUP_DIR/(p.name+'.'+now().replace(':','-')+'.bak')
            shutil.copy2(p,backup)
        p.write_text(content,encoding='utf-8')
        return p
    def check_python(self, raw):
        p, source=self.read(raw)
        if p.suffix.lower() not in {'.py','.pyw'}: raise ValueError('La comprobación AST solo aplica a Python.')
        try: ast.parse(source); return 'Sintaxis Python correcta (AST). Esto no demuestra que el programa funcione.'
        except SyntaxError as e: return f'Error de sintaxis: línea {e.lineno}, columna {e.offset}: {e.msg}'
    def run_tests(self, relative='.'):
        target=self.resolve(relative)
        if not target.exists(): raise ValueError('Ruta de pruebas inexistente.')
        return subprocess.run([sys.executable,'-m','pytest','-q',str(target)],cwd=self.root,capture_output=True,text=True,timeout=120)
