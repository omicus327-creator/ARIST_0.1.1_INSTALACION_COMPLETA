import argparse
from .assistant import ARIST
from .voice import Voice
from . import config

def main():
    p=argparse.ArgumentParser(description='ARIST - asistente de programación e impresión 3D')
    p.add_argument('--voz',action='store_true',help='Escucha continua mediante micrófono')
    p.add_argument('--voz-manual',action='store_true',help='Pulsa Enter para activar el micrófono en cada instrucción')
    p.add_argument('--activar-voz',action='store_true',help='Espera la palabra clave ARIST (requiere Vosk)')
    p.add_argument('--microfono',type=int,default=None)
    a=p.parse_args(); voice=Voice(a.microfono); app=ARIST(voice)
    print('\nARIST | Asistente de programación e impresión 3D')
    print(f'Workspace: {config.WORKSPACE}')
    print(f'IA: {config.AI_PROVIDER} | Modelo local: {config.OLLAMA_MODEL}')
    print('Escribe ayuda para ver comandos.\n')
    if a.activar_voz:
        voice.wake_loop(lambda text: app.handle(text),config.WAKE_WORD,config.VOSK_MODEL_PATH); return 0
    while True:
        try:
            if a.voz or a.voz_manual:
                if a.voz_manual: input('Pulsa Enter para hablar (Ctrl+C para salir)... ')
                try: cmd=voice.listen()
                except Exception as e: voice.say(f'Error de voz: {e}'); continue
            else: cmd=input('Tú: ')
            if not app.handle(cmd): break
        except (KeyboardInterrupt,EOFError): print('\nARIST finalizado.'); break
    return 0
