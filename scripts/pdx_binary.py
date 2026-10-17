"""Small ordered Clausewitz binary tree reader/writer for our own portrait rigs.

Format reference: ross-g/io_pdx_mesh pdx_data.py format documentation.
This module is an independent implementation; it contains no game asset data.
"""
from dataclasses import dataclass,field
from pathlib import Path
import struct

@dataclass
class Node:
    name:str
    props:dict=field(default_factory=dict)
    children:list=field(default_factory=list)
    def add(self,name,**props):
        child=Node(name,props);self.children.append(child);return child

def read(path):
    data=Path(path).read_bytes()
    if data[:4]!=b'@@b@':raise ValueError('Not binary PDX')
    root=Node('File');stack=[root];pos=4
    while pos<len(data):
        if data[pos]==91:
            depth=0
            while data[pos]==91:depth+=1;pos+=1
            end=data.index(b'\0',pos);name=data[pos:end].decode('latin1');pos=end+1
            stack=stack[:depth]
            node=Node(name);stack[-1].children.append(node);stack.append(node)
        elif data[pos]==33:
            length=data[pos+1];pos+=2
            name=data[pos:pos+length].decode('latin1');pos+=length
            kind=chr(data[pos]);count=struct.unpack_from('<i',data,pos+1)[0];pos+=5
            if kind in ['i','f']:
                value=list(struct.unpack_from('<'+kind*count,data,pos));pos+=count*4
            elif kind=='s':
                length=struct.unpack_from('<i',data,pos)[0];pos+=4
                value=[data[pos:pos+length].rstrip(b'\0').decode('latin1')];pos+=length
            else:raise ValueError('Unsupported property type '+kind)
            stack[-1].props[name]=value
        else:raise ValueError('Unexpected PDX byte at '+str(pos))
    return root

def write(path,root):
    result=bytearray(b'@@b@')
    def properties(props):
        for name,values in props.items():
            key=name.encode('latin1');result.extend(b'!'+bytes([len(key)])+key)
            if isinstance(values,str):values=[values]
            if not values:raise ValueError('Empty property '+name)
            if isinstance(values[0],str):
                raw=values[0].encode('latin1')+b'\0'
                result.extend(b's'+struct.pack('<ii',1,len(raw))+raw)
            else:
                kind='i' if all(isinstance(v,int) for v in values) else 'f'
                result.extend(kind.encode()+struct.pack('<i',len(values))+struct.pack('<'+kind*len(values),*values))
    def visit(node,depth):
        result.extend(b'['*depth+node.name.encode('latin1')+b'\0');properties(node.props)
        for child in node.children:visit(child,depth+1)
    properties(root.props)
    for node in root.children:visit(node,1)
    Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_bytes(result)

def summarize(node):
    return {'name':node.name,'props':{k:{'count':len(v),'first':v[:12]} for k,v in node.props.items()},'children':[summarize(n) for n in node.children]}
