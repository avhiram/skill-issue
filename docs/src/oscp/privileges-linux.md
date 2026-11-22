---
title: "OSCP · Élévation de privilèges Linux"
description: "Examiner les permissions, processus et configurations d'un système Linux."
---

# OSCP · Élévation de privilèges Linux

Examiner les permissions, processus et configurations d'un système Linux.

## Énumération

### Identifier l'utilisateur et ses groupes

```bash
id
```

### Identifier le nom de la machine

```bash
hostname
```

### Lire la bannière système

`/etc/issue` peut être personnalisé : ne pas s'y fier pour identifier la version exacte.

```bash
cat /etc/issue
```

### Lire la version de la distribution

```bash
cat /etc/os-release
```

### Identifier le noyau et l'architecture

```bash
uname -a
```

### Lister les processus

`ps aux` affiche les processus, leurs PID, propriétaires et ressources consommées.

```bash
ps aux
```

### Identifier les interfaces et adresses IP

`ip a` affiche les interfaces et leurs adresses, pas les routes.

```bash
ip a
```

### Lister les sockets et les processus associés

`ss -anp` affiche les sockets sans résolution DNS ; les processus peuvent être masqués sans droits suffisants.

```bash
ss -anp
```

### Examiner les règles IPv4 sauvegardées

`rules.v4` dépend d'`iptables-persistent` ; ce n'est pas forcément le pare-feu actif.

```bash
cat /etc/iptables/rules.v4
```

### Identifier les fichiers cron du système

Ne couvre pas les crontabs utilisateur ni les minuteurs systemd.

```bash
ls -lah /etc/cron*
```

### Lire ses tâches cron

Une absence de crontab n'exclut pas des tâches système.

```bash
crontab -l
```

### Lire la crontab root avec sudo

Nécessite une autorisation sudo appropriée.

```bash
sudo crontab -l
```

### Inventorier les paquets Debian/Ubuntu

`dpkg -l` liste les paquets et leurs états, pas les installations manuelles.

```bash
dpkg -l
```

### Trouver les dossiers accessibles en écriture

`-writable` vérifie l'accès du compte courant ; les chemins interdits sont ignorés.

```bash
find / -writable -type d 2>/dev/null
```

**Limites de lecture de la mémoire physique**

<p class="oscp-command-note">`/dev/mem` est généralement restreint ; cette recherche ne garantit pas de retrouver des secrets.</p>

```bash
# Nécessite des droits élevés ; souvent bloqué par le noyau
sudo strings -n 10 /dev/mem 2>/dev/null | grep -i 'pass'
```

### Rechercher « password » dans l'index local

`locate` dépend d'un index qui peut être incomplet ou ancien.

```bash
locate -i password | less
```

### Examiner les montages prévus au démarrage

`fstab` décrit les montages configurés, pas nécessairement actifs.

```bash
cat /etc/fstab
```

### Lister les systèmes de fichiers montés

```bash
mount
```

### Identifier disques et partitions

`lsblk` ne recense pas tous les montages réseau.

```bash
lsblk
```

### Identifier les modules chargés

`lsmod` n'affiche que les modules chargés.

```bash
lsmod
```

### Examiner un module disponible

`modinfo` décrit un module installé, même s'il n'est pas chargé.

```bash
modinfo NOM_MODULE
```

### Rechercher les exécutables SUID

SUID ne signifie pas automatiquement qu'un fichier est vulnérable.

```bash
find / -perm -u=s -type f 2>/dev/null
```

### Identifier les commandes autorisées par sudo

`sudo -l` peut demander le mot de passe et liste les droits accordés.

```bash
sudo -l
```

### Ouvrir un shell de connexion avec sudo

`sudo -i` ouvre un shell de connexion si la politique sudo l'autorise.

```bash
sudo -i
```

## Inventaire complémentaire

### Interfaces et connexions

Afficher adresses IP, routes et ports en écoute.

`ip` nécessite `iproute2` ; `ss -tulpn` peut masquer les processus sans privilèges.

```bash
ip -br address
ip route
ss -tulpn
```

### Volumes et espace disque

Comparer les périphériques et l'espace occupé.

`lsblk -f` identifie les volumes ; `df -hT` affiche les montages et l'espace utilisé.

```bash
lsblk -f
df -hT
```

### Arbre de processus

Lister les processus et leurs relations parent-enfant.

`ps auxww` évite de tronquer les lignes ; `ps axjf` affiche l'arbre des processus.

```bash
ps auxww
ps axjf
```

## Examiner les services

```bash
watch -n 1 "ps auxww | grep -i '[p]ass'"  # Recherche un motif, pas tous les secrets

```

```bash
# Examiner les paquets en texte lisible sur loopback (droits requis)
sudo tcpdump -i lo -A | grep -i 'pass'

```

```bash
# Enregistrer les paquets accessibles (droits requis)
sudo tcpdump -i any -s 0 -w capture.pcap
sudo tcpdump -i eth0 -w capture.pcap -n -U -s 0 'not host 10.11.1.111'
sudo tcpdump -vv -i eth0 'not host 10.11.1.111'

```

## Tâches cron

Examiner les tâches planifiées, leurs propriétaires et les scripts exécutés.

<p class="oscp-command-note">Cron : rechercher les exécutions dans les journaux accessibles.</p>

```bash
grep -i 'cron' /var/log/syslog  # Debian/Ubuntu, si disponible
# Autre journal selon la distribution
grep -i 'cron' /var/log/cron  # RHEL/CentOS, si disponible

```

<p class="oscp-command-note">Cron : vérifier les droits du script exécuté par la tâche planifiée.</p>

```bash
ls -l /chemin/vers/script.sh

```

<p class="oscp-command-note">Cron : vérifier si le script et ses répertoires parents sont modifiables.</p>

```bash
namei -l /chemin/vers/script.sh
```

<p class="oscp-command-note">Cron : afficher les tâches de l'utilisateur et examiner les répertoires de planification.</p>

```bash
crontab -l
ls -alh /var/spool/cron /var/spool/cron/crontabs 2>/dev/null
ls -lah /etc/cron* 2>/dev/null
ls -l /etc/at.allow /etc/at.deny /etc/cron.allow /etc/cron.deny 2>/dev/null
cat /etc/crontab
cat /etc/anacrontab 2>/dev/null
sudo crontab -u root -l  # Uniquement si autorisé

```

### Comptes Unix et identifiants privilégiés

<p class="oscp-command-note">Créer un hash SHA-512 crypt en saisissant le mot de passe dans l'invite OpenSSL.</p>

```bash
openssl passwd -6

```

```bash
# Examiner les comptes ayant un UID égal à 0 (lecture seule)
awk -F: '$3 == 0 {print $1 ":" $3 ":" $7}' /etc/passwd
```

<p class="oscp-command-note">Se connecter à un compte de test connu, puis vérifier son UID et ses groupes.</p>

```bash
su NOM_COMPTE

# Afficher l'UID et les groupes
id

```

### Examiner les empreintes de /etc/shadow

<p class="oscp-command-note">Shadow : extraire la ligne root si l'accès privilégié est autorisé.</p>

```bash
sudo grep '^root:' /etc/shadow > root_hash.txt

```

<p class="oscp-command-note">Tester hors ligne un hash SHA-512 crypt (`$6$`) avec une liste de mots de passe autorisée.</p>

```bash
# John the Ripper : tester l'empreinte extraite
john --wordlist=/usr/share/wordlists/rockyou.txt root_hash.txt

# Extraire uniquement le hash de la ligne shadow avant Hashcat
cut -d: -f2 root_hash.txt > sha512crypt.hash
hashcat -m 1800 sha512crypt.hash /usr/share/wordlists/rockyou.txt

```

```bash
# Afficher les résultats enregistrés par John
john --show root_hash.txt

# Hashcat : afficher les correspondances déjà trouvées
hashcat -m 1800 sha512crypt.hash --show

```

### Inventorier les exécutables SUID

<p class="oscp-command-note">Lister les fichiers réguliers avec le bit SUID ; ce n'est pas une preuve de vulnérabilité.</p>

```bash
find / -perm -4000 -type f 2>/dev/null

```

<p class="oscp-command-note">Afficher le propriétaire et les permissions des fichiers SUID.</p>

```bash
find / -perm -4000 -type f -exec ls -l {} + 2>/dev/null

```

### Examiner le comportement des binaires SUID

<p class="oscp-command-note">Remplacer `NOM_BINAIRE` par un nom réel pour afficher les processus correspondants.</p>

```bash
ps u -C NOM_BINAIRE

```

<p class="oscp-command-note">Lire les UID réel, effectif, sauvegardé et de système de fichiers d'un PID.</p>

```bash
grep '^Uid:' /proc/1234/status  # Remplacer 1234 par le PID

```

<p class="oscp-command-note">Exécuter `ls -l` sur chaque fichier trouvé ; aucun privilège supplémentaire n'est accordé.</p>

```bash
find /chemin -type f -exec ls -l {} \;

```

```bash
# Rechercher le binaire ciblé ; la recherche seule n'élève aucun privilège
find / -type f -name 'NOM_BINAIRE' 2>/dev/null

```

### Rechercher les capacités Linux

<p class="oscp-command-note">Lister les capacités associées aux fichiers accessibles.</p>

```bash
getcap -r / 2>/dev/null

```

<p class="oscp-command-note">Afficher les capacités attribuées à un exécutable.</p>

```bash
getcap /chemin/vers/binaire

# Exemple : si le fichier existe
getcap /usr/bin/nmap

```

<p class="oscp-command-note">Attribuer `CAP_NET_BIND_SERVICE` dans un laboratoire ; nécessite root ou `CAP_SETFCAP`.</p>

```bash
sudo setcap cap_net_bind_service=ep /chemin/vers/binaire

# Vérifier les capacités après modification
getcap /chemin/vers/binaire

```

<p class="oscp-command-note">Supprimer les capacités d'un exécutable (droits élevés requis).</p>

```bash
sudo setcap -r /chemin/vers/binaire

# Exemple (nécessite les droits root)
sudo setcap -r /usr/bin/nmap

```

### Comprendre les capacités Linux

**CAP_AUDIT_CONTROL** — Contrôler l'audit du noyau, notamment son activation.

**CAP_AUDIT_WRITE** — Écrire des événements dans le journal d'audit.

**CAP_BLOCK_SUSPEND** — Bloquer la mise en veille via certaines interfaces du noyau.

**CAP_CHOWN** — Modifier le propriétaire des fichiers.

**CAP_DAC_OVERRIDE** — Contourner des contrôles classiques de lecture, écriture et parcours.

**CAP_DAC_READ_SEARCH** — Contourner certaines restrictions de lecture et de parcours.

**CAP_FOWNER** — Effectuer certaines opérations réservées au propriétaire d'un fichier.

**CAP_IPC_LOCK** — Verrouiller des pages mémoire.

**CAP_KILL** — Contourner certaines vérifications de permission pour envoyer des signaux.

**CAP_MAC_ADMIN** — Modifier certaines règles de contrôle d'accès obligatoire (MAC).

**CAP_NET_BIND_SERVICE** — Lier un socket aux ports privilégiés (généralement inférieurs à 1024).

**CAP_NET_RAW** — Créer des sockets RAW et PACKET.

**CAP_SETGID** — Modifier les identifiants de groupe du processus.

**CAP_SETPCAP** — Manipuler certaines capacités des processus.

**CAP_SETUID** — Modifier les identifiants utilisateur du processus.

### Minuteurs systemd et cron système

Comparer les fichiers cron aux minuteurs systemd ; `systemctl` exige un système compatible.

<p class="oscp-command-note">Lister les dossiers cron et les minuteurs systemd configurés.</p>

```bash
ls -ld /etc/cron*
systemctl list-timers --all
```

## Autorisations sudo

Vérifier les commandes autorisées pour le compte courant.

<p class="oscp-command-note">Lister les droits sudo accordés.</p>

```bash
sudo -l
```

<p class="oscp-command-note">Chercher un nom de processus dans `/var/log/syslog` (Debian/Ubuntu, si présent).</p>

```bash
grep -F 'NOM_PROCESSUS' /var/log/syslog  # Si ce journal existe

```

## CVE Linux à vérifier selon la version

Ces CVE sont des pistes historiques, pas une preuve d'exploitabilité. Vérifier les correctifs rétroportés et les conditions exactes avant tout test.

**CVE-2010-3904**

RDS : vulnérabilité historique du noyau Linux ; vérifier la version et les correctifs.

**CVE-2010-4258**

Full Nelson : élévation locale historique ; vérifier la distribution et ses correctifs.

**CVE-2012-0056**

Mempodipper : élévation locale historique ; vérifier la version et la configuration.

**CVE-2016-5195**

Dirty COW : faille de concurrence dans la gestion mémoire ; vérifier les correctifs.

**CVE-2016-5696**

Vulnérabilité TCP du noyau ; ne pas la présenter comme une exécution de code à distance garantie.

**CVE-2017-8890**

Condition de concurrence du noyau ; vérifier les conditions d'exploitation.

**CVE-2018-8897**

Vulnérabilité liée à la gestion des interruptions ; vérifier le noyau et ses correctifs.

**CVE-2019-7304**

Vulnérabilité historique : vérifier l'avis CVE avant de l'associer à OverlayFS.

**CVE-2021-4034**

PwnKit : élévation locale dans `pkexec` (polkit), pas une CVE du noyau.

**CVE-2020-14386**

Vulnérabilité du noyau : vérifier l'avis CVE et les correctifs, sans supposer OverlayFS.

**CVE-2021-3156**

Baron Samedit : vulnérabilité de `sudo` ; vérifier le paquet et les correctifs rétroportés.

**CVE-2021-33034**

Vulnérabilité du noyau : confirmer les versions touchées dans l'avis du fournisseur.

**CVE-2022-0847**

Dirty Pipe : élévation locale liée aux pipes ; vérifier le correctif du noyau.

## Caractères génériques du shell

<p class="oscp-inline-ref"><strong>Zéro ou plusieurs caractères :</strong> <code>*</code></p>
<p class="oscp-inline-ref"><strong>Un caractère :</strong> <code>?</code></p>
<p class="oscp-inline-ref"><strong>Classe de caractères :</strong> <code>[]</code></p>
### Comprendre l'expansion des motifs

<p class="oscp-command-note">Lister les entrées non cachées de `/var/log` sélectionnées par `*`.</p>

```bash
ls /var/log/*

```

```bash
# Exemple d'archivage ; le risque dépend du répertoire courant
tar -cvf archive.tar /var/log/*  # Archive non compressée

```

### Motifs littéraux et motifs développés

```bash
touch '/tmp/file_*'  # Les guillemets empêchent l'expansion  # Crée un nom contenant * ; sans guillemets, le shell peut développer le motif

```

<p class="oscp-command-note">Copier les fichiers visibles de `/etc` ; les sous-dossiers nécessitent `-r`.</p>

```bash
# Le dossier cible doit exister et être accessible en écriture.
cp -v /etc/* /tmp/backup/

```

#### Observer l'expansion du shell

Afficher les noms correspondant au motif sans lire les fichiers.

<p class="oscp-command-note">Afficher les noms sélectionnés par le motif `./*` sans les modifier.</p>

```bash
printf '%s\n' ./*
```

## Groupe disk : accès brut aux volumes

Vérifier `id` et les droits du périphérique ; `debugfs` cible les systèmes ext2/3/4.

```bash
id
findmnt -no SOURCE /
```

```text
debugfs /dev/sda1  # Adapter le périphérique et vérifier le type ext
debugfs: cd /root  # Commande interne à debugfs
debugfs: ls
debugfs: cat /root/.ssh/id_rsa
debugfs: cat /etc/shadow

```

## UDF MySQL : vérifier les prérequis

Les fonctions `sys_exec` et `sys_eval` nécessitent une UDF préinstallée.

<p class="oscp-command-note">MySQL : ces fonctions ne sont pas natives ; elles exigent une UDF installée et autorisée.</p>

```sql
SELECT sys_exec('whoami');
SELECT sys_eval('whoami');

```

## Logiciels installés manuellement

<p class="oscp-command-note">Chemins à inspecter ; il ne s'agit pas de commandes.</p>

```text
/usr/local/
/usr/local/src/
/usr/local/bin/
/opt/
/home/
/var/
/usr/src/
```

<p class="oscp-command-note">Lister les paquets avec le gestionnaire de la distribution.</p>

```bash
# Debian/Ubuntu
dpkg -l

# Fedora/RHEL/CentOS/openSUSE
rpm -qa

# OpenBSD
pkg_info

# FreeBSD
pkg info

```

## Repérer les secrets exposés

Examiner uniquement les données accessibles et utiles au périmètre autorisé.

<p class="oscp-command-note">Exemples de combinaisons faibles (données, pas commandes).</p>

```text
root:root
username:username
username:username1
username:root
username:admin
username:qwerty
username:password

```

```bash
# Lister les boîtes aux lettres locales accessibles
ls -lah /var/mail /var/spool/mail 2>/dev/null
```

```bash
./LinEnum.sh -t -k password

```

### Ports et connexions réseau

<p class="oscp-command-note">Identifier les sockets en écoute et les connexions TCP/UDP.</p>

```bash
# Services en écoute
ss -tulpen
ss -tunap  # PID visibles selon les droits

```

### Rechercher les coffres KeePass

Un fichier `.kdbx` est chiffré ; sa présence ne donne pas le mot de passe.

<p class="oscp-command-note">Rechercher les fichiers `.kdbx` accessibles sous `/home`.</p>

```bash
find /home -type f -name '*.kdbx' 2>/dev/null
```

### Repérer les dossiers SSH

Lister les dossiers `.ssh` accessibles ; leurs clés ne sont pas forcément lisibles.

<p class="oscp-command-note">Répertoires `.ssh` sous `/home`.</p>

```bash
find /home -type d -name '.ssh' 2>/dev/null
```

## Permissions des répertoires

<p class="oscp-command-note">Distinguer les droits du compte courant des permissions accordées à tous.</p>

```bash
# Répertoires modifiables par le compte courant, puis par tous
find / -writable -type d 2>/dev/null
find / -perm -002 -type d 2>/dev/null
find / -perm -o=w -type d 2>/dev/null  # Équivalent à -002

# Dossiers traversables par « autres »
find / -perm -o=x -type d 2>/dev/null

# Répertoires modifiables et traversables par tous
find / \( -perm -o=w -perm -o=x \) -type d 2>/dev/null

```

## Examiner les montages et volumes

```bash
mount -l
cat /etc/fstab

```

## Fichiers SUID et SGID

Examiner les permissions et la configuration de Linux.

### Comprendre les permissions SUID et SGID

SUID exécute un fichier avec l'UID effectif de son propriétaire ; SGID utilise le GID effectif de son groupe.

### Rechercher les fichiers SUID et SGID

Lister les fichiers avec les bits SUID ou SGID activés.

<p class="oscp-command-note">Repérer les fichiers et dossiers aux permissions sensibles.</p>

```bash
# Trouver des fichiers SUID
find / -perm -u=s -type f 2>/dev/null

# Trouver des fichiers SGID
find / -perm -g=s -type f 2>/dev/null

```

### Évaluer les possibilités d’exploitation

<p class="oscp-command-note">Examiner un binaire SUID : chaînes et appels de bibliothèque (outils disponibles selon la distribution).</p>

```bash
# Option 1 : rechercher les chaînes lisibles avec strings.
strings /path/to/suid-binary

# Option 2 : observer les appels de bibliothèque (ltrace, si disponible).
ltrace /path/to/suid-binary

# Option 3 : étudier si la résolution d'un exécutable via PATH peut modifier le comportement d'un programme SUID.
# Créer un exécutable de test pour illustrer le risque de recherche dans PATH
printf '#!/bin/sh\nexec /bin/sh\n' > /tmp/cp
chmod +x /tmp/cp

# Placer le répertoire du binaire de remplacement en priorité dans PATH
export PATH=/tmp:$PATH

# Exécuter uniquement un programme de laboratoire dont le comportement est connu
/path/to/suid-program

```

<p class="oscp-command-note">Repérer les fichiers et dossiers aux permissions sensibles.</p>

```bash
# Trouver des fichiers enregistrables SUID
find / -perm -u=s -writable -type f 2>/dev/null

# Un fichier SUID modifiable est un risque ; l'effet dépend du propriétaire, du montage et du noyau.

```

```bash
# Rechercher des fichiers SUID dans les répertoires cron accessibles
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

<p class="oscp-command-note">Rechercher les chemins et fonctions sensibles dans les chaînes d'un binaire SUID.</p>

```bash
strings <BINAIRE_SUID> | grep -Ei '(/bin/|/usr/|system|exec|sh )'
```

### LinPEAS

```bash
./linpeas.sh | tee linpeas_output.txt

```

<p class="oscp-command-note">Convertir le rapport LinPEAS avec les scripts `peas2json.py`, `json2html.py` et `json2pdf.py` s'ils sont installés.</p>

```bash
# Copier le rapport sur la machine d'analyse autorisée.

# Convertir le texte en JSON.
python3 peas2json.py ./linpeas_output.txt peass.json

# Convertir le JSON en HTML.
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

<p class="oscp-command-note">Exécuter le script `exploit-suggester.py` uniquement s'il est présent et compatible avec Python 3.</p>

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
