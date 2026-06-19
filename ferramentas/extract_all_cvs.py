import os
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

# Tenta importar pypdf, se nao, instala
try:
    import pypdf
except ImportError:
    print("pypdf não está instalado. Tentando instalar via pip3...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf

def get_docx_text(path):
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
        return f"Erro ao ler DOCX {path}: {str(e)}"

def get_pdf_text(path):
    try:
        reader = pypdf.PdfReader(path)
        text_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_pages.append(f"--- Página {i+1} ---\n{page_text}")
        return "\n\n".join(text_pages)
    except Exception as e:
        return f"Erro ao ler PDF {path}: {str(e)}"

def main():
    workspace = "/Users/eltongoncalves/Desenv/minerador-de-vagas"
    curriculos_dir = os.path.join(workspace, "curriculos")
    output_path = os.path.join(workspace, "analises_e_perfis/historico_e_analise/TEXTO_COMPLETO_CURRICULOS.md")
    
    # Criar pasta de destino se nao existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Texto Extraído de Todos os Currículos Históricos (PDF e DOCX)\n\n")
        
        # Percorrer todas as subpastas em curriculos/
        for root, dirs, files in os.walk(curriculos_dir):
            for file in sorted(files):
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, workspace)
                
                if file.lower().endswith('.pdf'):
                    print(f"Lendo PDF: {rel_path}")
                    f.write(f"## Arquivo: {rel_path}\n\n")
                    text = get_pdf_text(file_path)
                    f.write(text + "\n\n---\n\n")
                    
                elif file.lower().endswith('.docx'):
                    print(f"Lendo DOCX: {rel_path}")
                    f.write(f"## Arquivo: {rel_path}\n\n")
                    text = get_docx_text(file_path)
                    f.write(text + "\n\n---\n\n")
                    
    print(f"Extração concluída! Arquivo salvo em: {output_path}")

if __name__ == "__main__":
    main()
