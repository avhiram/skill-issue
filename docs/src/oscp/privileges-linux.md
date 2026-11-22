---
title: "OSCP · Élévation de privilèges Linux"
description: "Examiner les permissions, processus et configurations d'un système Linux."
---

# OSCP · Élévation de privilèges Linux

Examiner les permissions, processus et configurations d'un système Linux.

## Énumération initiale

### Identifier l'utilisateur et ses groupes

`id` affiche les UID, GID et groupes supplémentaires.

```bash
id
```

### Examiner les droits sudo

`sudo -l` peut demander une authentification et liste les règles applicables au compte courant.

```bash
sudo -l
```

### Trouver les fichiers avec le bit SUID

Liste les fichiers ordinaires qui portent le bit SUID. Son effet à l’exécution dépend du propriétaire, des permissions d’exécution et des options du montage.

```bash
find / -type f -perm -u=s 2>/dev/null
```

### Identifier le nom de la machine

`hostname` affiche le nom configuré localement.

```bash
hostname
```

### Lire la bannière système

`/etc/issue` peut être personnalisé : ne pas s'y fier pour identifier la version exacte.

```bash
cat /etc/issue
```

### Lire la version de la distribution

`/etc/os-release` contient les identifiants et versions déclarés par la distribution.

```bash
cat /etc/os-release
```

### Identifier le noyau et l'architecture

`uname -a` affiche la version du noyau et l'architecture.

```bash
uname -a
```

### Lister les processus

`ps aux` affiche les PID, propriétaires et consommations CPU/mémoire ; la visibilité dépend de `/proc`.

```bash
ps aux
```

### Lister les adresses IP locales

`ip address` affiche les adresses des interfaces ; `ip route` affiche les routes séparément.

```bash
ip address show
```

### Identifier les sockets ouverts

`ss -anp` liste les sockets sans résoudre les noms ; `-p` peut nécessiter des privilèges pour afficher les PID.

```bash
ss -anp
```

### Lire les règles iptables sauvegardées

`rules.v4` n'existe que si des règles IPv4 ont été sauvegardées ; ce fichier ne garantit pas leur activation.

```bash
cat /etc/iptables/rules.v4 2>/dev/null
```

### Lister les fichiers cron système

Les fichiers `/etc/cron*` ne couvrent ni toutes les crontabs utilisateur ni les minuteurs systemd.

```bash
ls -lah /etc/cron* 2>/dev/null
```

### Lire la crontab courante

`crontab -l` affiche la crontab personnelle ou signale qu'elle n'existe pas.

```bash
crontab -l
```

### Lire la crontab root si autorisé

La politique sudo doit autoriser la lecture de la crontab root.

```bash
sudo crontab -u root -l
```

### Lister les paquets gérés par dpkg

`dpkg -l` affiche les paquets enregistrés et leur état sur Debian et dérivées.

```bash
dpkg -l
```

### Rechercher les répertoires modifiables

`-writable` teste les permissions du compte courant ; les erreurs d'accès sont masquées.

```bash
find / -type d -writable 2>/dev/null
```

### Comprendre les restrictions de `/dev/mem`

<p class="oscp-command-note">L'accès à `/dev/mem` est souvent bloqué par le noyau. Éviter de parcourir la mémoire brute sans autorisation explicite.</p>

```bash
# Vérifier les permissions du périphérique sans lire la mémoire physique
ls -l /dev/mem 2>/dev/null
```

### Rechercher des chemins via l'index locate

`locate` interroge un index local, qui peut être absent, incomplet ou périmé.

```bash
locate -i password | less
```

### Lire la configuration des montages

`/etc/fstab` décrit les montages configurés ; utiliser `findmnt` pour les montages actifs.

```bash
cat /etc/fstab
```

### Lister les systèmes de fichiers montés

`findmnt` affiche les points de montage actifs et leur source.

```bash
findmnt
```

### Lister les périphériques blocs

`lsblk` montre les périphériques blocs, mais pas l'ensemble des montages réseau.

```bash
lsblk
```

### Lister les modules du noyau actifs

`lsmod` n'affiche que les modules actuellement chargés.

```bash
lsmod
```

### Lire les métadonnées d'un module

Remplacer `NOM_MODULE` par un nom connu ; `modinfo` n'exige pas que le module soit chargé.

```bash
modinfo NOM_MODULE
```

### Ouvrir une session privilégiée si autorisée

`sudo -i` ouvre une session du compte cible, généralement root, seulement si autorisé.

```bash
sudo -i
```

## Inventaire complémentaire

### Adresses, routes et ports en écoute

Examiner les interfaces, les routes IPv4 et IPv6 et les services à l'écoute.

`ip` et `ss` appartiennent généralement à `iproute2` ; l'affichage des PID dépend des droits.

```bash
ip -br address
ip route show
ip -6 route show
ss -tulpn
```

### Volumes et espace disque

Comparer les périphériques détectés et l'espace des systèmes montés.

`lsblk -f` affiche les UUID et types de systèmes de fichiers ; `df -hT` indique le type et l'occupation des montages.

```bash
lsblk -f
df -hT
```

### Arbre de processus

Observer les processus et leurs relations de parenté.

`ps auxww` conserve les longues lignes de commande ; `ps axjf` montre la hiérarchie des processus.

```bash
ps auxww
ps axjf
```

## Examiner les processus et le trafic local

<p class="oscp-command-note">Surveiller les lignes de commande contenant un motif ; cela ne recherche pas les secrets dans la mémoire.</p>

```bash
watch -n 1 "ps auxww | grep -i '[p]ass'"  # Recherche un motif, pas tous les secrets

```

```bash
# Observer le trafic loopback en ASCII ; la capture ne déchiffre pas TLS
sudo tcpdump -i lo -nn -A | grep -i 'pass'

```

```bash
# Capturer les paquets accessibles dans un fichier PCAP (droits requis)
sudo tcpdump -i any -nn -s 0 -w capture.pcap
sudo tcpdump -i eth0 -nn -U -s 0 -w capture-eth0.pcap 'not host 10.11.1.111'
sudo tcpdump -vv -nn -i eth0 'not host 10.11.1.111'

```

## Examiner les tâches cron

Identifier les planifications, les comptes d'exécution et les permissions des scripts.

<p class="oscp-command-note">Rechercher les événements cron dans les journaux disponibles.</p>

```bash
grep -i 'cron' /var/log/syslog 2>/dev/null  # Debian/Ubuntu
# Autre journal selon la distribution
grep -i 'cron' /var/log/cron 2>/dev/null  # RHEL/CentOS

```

<p class="oscp-command-note">Examiner le propriétaire et les droits du script appelé par cron.</p>

```bash
stat /chemin/vers/script.sh

```

<p class="oscp-command-note">Contrôler les permissions de chaque répertoire parent du script cron.</p>

```bash
namei -l /chemin/vers/script.sh
```

<p class="oscp-command-note">Lister la crontab personnelle, les fichiers cron système et les restrictions d'accès.</p>

```bash
crontab -l
ls -alh /var/spool/cron /var/spool/cron/crontabs 2>/dev/null
ls -lah /etc/cron* 2>/dev/null
ls -l /etc/at.allow /etc/at.deny /etc/cron.allow /etc/cron.deny 2>/dev/null
cat /etc/crontab 2>/dev/null
cat /etc/anacrontab 2>/dev/null
sudo crontab -u root -l  # Uniquement si autorisé

```

### Comptes locaux et UID privilégiés

<p class="oscp-command-note">Générer un hash SHA-512 crypt de laboratoire sans placer le mot de passe en argument.</p>

```bash
openssl passwd -6

```

<p class="oscp-command-note">Un UID de 0 confère les privilèges root, quel que soit le nom du compte.</p>

```bash
# Afficher les noms, UID et shells des comptes ayant l'UID 0
awk -F: '$3 == 0 {print $1 ":" $3 ":" $7}' /etc/passwd
```

<p class="oscp-command-note">`su` demande généralement le mot de passe du compte cible ; `id` affiche ensuite les identifiants effectifs.</p>

```bash
su NOM_COMPTE

# Afficher l'UID et les groupes
id

```

### Empreintes de mots de passe dans shadow

<p class="oscp-command-note">La lecture de `/etc/shadow` nécessite généralement root ; protéger les copies de hashes.</p>

```bash
sudo grep '^root:' /etc/shadow > root_hash.txt  # Conserver ce fichier en lieu sûr

```

<p class="oscp-command-note">John et Hashcat peuvent tester un hash SHA-512 crypt (`$6$`) ; vérifier son format avant usage.</p>

```bash
# John : tester le hash avec une liste de mots de passe
john --wordlist=/usr/share/wordlists/rockyou.txt root_hash.txt

# Hashcat attend l'empreinte seule (sans les champs shadow)
cut -d: -f2 root_hash.txt > sha512crypt.hash
hashcat -m 1800 -a 0 sha512crypt.hash /usr/share/wordlists/rockyou.txt

```

```bash
# John : afficher les correspondances déjà trouvées
john --show root_hash.txt

# Hashcat : afficher les correspondances présentes dans le potfile
hashcat -m 1800 sha512crypt.hash --show

```

### Lister les fichiers SUID

<p class="oscp-command-note">Lister les fichiers SUID sans présumer qu'ils sont exploitables.</p>

```bash
find / -type f -perm -4000 2>/dev/null

```

<p class="oscp-command-note">Afficher le propriétaire et les bits de permission de chaque fichier SUID.</p>

```bash
find / -type f -perm -4000 -exec ls -l {} + 2>/dev/null

```

### Examiner les exécutables SUID

<p class="oscp-command-note">`ps -C` recherche le nom de l'exécutable, pas une sous-chaîne de sa ligne de commande.</p>

```bash
ps -u "$(id -un)" -C NOM_BINAIRE -o pid,user,euser,comm

```

<p class="oscp-command-note">La ligne `Uid` de `/proc/PID/status` contient les UID réel, effectif, sauvegardé et filesystem.</p>

```bash
grep '^Uid:' /proc/1234/status  # Remplacer 1234 par un PID existant

```

<p class="oscp-command-note">`find -exec` lance `ls -l` avec les droits du processus courant, sans privilège supplémentaire.</p>

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

## MySQL : vérifier les UDF disponibles

Les fonctions `sys_exec` et `sys_eval` nécessitent une UDF préinstallée.

<p class="oscp-command-note">Les appels `sys_exec` et `sys_eval` échouent sans UDF correspondante ; ne pas les confondre avec des fonctions natives.</p>

```sql
-- À utiliser seulement si l'UDF sys_exec existe
SELECT sys_exec('whoami');
-- À utiliser seulement si l'UDF sys_eval existe
SELECT sys_eval('whoami');

```

## Repérer les installations locales

<p class="oscp-command-note">Ces chemins sont des repères, pas des commandes à exécuter.</p>

```text
/usr/local/  # Installations locales
/usr/local/src/
/usr/local/bin/
/opt/  # Applications tierces
/home/
/var/
/usr/src/
```

<p class="oscp-command-note">Lister les paquets avec le gestionnaire de la distribution.</p>

```bash
# Debian/Ubuntu : base dpkg
dpkg -l

# Fedora/RHEL/CentOS/openSUSE : base RPM
rpm -qa

# OpenBSD : paquets installés
pkg_info

# FreeBSD : paquets installés
pkg info

```

## Examiner les fichiers sensibles accessibles

Examiner uniquement les données accessibles et utiles au périmètre autorisé.

<p class="oscp-command-note">Exemples pédagogiques de couples identifiant/mot de passe faibles ; pas de syntaxe shell.</p>

```text
root:root
username:username
username:username1  # Exemple uniquement
username:root
username:admin
username:qwerty
username:password

```

```bash
# Vérifier l'existence et les droits des boîtes aux lettres locales
ls -ld /var/mail /var/spool/mail 2>/dev/null
```

```bash
./LinEnum.sh -t -k password

```

### Vérifier les sockets TCP et UDP

<p class="oscp-command-note">`ss` affiche les sockets locales ; les noms des processus peuvent nécessiter des privilèges.</p>

```bash
# Ports TCP/UDP en écoute
ss -tulpen  # Informations étendues si disponibles
ss -tunap  # PID visibles selon les droits

```

### Identifier les fichiers KeePass

Les fichiers `.kdbx` sont chiffrés ; leur découverte ne signifie pas qu'ils sont déchiffrables.

<p class="oscp-command-note">Localiser les bases KeePass sous `/home` sans ouvrir leur contenu.</p>

```bash
find /home -type f -iname '*.kdbx' 2>/dev/null
```

### Localiser les configurations SSH utilisateur

La présence de `.ssh` ne prouve pas que les clés privées sont accessibles.

<p class="oscp-command-note">Chercher les dossiers `.ssh` dans les répertoires personnels.</p>

```bash
find /home -type d -name '.ssh' -print 2>/dev/null
```

## Dossiers accessibles en écriture ou en parcours

<p class="oscp-command-note">`-writable` teste les droits effectifs du compte ; `-perm` inspecte les bits de permission.</p>

```bash
# D'abord l'accès effectif du compte, puis les bits world-writable
find / -writable -type d 2>/dev/null
find / -perm -002 -type d 2>/dev/null
find / -perm -o=w -type d 2>/dev/null  # Équivalent à -002

# Dossiers accessibles en parcours par « autres »
find / -perm -o=x -type d 2>/dev/null

# Dossiers avec écriture et parcours pour « autres »
find / \( -perm -o=w -perm -o=x \) -type d 2>/dev/null

```

## Examiner les montages et volumes

Comparer les montages actifs aux volumes configurés dans `fstab`.

```bash
findmnt
cat /etc/fstab

```

## Fichiers SUID et SGID

Identifier les exécutables dotés de bits spéciaux, sans conclure automatiquement à une faille.

### Effet des bits SUID et SGID

Sur un exécutable, SUID applique l'UID effectif du propriétaire ; SGID applique le GID effectif du groupe. Les systèmes de fichiers `nosuid` peuvent neutraliser ces bits.

### Lister les exécutables SUID et SGID

Chercher les fichiers réguliers concernés, y compris dans les dossiers où la lecture est autorisée.

<p class="oscp-command-note">Lister séparément les fichiers SUID et SGID.</p>

```bash
# Fichiers SUID
find / -perm -u=s -type f 2>/dev/null

# Fichiers SGID
find / -perm -g=s -type f 2>/dev/null

```

### Analyser un exécutable SUID

<p class="oscp-command-note">`strings` lit le fichier ; `ltrace` exécute le programme et peut être bloqué sur un binaire SUID.</p>

```bash
# Rechercher des chaînes imprimables sans lancer le binaire
strings /path/to/suid-binary

# Tracer les appels de bibliothèque en laboratoire (exécute le binaire)
ltrace /path/to/suid-binary

# Vérifier si un programme appelle une commande sans chemin absolu.
# Préparer un exécutable de test dans un environnement isolé
printf '#!/bin/sh\nprintf "test PATH\\n"\n' > /tmp/cp
chmod +x /tmp/cp

# Préfixer PATH uniquement pour la commande de test
PATH=/tmp:$PATH /chemin/vers/programme-de-test

# La présence d'un programme dans PATH ne prouve pas une élévation de privilèges.

```

<p class="oscp-command-note">Rechercher les exécutables SUID modifiables par le compte courant.</p>

```bash
# Fichiers SUID accessibles en écriture
find / -perm -u=s -writable -type f 2>/dev/null

# Vérifier propriétaire, droits réels et options de montage avant de conclure.

```

```bash
# Vérifier les fichiers SUID dans les répertoires cron (cas inhabituel)
find /etc/cron* /var/spool/cron/ -type f -perm -u=s 2>/dev/null

```

#### Inspecter les dépendances ELF

`readelf -d` lit la section dynamique ; `NEEDED` indique les bibliothèques demandées.

<p class="oscp-command-note">Lister les entrées `NEEDED` du binaire ELF.</p>

```bash
readelf -d /chemin/vers/binaire | grep NEEDED
```

#### Tracer les accès aux fichiers

`strace` lance réellement le programme. Le traçage d'un exécutable SUID peut modifier son comportement ou être refusé.

<p class="oscp-command-note">Observer les accès aux fichiers et les erreurs `ENOENT` en laboratoire.</p>

```bash
strace -f -e trace=file /chemin/vers/programme-de-test 2>&1 | grep -Ei 'ENOENT|openat|access'
```

#### Rechercher des chemins dans un binaire

`strings` peut révéler des chemins ou noms de fonctions ; ces indices ne prouvent pas qu'ils sont utilisés.

<p class="oscp-command-note">Filtrer les chaînes lisibles pour repérer chemins et appels potentiels.</p>

```bash
strings /chemin/vers/binaire | grep -Ei '(/bin/|/usr/|system|exec|sh )'
```

### LinPEAS

Exécuter le script seulement après avoir vérifié sa provenance et ses permissions.

```bash
bash ./linpeas.sh | tee linpeas_output.txt

```

<p class="oscp-command-note">Convertir le rapport LinPEAS avec les scripts `peas2json.py`, `json2html.py` et `json2pdf.py` s'ils sont installés.</p>

```bash
# Exécuter les conversions sur la machine d'analyse où les scripts sont installés.

# Transformer le rapport texte en JSON.
python3 peas2json.py ./linpeas_output.txt peass.json

# Produire une version HTML du rapport JSON.
python3 json2html.py peass.json peass.html

# Facultatif : convertir également le rapport au format PDF.
python3 json2pdf.py peass.json peass.pdf

```

### LinEnum

Le script doit être présent localement ; certaines vérifications demandent des droits supplémentaires.

<p class="oscp-command-note">LinEnum : lancer l'inventaire standard ou une recherche approfondie par mot-clé.</p>

```bash
./LinEnum.sh

# Chercher les occurrences du mot « password »
./LinEnum.sh -t -k password

```

```bash
bash ./LinEnum.sh | tee linenum_output.txt

```

### Unix-privesc-check

Vérifier la compatibilité du script avec la machine cible avant exécution.

```bash
./unix-privesc-check.sh | tee unix_privesc_check_output.txt

```

### Checksec

Outil de contrôle des protections des exécutables, si installé.

```bash
checksec --all

```

### Peepdf

Analyseur de fichiers PDF, distinct des outils d'élévation de privilèges Linux.

```bash
peepdf.py file.pdf

```

### Recherche de vulnérabilités potentielles

<p class="oscp-command-note">Le nom `exploit-suggester.py` ne garantit ni sa provenance ni sa compatibilité ; vérifier son aide avant usage.</p>

```bash
python3 exploit-suggester.py --help

```

## Contrôles complémentaires en lecture seule

Ces vérifications aident à repérer les permissions risquées ; elles ne démontrent pas une élévation possible.

### Identifier les dossiers world-writable

Le bit d'écriture « autres » permet potentiellement la création de fichiers ; vérifier aussi les droits de parcours et le sticky bit.

<p class="oscp-command-note">Dossiers dont le bit d'écriture « autres » est actif.</p>

```bash
find / -type d -perm -0002 -print 2>/dev/null  # Vérifier aussi le sticky bit
```

### Contrôle croisé SUID et SGID

Repérer les fichiers avec les bits spéciaux, sans les exécuter.

<p class="oscp-command-note">Fichiers portant les bits SUID ou SGID.</p>

```bash
find / -type f -perm -4000 2>/dev/null  # SUID
find / -type f -perm -2000 2>/dev/null  # SGID
```

### Consulter les dernières traces cron

Sur Debian/Ubuntu, les événements cron peuvent être dans syslog ; sinon consulter `journalctl` si disponible.

```bash
grep -i 'cron' /var/log/syslog 2>/dev/null | tail -n 30
```

### Examiner les exports NFS du serveur

`/etc/exports` décrit les partages NFS ; les fichiers de `/etc/exports.d/` peuvent compléter la configuration.

```bash
cat /etc/exports 2>/dev/null
```

[Journal de cron](https://manpages.debian.org/trixie/cron/cron.8.en.html) · [Configuration des exports NFS](https://manpages.debian.org/trixie/nfs-kernel-server/exports.5.en.html).

**Référence complémentaire :** [Notes de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/16_linux_privesc.md). Explications rédigées pour SKILL-ISSUE.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
