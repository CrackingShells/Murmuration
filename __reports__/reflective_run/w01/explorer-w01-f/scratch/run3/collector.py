# minimal OTLP/HTTP receiver: appends each POST (path, content-type, body) to otlp.jsonl; exits after 150 s
import http.server, json, sys, time, threading
OUT=sys.argv[1]; PORT=int(sys.argv[2])
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n=int(self.headers.get("content-length",0)); b=self.rfile.read(n)
        try: body=b.decode()
        except Exception: body=repr(b[:200])
        open(OUT,"a").write(json.dumps({"t":time.time(),"path":self.path,"ct":self.headers.get("content-type"),"enc":self.headers.get("content-encoding"),"body":body})+"\n")
        self.send_response(200); self.send_header("content-type","application/json"); self.end_headers(); self.wfile.write(b"{}")
    def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(("127.0.0.1",PORT),H)
threading.Timer(150,srv.shutdown).start()
srv.serve_forever()
