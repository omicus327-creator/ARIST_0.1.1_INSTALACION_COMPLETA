import requests
from urllib.parse import quote
class OctoPrint:
    name='OctoPrint'
    def __init__(self,url,key):
        if not url or not key: raise ValueError('Falta URL o API key de OctoPrint.')
        self.url=url.rstrip('/'); self.s=requests.Session(); self.s.headers['X-Api-Key']=key
    def req(self,method,path,**kw):
        r=self.s.request(method,self.url+path,timeout=30,**kw); r.raise_for_status(); return r
    def status(self): return self.req('GET','/api/job').json()
    def upload(self,path):
        with path.open('rb') as f:
            d=self.req('POST','/api/files/local',files={'file':(path.name,f,'application/octet-stream')},data={'select':'false','print':'false'}).json()
        return d.get('files',{}).get('local',{}).get('path',path.name)
    def start(self,remote):
        self.req('POST','/api/files/local/'+quote(remote,safe='/'),json={'command':'select'})
        self.req('POST','/api/job',json={'command':'start'})
    def cancel(self): self.req('POST','/api/job',json={'command':'cancel'})
