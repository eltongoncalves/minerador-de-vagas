import os
import re

COMPANIES = [
    {"key": "tinnova", "names": ["tinnova"]},
    {"key": "200dev", "names": ["200dev"]},
    {"key": "accenture", "names": ["accenture"]},
    {"key": "g4f", "names": ["g4f"]},
    {"key": "chaintech", "names": ["chaintech"]},
    {"key": "evah", "names": ["evah"]},
    {"key": "south system", "names": ["south system", "southsystem"]},
    {"key": "conquest one", "names": ["conquest one", "conquestone"]},
    {"key": "tecban", "names": ["tecban", "avantti", "tec ban"]},
    {"key": "minsait", "names": ["minsait", "indra"]},
    {"key": "panvel", "names": ["panvel", "dimed"]},
    {"key": "basis", "names": ["basis"]},
    {"key": "foursys", "names": ["foursys"]},
    {"key": "ntt data", "names": ["ntt data", "nttdata", "everis"]},
    {"key": "cosanpa", "names": ["cosanpa"]},
    {"key": "i9amazon", "names": ["i9amazon", "i9 amazon"]},
    {"key": "do bem contabilidade", "names": ["do bem", "dobem"]},
    {"key": "biotec", "names": ["biotec", "biotec-amazônia", "biotec-amazonia"]},
    {"key": "solus", "names": ["solus"]},
    {"key": "vibe", "names": ["vibe", "banpará", "banpara"]},
    {"key": "img seguros", "names": ["img seguros", "img seguradora", "img corretora"]},
    {"key": "ufra", "names": ["ufra", "parfor"]},
    {"key": "bellivery", "names": ["bellivery"]},
    {"key": "connect informatica", "names": ["connect"]},
    {"key": "comdac", "names": ["comdac"]}
]

# Patterns that indicate a new section or next experience
NEXT_EXP_PATTERNS = [
    r'^\s*-\s+(?:[0-9]{2}/[0-9]{4}|[0-9]{4})\b',
    r'^\s*##\s+',
    r'^\s*###\s+',
    r'^\s*\[[0-9]{4}\b',
    r'^\s*(?:Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)/[0-9]{4}\b',
    r'^\s*Formação\s+Acadêmica\b',
    r'^\s*Competências\b',
    r'^\s*Diferenciais\b'
]

def clean_text(text):
    # Remove excessive blank lines
    lines = [line.strip() for line in text.split('\n')]
    non_empty = []
    for line in lines:
        if line:
            non_empty.append(line)
        elif non_empty and non_empty[-1] != "":
            non_empty.append("")
    # Strip leading/trailing empty lines
    while non_empty and non_empty[0] == "":
        non_empty.pop(0)
    while non_empty and non_empty[-1] == "":
        non_empty.pop()
    return "\n".join(non_empty)

def extract_experience_block(lines, start_idx, file_name):
    block_lines = []
    # Include the match line (which usually contains the company name and date)
    block_lines.append(lines[start_idx])
    
    for i in range(start_idx + 1, min(start_idx + 40, len(lines))):
        line = lines[i]
        
        # Check if line indicates another experience or section
        is_next = False
        for pattern in NEXT_EXP_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                is_next = True
                break
                
        # Also check if it mentions another company in a header-like format
        for comp in COMPANIES:
            for name in comp["names"]:
                if name in line.lower() and (line.strip().startswith('-') or line.strip().startswith('##') or line.strip().startswith('###') or line.strip().startswith('[')):
                    is_next = True
                    break
            if is_next:
                break
                
        if is_next:
            break
            
        block_lines.append(line)
        
    return "\n".join(block_lines)

def main():
    workspace = "/Users/eltongoncalves/Desenv/minerador-de-vagas"
    cv_text_file = os.path.join(workspace, "analises_e_perfis/historico_e_analise/TEXTO_COMPLETO_CURRICULOS.md")
    output_file = os.path.join(workspace, "curriculos/2026/timeline_experiencias_detalhada.md")
    
    if not os.path.exists(cv_text_file):
        print(f"Erro: {cv_text_file} não encontrado.")
        return
        
    with open(cv_text_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split file by "## Arquivo: "
    sections = content.split("## Arquivo: ")
    file_data = {}
    
    for section in sections:
        if not section.strip():
            continue
        parts = section.split("\n", 1)
        if len(parts) < 2:
            continue
        file_path = parts[0].strip()
        text = parts[1]
        file_data[file_path] = text
        
    # We will also read the reference markdown curriculums in curriculos/2026/ directly if they are not in the file
    ref_dir = os.path.join(workspace, "curriculos/2026")
    for file in os.listdir(ref_dir):
        if file.endswith('.md') and file != 'timeline_experiencias_detalhada.md':
            file_path = os.path.join(ref_dir, file)
            rel_path = os.path.relpath(file_path, workspace)
            if rel_path not in file_data:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_data[rel_path] = f.read()
                except:
                    pass
                    
    # Initialize compilation dictionary: company_key -> list of {file: rel_path, text: extracted_text}
    compilation = {comp["key"]: [] for comp in COMPANIES}
    
    for rel_path, text in file_data.items():
        lines = text.split('\n')
        
        for comp in COMPANIES:
            key = comp["key"]
            names = comp["names"]
            
            # Find the best match line index
            best_idx = -1
            for idx, line in enumerate(lines):
                # Search for any of the names in the line
                match_found = False
                for name in names:
                    # Look for names as whole words or in bold/headers
                    if re.search(r'\b' + re.escape(name) + r'\b', line.lower()) or f"**{name}" in line.lower() or f"#{name}" in line.lower():
                        # Verify it's not a skill mention like "Java (Spring)" or similar unless it's in a path
                        # Resumes usually list company in headers or bullet points
                        if line.strip().startswith('-') or line.strip().startswith('##') or line.strip().startswith('###') or line.strip().startswith('[') or "**" in line or "Cargo" in line or "Período" in line:
                            match_found = True
                            break
                if match_found:
                    best_idx = idx
                    break
                    
            if best_idx != -1:
                extracted = extract_experience_block(lines, best_idx, rel_path)
                cleaned = clean_text(extracted)
                if len(cleaned.strip()) > 30: # ignore trivial matches
                    compilation[key].append({
                        "file": rel_path,
                        "text": cleaned
                    })
                    
    # Write compilation to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 📑 Linha do Tempo Profissional Detalhada com Referências de Currículos\n\n")
        f.write("Este documento compila as descrições de atividades de cada empresa em que você trabalhou, extraídas diretamente de cada um dos seus currículos históricos (PDF, DOCX e MD). O objetivo é registrar todas as variações de textos e referências de cada currículo para evitar perda de dados.\n\n")
        f.write("---\n\n")
        
        # Order of presentation: chronologically descending (same as timeline_experiencias.md)
        ordered_keys = [
            "tinnova", "200dev", "accenture", "g4f", "chaintech", "evah",
            "south system", "conquest one", "tecban", "minsait", "panvel",
            "basis", "foursys", "ntt data", "cosanpa", "i9amazon",
            "do bem contabilidade", "biotec", "solus", "vibe", "img seguros",
            "ufra", "bellivery", "connect informatica", "comdac"
        ]
        
        for key in ordered_keys:
            comp_name = key.upper()
            f.write(f"## 🏢 {comp_name}\n\n")
            
            records = compilation.get(key, [])
            if not records:
                f.write("*Nenhuma referência textual explícita encontrada nos currículos históricos analisados para esta empresa.*\n\n")
            else:
                for record in records:
                    file_name = record["file"]
                    text_block = record["text"]
                    
                    # Highlight the file name beautifully
                    f.write(f"### 📄 No arquivo: `[{file_name}](file:///{os.path.join(workspace, file_name)})`\n\n")
                    f.write("```markdown\n")
                    f.write(text_block + "\n")
                    f.write("```\n\n")
            f.write("---\n\n")
            
    print(f"Linha do tempo detalhada gerada em: {output_file}")

if __name__ == "__main__":
    main()
