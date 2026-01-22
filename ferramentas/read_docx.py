import zipfile
import xml.etree.ElementTree as ET
import os

def get_docx_text(path):
    """Extrai texto de um arquivo .docx sem bibliotecas externas"""
    try:
        document = zipfile.ZipFile(path)
        xml_content = document.read('word/document.xml')
        document.close()
        tree = ET.fromstring(xml_content)
        
        paragraphs = []
        for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            texts = [node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
            if texts:
                paragraphs.append("".join(texts))
        
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Erro ao ler {path}: {str(e)}"

files = [
    'curriculos_elton/TEXTO ELTON  -  VERSÃO FINAL.docx',
    'curriculos_elton/TEXTO ELTON  -  VERSÃO ATUALIZADA.docx',
    'curriculos_elton/SISTEMAS DE INFORMAÇÃO TEXTO ELTON.docx'
]

output_path = 'EXTRACAO_TEXTO_CURRICULOS.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# Extração de Texto dos Currículos DOCX\n\n")
    for file_path in files:
        full_path = f"/Users/eltongoncalves/Source/minerador-de-vagas/{file_path}"
        if os.path.exists(full_path):
            f.write(f"## Arquivo: {file_path}\n\n")
            text = get_docx_text(full_path)
            f.write(text + "\n\n---\n\n")

print(f"Texto extraído para {output_path}")
