#!/usr/bin/env python3
"""Documented French-language QA for SKILL-ISSUE OSCP notes.

Never execute any OSCP command. Keep all non-comment code lines unchanged.
Only translate high-confidence natural-language # comments and headings, and
classify clear data/reference values as inline reference notes.
"""
from __future__ import annotations
import collections
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path("docs/src/oscp")
OUTPUT = Path("oscp-french-quality-audit.json")
FENCE = chr(96) * 3

FR_BEGIN = re.compile(
    r"^(?:utiliser|afficher|vérifier|contrôler|tester|examiner|créer|lister|"
    r"télécharger|envoyer|rechercher|exécuter|définir|ouvrir|fermer|obtenir|"
    r"récupérer|installer|désinstaller|depuis|avec|sans|pour|exemple|"
    r"récepteur|émetteur|connexion|résoudre|accéder|lancer|lecture|"
    r"local|domaine|recherche|enregistrement|analyse|écouter|fichier|"
    r"chemin|étape|consulter|machine|rappel|option|variante|autre|"
    r"une|un|les|le|la|des|et|information|identifiant|"
    r"configuration|commande|attention)\b", re.I
)
EN_BEGIN = re.compile(
    r"^(?:the|this|these|those|for|from|with|without|using|use|"
    r"to|if|when|while|then|after|before|next|first|now|"
    r"run|check|verify|test|list|show|display|enumerate|"
    r"download|upload|save|create|add|copy|search|find|"
    r"retrieve|read|write|execute|exec|connect|disconnect|"
    r"open|close|install|uninstall|restart|start|stop|"
    r"set|specify|replace|change|extract|print|filter|"
    r"query|scan|scaning|attempt|try|ensure|identify|"
    r"get|mount|enable|disable|lock|unlock|import|export|"
    r"we|you|it|example|examples|note|tip|warning|"
    r"credentials|credential|password|passwords|"
    r"hash|hashes|user|users|service|services|"
    r"directory|directories|file|files|"
    r"script|scripts|server|servers|"
    r"domain|domains|port|ports|"
    r"windows|linux|basic|advanced|output|"
    r"data|target|source|shell|remote|local|"
    r"attack|attacks|vulnerability|vulnerabilities|"
    r"authentication|privileges|network|"
    r"networking|custom|current|general|"
    r"alternative|only|all|no|"
    r"python|powershell|bash|"
    r"nmap|netcat|john|hashcat)\b", re.I
)
EN_WORDS = re.compile(
    r"\b(?:the|with|without|using|from|download|upload|"
    r"check|run|show|find|search|creates|create|saving|save|"
    r"list|user|users|file|files|server|when|then|before|"
    r"after|this|that|those|these|for|the|target|"
    r"command|commands|script|scripts|example|examples|"
    r"password|credentials|directory|scan|scanning|"
    r"authentication|network|port|ports|"
    r"output|executing|execute|detect|"
    r"trying|from|allow|write|read|other|same|"
    r"options|specified|specified|new|"
    r"several|default|remote|local|"
    r"information|information|connected)\b", re.I
)

# Manually verified source-based translations: fixes recurrent technical terms.
MANUAL = {
    "Example": "Exemple",
    "Example:": "Exemple :",
    "For example": "Par exemple",
    "Example usage": "Exemple d’utilisation",
    "From Windows": "Depuis Windows",
    "From Kali": "Depuis Kali",
    "Using PowerShell": "Avec PowerShell",
    "Using NTLM hash": "Avec le hash NTLM",
    "Using an NTLM hash": "Avec un hash NTLM",
    "No Password": "Sans mot de passe",
    "Wrong User or Key": "Utilisateur ou clé incorrects",
    "Credentials": "Identifiants",
    "Pass the Hash": "Pass-the-Hash",
    "Testing with Crackmapexec": "Vérification avec CrackMapExec",
    "Save output to a file": "Enregistrer la sortie dans un fichier",
    "Run specific script": "Exécuter un script précis",
    "Get help on what a script does": "Afficher l’aide du script",
    "Update the script database": "Actualiser la base de scripts",
    "Run the exploit with appropriate parameters": "Exécuter le script avec les paramètres appropriés",
    "Create a Socket": "Créer une socket",
    "Connect to the Server": "Se connecter au serveur",
    "Receive the banner": "Recevoir la bannière",
    "Close the socket": "Fermer la socket",
    "Linux": "Linux",
    "Windows": "Windows",
    "Example: ": "Exemple : ",
    "Using the NTLM hash": "Avec le hash NTLM",
    "Use custom user-agent": "Utiliser un agent utilisateur personnalisé",
    "Basic directory scanning": "Scan élémentaire des répertoires",
    "Basic file scanning": "Recherche élémentaire de fichiers",
    "From PowerShell": "Depuis PowerShell",
    "From CMD": "Depuis CMD",
    "Using -e": "Avec l’option -e",
    "Without -e option": "Sans l’option -e",
    "Using credentials": "Avec des identifiants",
    "Using hashes": "Avec des empreintes",
    "Save output to a file": "Enregistrer la sortie dans un fichier",
    "Creates the new user": "Crée le compte utilisateur",
    "From Kali (GetNPUsers.py)": "Depuis Kali (GetNPUsers.py)",
    "Run a category of scripts": "Exécuter une catégorie de scripts",
}

# Protected strings are restored byte-for-byte after translation.
MASK = re.compile(
    r"https?://[^\s]+|"
    r"\u0060[^\u0060]+\u0060|"
    r"(?<![a-zA-Z])\$[a-zA-Z_][a-zA-Z_0-9]*|"
    r"<[^>\n]{1,100}>|"
    r"\[[a-zA-Z_][a-zA-Z_0-9:/\\.-]*\]|"
    r"--[a-zA-Z][a-zA-Z_0-9-]*|"
    r"(?<![a-zA-Z])-[A-Z]\b|"
    r"\b[A-Z][A-Z0-9_]{2,}\b|"
    r"(?:\b[a-zA-Z_0-9.-]+/){2,}[a-zA-Z_0-9.-]+|"
    r"\b[a-zA-Z_0-9.-]+\.(?:exe|dll|txt|py|ps1|sh|json|xml|html|php|sql|c|cpp|h|bat|cmd|conf|log)\b|"
    r"\b\d{1,3}(?:\.\d{1,3}){3}\b"
)

def count_words_en(text: str) -> int:
    return len(EN_WORDS.findall(text))

def needs_french(text: str) -> bool:
    s=text.strip()
    if not s or re.match(r"^(?:#(?:include|define|if|ifdef|endif|pragma)|!/)",s):
        return False
    if s in MANUAL:
        return True
    if FR_BEGIN.search(s):
        return False
    return bool(EN_BEGIN.search(s) or count_words_en(s)>=2)

def protect(text: str) -> tuple[str,dict[str,str]]:
    cache={}
    def mask(match: re.Match) -> str:
        token="ZXQ"+str(len(cache)).zfill(4)+"ZXQ"
        cache[token]=match.group(0)
        return token
    return MASK.sub(mask,text),cache

def restore(translated: str,cache: dict[str,str]) -> str | None:
    for token,value in cache.items():
        # Model may insert spaces in the middle of a marker.
        normalized=re.sub(r"\s+","",translated)
        if token not in normalized:
            return None
        translated=re.sub(r"\s*".join(map(re.escape,token)),lambda _:value,translated,flags=re.I)
    if re.search(r"ZXQ\d+ZXQ",translated,re.I):
        return None
    return translated

def translate_safe(text: str,translator,audit:dict) -> str | None:
    original=text.strip()
    if original in MANUAL:
        return MANUAL[original]
    masked,codes=protect(original)
    try:
        translated=translator(masked)
    except Exception as exc:
        audit["translation_errors"].append({"source":original[:160],"error":str(exc)[:150]})
        return None
    translated=restore(translated,codes)
    if translated is None or not translated.strip():
        audit["unsafe_translations"].append(original[:250])
        return None
    # Keep meaningful line endings and technical punctuation.
    if len(translated)>max(150,4*len(original)):
        audit["unsafe_translations"].append(original[:250])
        return None
    return translated

def data_type(text:str, lang:str) -> str|None:
    if lang!="text":return None
    t=text.strip()
    if "\n" in t or len(t)>400 or not t: return None
    if re.fullmatch(r"[a-zA-Z]:\\[^\n]+",t) or re.fullmatch(r"/(?:usr|etc|var|tmp|root|home|opt|proc|dev|mnt)/[^\n]+",t):
        return "Chemin de référence"
    if re.match(r"^\$(?:1|2[abxy]?|5|6|krb5)",t):
        return "Exemple de format d’empreinte"
    if re.fullmatch(r"[*.?\[\]]{1,3}",t):
        return "Caractère de recherche"
    if re.fullmatch(r"https?://[^\s]+",t):
        return "URL de référence"
    if re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_.-]+",t,re.I) and "/" not in t:
        return "Exemple de valeur"
    if re.fullmatch(r"--[a-z][a-z0-9-]*(?:\s+\[[^\]]+\])?",t,re.I):
        return "Option de commande"
    if re.fullmatch(r"[a-z0-9]+\.(?:txt|log|json|xml|php|html|ps1)",t,re.I):
        return "Nom de fichier"
    if re.fullmatch(r"<[^>]+>=<[^>]+>(?:&<[^>]+>=\^PASS\^)?",t):
        return "Paramètre de formulaire"
    return None

def classify_data(md: str,stats: dict) -> str:
    # An attached explanation is removed only when a reference replaces
    # its fenced code; the reference itself is preserved visibly.
    pattern=re.compile(
        r"(?:<p class=\"oscp-command-note\">([^<]*)</p>\s*)?"
        r"^"+FENCE+r"text\n([\s\S]*?)^"+FENCE+r"\s*$",
        re.M
    )
    def change(m):
        kind=data_type(m.group(2), "text")
        if not kind:return m.group(0)
        stats["references_reclassified"]+=1
        content=m.group(2).strip()
        # VitePress code span may contain backticks; use escaped HTML code.
        return '<p class="oscp-inline-ref"><strong>'+kind+' :</strong> <code>'+html.escape(content)+'</code></p>'
    return pattern.sub(change,md)

def clean_document(content: str,filename: str,translator,audit:dict):
    stats=collections.Counter()
    if filename in ("index","ad-theorie","cloud","references"):
        return content,stats
    working=classify_data(content,stats)
    result=[]
    in_code=False
    lines=working.splitlines(keepends=True)
    for line in lines:
        if line.lstrip().startswith(FENCE):
            in_code=not in_code
            result.append(line)
            continue
        if not in_code:
            heading=re.match(r"^(\s*#{2,5}\s+)([^\n]+)(\n?)$",line)
            if heading and needs_french(heading.group(2)):
                trans=translate_safe(heading.group(2),translator,audit)
                if trans:
                    line=heading.group(1)+trans+heading.group(3)
                    stats["titles_translated"]+=1
                else:
                    audit["not_translated"].append({"file":filename,"type":"heading","value":heading.group(2)[:200]})
            bold=re.match(r"^(\s*\*\*)([^*\n]{3,110})(\*\*\s*)(\n?)$",line)
            if bold and needs_french(bold.group(2)) and not re.search(r"[<$\u0060{}]|--",bold.group(2)):
                trans=translate_safe(bold.group(2),translator,audit)
                if trans:
                    line=bold.group(1)+trans+bold.group(3)+bold.group(4)
                    stats["labels_translated"]+=1
                else:
                    audit["not_translated"].append({"file":filename,"type":"label","value":bold.group(2)[:200]})
            result.append(line)
            continue
        match=re.match(r"^(\s*)#\s+([^#\n].*?)(\r?\n?)$",line)
        if not match or not needs_french(match.group(2)):
            result.append(line)
            continue
        prose=match.group(2).strip()
        translated=translate_safe(prose,translator,audit)
        if translated:
            result.append(match.group(1)+"# "+translated+match.group(3))
            stats["comments_translated"]+=1
        else:
            result.append(line)
            audit["not_translated"].append({"file":filename,"type":"comment","value":prose[:250]})
    return "".join(result),stats

def noncomment_code(md: str):
    blocks=re.findall(r"^"+FENCE+r"[^\n]*\n([\s\S]*?)^"+FENCE,md,re.M)
    lines=[]
    for code in blocks:
        for line in code.splitlines():
            if line.strip() and not re.match(r"^\s*#\s+",line):
                lines.append(line)
    return collections.Counter(lines)

def main():
    import argostranslate.package
    import argostranslate.translate
    argostranslate.package.update_package_index()
    packages=argostranslate.package.get_available_packages()
    package=next((p for p in packages if p.from_code=="en" and p.to_code=="fr"),None)
    assert package is not None,"Offline en->fr translation model not available"
    argostranslate.package.install_from_path(package.download())
    translation=lambda value:argostranslate.translate.translate(value,"en","fr")
    audit={"per_file":{},"not_translated":[],"unsafe_translations":[],"translation_errors":[]}
    totals=collections.Counter()
    for p in sorted(ROOT.glob("*.md")):
        original=p.read_text(encoding="utf-8")
        updated,stats=clean_document(original,p.stem,translation,audit)
        # Only pure reference lines may leave fenced code. All remaining
        # executable or code-data lines must remain exactly the same.
        orig=noncomment_code(original)
        after=noncomment_code(updated)
        missing=orig-after
        # Any converted data reference must still appear verbatim in
        # the resulting document. The QA must not hide silently lost data.
        lost=[s for s,n in missing.items() if n>0 and html.escape(s) not in updated and s not in updated]
        if lost:
            raise AssertionError(f"Lost {len(lost)} non-comment code lines in {p}: {lost[:4]}")
        p.write_text(updated,encoding="utf-8")
        audit["per_file"][p.stem]=dict(stats)
        totals.update(stats)
        print(p.name,dict(stats),flush=True)
    remaining=[]
    english_headings=[]
    for p in sorted(ROOT.glob("*.md")):
        s=p.read_text(encoding="utf-8")
        for block in re.findall(r"^"+FENCE+r"[^\n]*\n([\s\S]*?)^"+FENCE,s,re.M):
            for line in block.splitlines():
                match=re.match(r"^\s*#\s+(.+)",line)
                if match and needs_french(match.group(1)):
                    remaining.append({"file":p.name,"comment":match.group(1)[:200]})
        for m in re.finditer(r"^#{2,5}\s+(.+)",s,re.M):
            if needs_french(m.group(1)):english_headings.append({"file":p.name,"title":m.group(1)[:150]})
    audit["totals"]=dict(totals)
    audit["remaining_english_comments"]=remaining
    audit["remaining_english_headings"]=english_headings
    OUTPUT.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"totals":dict(totals),"english_comments_remaining":len(remaining),"english_titles_remaining":len(english_headings),"unsafe":len(audit["unsafe_translations"]),"other_untranslated":len(audit["not_translated"])},ensure_ascii=False,indent=2))
    assert totals["comments_translated"]>350, "Not enough comments translated"
    assert totals["references_reclassified"]>=15, "Reference reclassification incomplete"

if __name__=="__main__":
    main()
