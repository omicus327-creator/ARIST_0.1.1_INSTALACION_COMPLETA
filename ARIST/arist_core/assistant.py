from __future__ import annotations
import re
from pathlib import Path
from . import config
from .ai import AIClient
from .coding import ProjectTools
from .database import Registry, digest_file
from . import file_manager
from .printers import build_printer
from .voice import Voice

GCODE={'.gcode','.gco','.gc'}
MODEL3D={'.stl','.3mf','.obj'}
class ARIST:
    def __init__(self,voice=None):
        self.voice=voice or Voice(); self.ai=AIClient(); self.tools=ProjectTools(); self.registry=Registry()
        self.printer=build_printer(config); self.active_job=None
    def say(self,s): self.voice.say(s)
    def files3d(self):
        items=[]
        for p in config.PRINT_FILES_DIR.rglob('*'):
            if p.is_file() and p.suffix.lower() in GCODE|MODEL3D: items.append(p)
        return items[:150]
    def list_print_files(self):
        fs=self.files3d()
        if not fs: self.say(f'No encontré archivos 3D ni G-code en {config.PRINT_FILES_DIR}.'); return
        lines=[]
        for p in fs:
            rec=self.registry.find_hash(digest_file(p))
            state=rec['status'] if rec else 'NO ENVIADO'
            lines.append(f'- {p.relative_to(config.PRINT_FILES_DIR)} [{p.suffix.lower()}] | {state}')
        self.say('Archivos encontrados:\n'+'\n'.join(lines))
    def print_history(self):
        rows=self.registry.latest()
        if not rows: self.say('Todavía no hay registros de impresión.'); return
        self.say('Historial de impresión:\n'+'\n'.join(f"#{r['id']} {r['filename']} | {r['status']} | {r['printer']} | {r['created_at']}" for r in rows))
    def find_file(self,name):
        raw=Path(name.strip().strip('"'))
        p=(raw if raw.is_absolute() else config.PRINT_FILES_DIR/raw).resolve()
        try: p.relative_to(config.PRINT_FILES_DIR)
        except ValueError: raise ValueError('El archivo debe estar dentro de la carpeta print_files.')
        if not p.is_file() or p.suffix.lower() not in GCODE|MODEL3D: raise ValueError('No encontré un archivo STL, 3MF, OBJ o G-code válido.')
        return p
    def slice_file(self,path):
        if path.suffix.lower() in GCODE: return path
        raise RuntimeError('Este archivo 3D necesita laminado. Configura CuraEngine o PrusaSlicer en ARIST_SLICER y ARIST_SLICER_PATH. El perfil de impresión debe configurarse para tu impresora antes de laminar.')
    def upload(self,name):
        if not self.printer: raise RuntimeError('No hay impresora configurada. Configura OctoPrint o Moonraker en .env.')
        p=self.slice_file(self.find_file(name))
        previous=self.registry.find_hash(digest_file(p))
        if previous and previous['status'] in {'CARGADO','IMPRIMIENDO','COMPLETADO'}:
            self.say(f'Este archivo ya figura en el historial como {previous["status"]}; no lo volveré a cargar automáticamente.')
            return
        if not self.confirm(f'¿Autorizas cargar {p.name} a {self.printer.name}? La carga no iniciará la impresión.') : self.say('Carga cancelada.'); return
        remote=self.printer.upload(p); self.registry.add(p,self.printer.name,remote,'CARGADO')
        self.say(f'{p.name} quedó cargado. No se inició la impresión.')
    def start_print(self,name):
        if not self.printer: raise RuntimeError('No hay impresora configurada.')
        p=self.find_file(name)
        if p.suffix.lower() not in GCODE: raise RuntimeError('Primero debes laminar el modelo 3D y generar G-code.')
        rec=self.registry.find_hash(digest_file(p))
        if not rec or rec['status']!='CARGADO': raise RuntimeError('El G-code no aparece cargado en el registro. Usa: carga archivo NOMBRE.gcode')
        if not self.confirm(f'Confirma que la impresora está preparada. ¿Iniciar {p.name}?'): self.say('Inicio cancelado.'); return
        self.printer.start(rec['remote_path']); self.registry.update(rec['id'],'IMPRIMIENDO'); self.active_job=rec['id']; self.say('Orden de inicio enviada.')
    def status(self):
        if not self.printer: raise RuntimeError('No hay impresora configurada.')
        data=self.printer.status(); self.say('Respuesta de estado de impresora:\n'+str(data)[:3500])
    def confirm(self,prompt):
        self.say(prompt+' Responde sí o no.')
        try: ans=self.voice.listen(timeout=8,limit=6).lower()
        except Exception: ans=input('Confirmación (sí/no): ').strip().lower()
        return ans in {'si','sí','si confirmar','sí confirmar','confirmar','adelante'}
    def handle(self,cmd):
        c=cmd.strip(); low=c.lower()
        if low in {'salir','terminar','cerrar arist'}: return False
        try:
            if low in {'ayuda','comandos'}: self.say(self.help()); return True
            if low in {'unidades','lista unidades'}:
                devices=file_manager.get_devices()
                self.say('Unidades disponibles: '+(', '.join(devices) if devices else 'no se detectaron unidades.')); return True
            if low in {'lista directorios','directorios'}:
                directories=file_manager.get_directories()
                self.say('Directorios de ARIST (máximo 200; se omiten .venv y modelos):\n'+'\n'.join(f'- {p.relative_to(file_manager.BASE_DIR)}' for p in directories)); return True
            m=re.match(r'^crea directorio\s+(.+)$',c,re.I)
            if m:
                path=file_manager.create_directory(m.group(1)); self.say(f'Directorio creado: {path.relative_to(file_manager.BASE_DIR)}'); return True
            m=re.match(r'^elimina directorio\s+(.+)$',c,re.I)
            if m:
                target=file_manager.get_safe_path(m.group(1))
                if not self.confirm(f'¿Confirmas eliminar el directorio vacío {target.relative_to(file_manager.BASE_DIR)}?'):
                    self.say('Eliminación cancelada.'); return True
                path=file_manager.delete_directory(m.group(1)); self.say(f'Directorio vacío eliminado: {path.relative_to(file_manager.BASE_DIR)}'); return True
            m=re.match(r'^cambia permisos\s+(.+?)\s+(r|w|[0-7]{3,4})$',c,re.I)
            if m:
                path=file_manager.set_permissions(m.group(1),m.group(2)); self.say(f'Permisos actualizados: {path.relative_to(file_manager.BASE_DIR)}'); return True
            if low in {'lista archivos 3d','lista archivos','lista gcode','archivos para imprimir'}: self.list_print_files(); return True
            if low in {'historial','enviados','archivos enviados'}: self.print_history(); return True
            if low in {'estado impresora','estado de impresion','estado de impresión'}: self.status(); return True
            m=re.match(r'^(?:carga|sube|envia) archivo\s+(.+)$',c,re.I)
            if m: self.upload(m.group(1)); return True
            m=re.match(r'^(?:inicia|comienza) impresion\s+(.+)$',c,re.I)
            if m: self.start_print(m.group(1)); return True
            m=re.match(r'^(?:revisa|analiza) archivo\s+(.+)$',c,re.I)
            if m:
                p,src=self.tools.read(m.group(1)); self.say(self.ai.chat(f'Analiza este archivo {p.name}. Señala errores, riesgos y mejoras; no apliques cambios.\n\n{src}')); return True
            m=re.match(r'^comprueba sintaxis\s+(.+)$',c,re.I)
            if m: self.say(self.tools.check_python(m.group(1))); return True
            if low in {'archivos proyecto','lista proyecto'}: self.say('\n'.join(self.tools.scan()) or 'Workspace vacío.'); return True
            if low == 'revisa proyecto':
                files=self.tools.scan(); chunks=[]
                for rel in files:
                    try:
                        p,src=self.tools.read(rel, max_chars=5000); chunks.append(f'\n### {rel}\n{src}')
                    except Exception: pass
                    if sum(map(len,chunks))>18000: break
                if not chunks: self.say('No hay archivos de texto compatibles en workspace.'); return True
                self.say(self.ai.chat('Analiza la estructura y los archivos de este proyecto. Identifica arquitectura, errores potenciales, dependencias faltantes y mejoras. No propongas cambios destructivos.\n'+''.join(chunks))); return True
            m=re.match(r'^crea archivo\s+([^|]+)\|\s*(.+)$',c,re.I)
            if m:
                target=m.group(1).strip(); task=m.group(2).strip()
                generated=self.ai.chat('Genera el contenido completo del archivo solicitado. Devuelve únicamente el contenido, preferiblemente dentro de un solo bloque de código sin explicación.\nArchivo: '+target+'\nObjetivo: '+task)
                fence=re.search(r'```(?:[a-zA-Z0-9_+.-]+)?\s*\n(.*?)```',generated,re.S)
                content=fence.group(1) if fence else generated
                if self.confirm(f'Voy a crear o reemplazar {target} dentro de workspace. ¿Autorizas guardar el archivo?'):
                    saved=self.tools.write_with_backup(target,content); self.say(f'Archivo guardado: {saved.relative_to(self.tools.root)}. No se ejecutó.');
                else: self.say('No se guardaron cambios.')
                return True
            if low.startswith('programa ') or low.startswith('corrige ') or low.startswith('explica ') or low.startswith('analiza '):
                self.say(self.ai.chat(c)); return True
            self.say(self.ai.chat(c)); return True
        except Exception as e: self.say(f'No pude completar la operación: {e}'); return True
    @staticmethod
    def help():
        return '''COMANDOS ARIST\nPROGRAMACIÓN: programa <tarea>; corrige <error>; revisa archivo <ruta>; revisa proyecto; crea archivo <ruta> | <descripción>; comprueba sintaxis <archivo.py>; archivos proyecto.\nARCHIVOS: unidades; lista directorios; crea directorio <ruta>; elimina directorio <ruta>; cambia permisos <ruta> <r|w>. Las rutas quedan limitadas a la carpeta ARIST; solo se eliminan directorios vacíos. En Windows, r=solo lectura y w=escritura.\nIMPRESIÓN: lista archivos 3d; carga archivo <nombre.gcode>; inicia impresion <nombre.gcode>; estado impresora; historial.\nGENERAL: ayuda; salir.\nLos archivos de trabajo van en workspace y los modelos 3D/G-code en print_files. Las cargas e inicios requieren confirmación.'''
