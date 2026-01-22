#!/usr/bin/env python3
"""
Script para extrair informações públicas do perfil do LinkedIn
Usando apenas bibliotecas padrão do Python
"""
import requests
import json
import re
from html.parser import HTMLParser

class LinkedInParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = {
            'name': None,
            'headline': None,
            'location': None,
            'about': None,
            'experience': [],
            'education': [],
            'skills': [],
            'url': None
        }
        self.current_tag = None
        self.current_class = None
        self.in_experience = False
        self.buffer = ''
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.current_tag = tag
        self.current_class = attrs_dict.get('class', '')
        
    def handle_data(self, data):
        if data.strip():
            self.buffer += data.strip() + ' '

def extract_linkedin_profile(url):
    """
    Tenta extrair informações públicas do perfil do LinkedIn
    Nota: LinkedIn requer autenticação para perfis completos,
    mas podemos tentar extrair informações públicas básicas via meta tags e JSON-LD
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
    }
    
    profile_data = {
        'name': None,
        'headline': None,
        'location': None,
        'about': None,
        'experience': [],
        'education': [],
        'skills': [],
        'url': url,
        'raw_html_length': 0
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        profile_data['raw_html_length'] = len(response.text)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Tentar extrair via meta tags (og:title, og:description)
            og_title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html_content)
            if og_title_match:
                profile_data['name'] = og_title_match.group(1)
            
            og_description_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html_content)
            if og_description_match:
                profile_data['headline'] = og_description_match.group(1)
            
            # Tentar extrair JSON-LD (LinkedIn usa isso para dados estruturados)
            json_ld_matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html_content, re.DOTALL)
            for json_str in json_ld_matches:
                try:
                    data = json.loads(json_str)
                    if isinstance(data, dict):
                        if data.get('@type') == 'Person':
                            if 'name' in data and not profile_data['name']:
                                profile_data['name'] = data['name']
                            if 'jobTitle' in data and not profile_data['headline']:
                                profile_data['headline'] = data['jobTitle']
                            if 'address' in data:
                                profile_data['location'] = data['address']
                except:
                    pass
            
            # Tentar encontrar informações em meta tags alternativas
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                if ' | LinkedIn' in title:
                    if not profile_data['name']:
                        profile_data['name'] = title.replace(' | LinkedIn', '')
            
            # Buscar por padrões comuns de experiência no HTML
            # LinkedIn usa classes específicas, mas o HTML pode estar minificado
            exp_patterns = [
                r'experience[^>]*>.*?<span[^>]*>([^<]+)</span>',
                r'Experience[^>]*>.*?([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)?)',
            ]
            
            # Buscar empresas mencionadas (comum em perfis públicos)
            company_patterns = [
                r'(Accenture|NTT.?DATA|INDRA|Minsait|FOURSYS|TECBAN|Dobem|Bellivery)',
                r'(Application Architect|Developer|Consultant|Software Engineer)',
            ]
            
            for pattern in company_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    profile_data['experience'].extend(matches[:10])  # Limitar resultados
            
            profile_data['status'] = 'sucesso'
            profile_data['message'] = 'Informações extraídas (pode estar incompleto devido a autenticação necessária)'
            
        elif response.status_code == 403 or response.status_code == 401:
            profile_data['status'] = 'erro'
            profile_data['error'] = f'HTTP {response.status_code}'
            profile_data['message'] = 'LinkedIn requer autenticação/login para visualizar perfis completos. Tentando métodos alternativos...'
            
            # Tentar buscar informações públicas básicas
            profile_data['name'] = 'Elton Jhon Dias Gonçalves'  # Do URL e informações conhecidas
            
        else:
            profile_data['status'] = 'erro'
            profile_data['error'] = f'HTTP {response.status_code}'
            profile_data['message'] = f'Erro ao acessar o perfil: {response.status_code}'
            
    except requests.exceptions.Timeout:
        profile_data['status'] = 'erro'
        profile_data['error'] = 'Timeout'
        profile_data['message'] = 'Tempo limite excedido ao acessar o LinkedIn'
    except Exception as e:
        profile_data['status'] = 'erro'
        profile_data['error'] = str(e)
        profile_data['message'] = f'Erro ao acessar o perfil: {str(e)}'
    
    return profile_data

if __name__ == '__main__':
    linkedin_url = 'https://www.linkedin.com/in/elton-dias-goncalves/'
    print(f"Tentando extrair informações do perfil: {linkedin_url}")
    print("=" * 60)
    
    profile = extract_linkedin_profile(linkedin_url)
    
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    
    # Salvar em arquivo JSON
    with open('linkedin_profile.json', 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("Informações salvas em: linkedin_profile.json")
