"""Installed Tesseract C API, one handle per source/task; no downloaded deps.

Signatures verified against installed primary capi.h. Clear image/adaptive
state between each read; preserve model/library provenance with raw outputs.
"""
import ctypes as C,ctypes.util,hashlib
from pathlib import Path
class NativeTesseract:
    def __init__(self):
        candidates=['/opt/homebrew/lib/libtesseract.dylib',ctypes.util.find_library('tesseract'),'libtesseract.so.5'];errors=[]
        for name in candidates:
            if not name:continue
            try:self.lib=C.CDLL(name);self.library=name;break
            except OSError as e:errors.append(str(e))
        else:raise RuntimeError(errors)
        lib=self.lib;P=C.c_void_p;I=C.c_int;S=C.c_char_p
        signatures={'TessVersion':([],S),'TessBaseAPICreate':([],P),'TessBaseAPIInit3':([P,S,S],I),'TessBaseAPISetVariable':([P,S,S],I),'TessBaseAPISetPageSegMode':([P,I],None),'TessBaseAPISetImage':([P,C.POINTER(C.c_ubyte),I,I,I,I],None),'TessBaseAPIRecognize':([P,P],I),'TessBaseAPIGetUTF8Text':([P],P),'TessDeleteText':([P],None),'TessBaseAPIClearAdaptiveClassifier':([P],None),'TessBaseAPIClear':([P],None),'TessBaseAPIEnd':([P],None),'TessBaseAPIDelete':([P],None),'TessBaseAPIGetDatapath':([P],S)}
        for name,(args,result) in signatures.items():getattr(lib,name).argtypes=args;getattr(lib,name).restype=result
        self.handle=lib.TessBaseAPICreate();assert self.handle;assert lib.TessBaseAPIInit3(self.handle,None,b'eng')==0;assert lib.TessBaseAPISetVariable(self.handle,b'tessedit_char_whitelist',b'0123456789,.-');lib.TessBaseAPISetVariable(self.handle,b'debug_file',b'/dev/null')
        datapath=Path(lib.TessBaseAPIGetDatapath(self.handle).decode());model=datapath/'eng.traineddata';self.metadata=dict(engine='Installed Tesseract C API; no cross-cell adaptive state',version=lib.TessVersion().decode(),library=self.library,model_path=str(model),model_bytes=model.stat().st_size,model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),psm=[6,7],language='eng',character_whitelist='0123456789,.-',qualification='Same recognizer/model, two segmentation modes are not independent source witnesses. Raw original/whole-page engine and direct image reviews remain separate.')
    def read(self,image,psm):
        im=image.convert('L');data=im.tobytes();buffer=(C.c_ubyte*len(data)).from_buffer_copy(data);lib=self.lib;h=self.handle;lib.TessBaseAPIClearAdaptiveClassifier(h);lib.TessBaseAPISetPageSegMode(h,psm);lib.TessBaseAPISetImage(h,buffer,im.width,im.height,1,im.width);assert lib.TessBaseAPIRecognize(h,None)==0;p=lib.TessBaseAPIGetUTF8Text(h)
        try:return C.string_at(p).decode() if p else ''
        finally:
            if p:lib.TessDeleteText(p)
            lib.TessBaseAPIClear(h)
    def close(self):
        if self.handle:self.lib.TessBaseAPIEnd(self.handle);self.lib.TessBaseAPIDelete(self.handle);self.handle=None
    def __del__(self):
        if getattr(self,'handle',None):self.close()
