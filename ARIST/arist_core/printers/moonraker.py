import requests
class Moonraker:
    name='Moonraker'
    def __init__(self,url,key=''):
        if not url: raise ValueError('Falta ARIST_MOONRAKER_URL.')
        self.url=url.rstrip('/'); self.s=requests.Session()
        if key: self.s.headers['X-Api-Key']=key
    def req(self,method,path,**kw):
        r=self.s.request(method,self.url+path,timeout=30,**kw); r.raise_for_status(); return r.json()
    def status(self): return self.req('GET','/printer/objects/query?print_stats&virtual_sdcard&toolhead')
    def upload(self,path):
        with path.open('rb') as f:
            d=self.req('POST','/server/files/upload',files={'file':(path.name,f,'application/octet-stream')},data={'root':'gcodes'})
        return d.get('item',{}).get('path',path.name)
    def start(self,remote): self.req('POST','/printer/print/start',json={'filename':remote})
    def cancel(self): self.req('POST','/printer/print/cancel')
