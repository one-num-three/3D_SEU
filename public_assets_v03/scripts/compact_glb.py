"""MIT. Remove redundant mesh-datablock labels only; node names, IDs and all binary geometry unchanged."""
from pathlib import Path
import json,struct,hashlib,sys

def compact(path):
 p=Path(path);raw=p.read_bytes();n,kind=struct.unpack_from('<II',raw,12);assert kind==0x4E4F534A
 doc=json.loads(raw[20:20+n]);binary_chunks=raw[20+n:]
 removed=sum('name'in m for m in doc.get('meshes',[]))
 for m in doc.get('meshes',[]):m.pop('name',None)
 data=json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode();data+=b' '*((-len(data))%4)
 result=struct.pack('<4sII',b'glTF',2,20+len(data)+len(binary_chunks))+struct.pack('<II',len(data),0x4E4F534A)+data+binary_chunks
 assert result[20+len(data):]==binary_chunks
 p.write_bytes(result)
 return {'bytes_before':len(raw),'bytes_after':len(result),'removed_redundant_mesh_labels':removed,'node_names_ids_and_binary_geometry_unchanged':True,'binary_chunks_sha256':hashlib.sha256(binary_chunks).hexdigest()}
if __name__=='__main__':print(json.dumps(compact(sys.argv[1]),indent=2))
