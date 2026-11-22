---
title: "OSCP · Transferts de fichiers"
description: "Copier un fichier entre Linux et Windows, depuis la machine qui l’envoie ou celle qui le reçoit."
---

# Transferts de fichiers

La **source** possède le fichier, la **destination** le reçoit. Exécute chaque commande sur la machine indiquée et adapte les adresses et les comptes. Les exemples utilisent `rapport.txt` dans le dossier courant sous Linux et dans `C:\Users\Public` sous Windows.

| Machine d’exemple | Adresse |
| --- | --- |
| Kali | `10.10.14.10` |
| Second Linux | `10.10.10.20` |
| Windows distant | `10.10.10.30` |

Pour les transferts **Windows vers Windows**, l'adresse `10.10.10.30` représente le Windows **destination** ; le Windows source est un autre poste disposant du fichier.

<TransferSelector />

## Vérifier la connexion

### Afficher les adresses et les routes de Kali

```bash
ip -br address
ip route
```

### Sur Kali, vérifier l'accès TCP aux services SSH et SMB

`nc -zv` teste l'ouverture TCP sans transférer de fichier. Teste uniquement le service nécessaire.

```bash
nc -zv 10.10.10.20 22
nc -zv 10.10.10.30 445
```

### Depuis Windows, tester le port HTTP de Kali

`TcpTestSucceeded : True` confirme la connexion TCP, pas les droits de téléchargement HTTP.

```powershell
Test-NetConnection 10.10.14.10 -Port 8000
```

## Linux vers Linux

### Sur Kali, envoyer un fichier au second Linux par SCP {#ll-scp}

À exécuter sur Kali (`10.10.14.10`), source du fichier. Le serveur SSH du second Linux (`10.10.10.20`) doit être accessible et `etudiant` doit pouvoir écrire dans `/tmp`.

```bash
scp ./rapport.txt etudiant@10.10.10.20:/tmp/
```

### Sur Kali, récupérer un fichier du second Linux par SCP {#ll-scp-reception}

À exécuter sur Kali (`10.10.14.10`), qui reçoit le fichier. Le Linux distant (`10.10.10.20`) possède `/tmp/rapport.txt` et doit autoriser la connexion SSH.

```bash
scp etudiant@10.10.10.20:/tmp/rapport.txt ./rapport.txt
```

### Sur Kali, envoyer un dossier complet au second Linux par SCP {#ll-scp-dossier}

Le dossier `./dossier` doit exister sur Kali ; `-r` copie récursivement son contenu vers `/tmp/dossier` sur le second Linux.

```bash
scp -r ./dossier etudiant@10.10.10.20:/tmp/
```

### Sur Kali, synchroniser un dossier vers le second Linux avec rsync {#ll-rsync}

`rsync` doit être installé sur Kali et le second Linux, avec SSH accessible. Le `/` final de `./dossier/` copie son contenu dans `/tmp/dossier/` ; `-P` affiche la progression et conserve les transferts partiels.

```bash
rsync -avP ./dossier/ etudiant@10.10.10.20:/tmp/dossier/
```

### Sur Kali, ouvrir une session SFTP vers le second Linux {#ll-sftp}

Le serveur SSH/SFTP doit être actif sur `10.10.10.20` ; la connexion demande l'authentification du compte `etudiant`.

```bash
sftp etudiant@10.10.10.20
```

### Dans SFTP, envoyer et récupérer un fichier

Le répertoire local est celui d'où `sftp` a été lancé ; le répertoire distant dépend du compte SSH. Vérifier les chemins avec `lpwd` et `pwd` avant le transfert.

À saisir dans l'invite `sftp>` : `put` envoie un fichier local et `get` récupère un fichier distant. Ce ne sont pas des commandes Bash.

```text
lpwd
pwd
put rapport.txt
get autre_fichier.txt
bye
```

### Sur le second Linux, télécharger le fichier HTTP servi par Kali {#ll-http}

Démarre le serveur HTTP sur Kali (`10.10.14.10`) avec [la commande dédiée](#http-source), puis exécute `curl` sur le second Linux (`10.10.10.20`). Le port 8000 doit être joignable depuis ce dernier.

```bash
curl --fail --show-error --location --output ./rapport.txt http://10.10.14.10:8000/rapport.txt
```

### Sur le second Linux, recevoir un fichier de Kali avec Netcat {#ll-netcat}

Sur le second Linux (`10.10.10.20`), lancer `nc -l 9001` **avant** l'envoi depuis Kali. La redirection `>` écrase `./rapport.txt` s'il existe ; ce transfert TCP n'est ni chiffré ni authentifié.

```bash
nc -l 9001 > ./rapport.txt
```

### Sur Kali, envoyer un fichier au second Linux avec Netcat

Sur Kali (`10.10.14.10`), envoyer `./rapport.txt` vers l'écoute TCP 9001 du second Linux. Avec `netcat-openbsd`, `-N` ferme la connexion après la fin de l'entrée standard ; vérifier ensuite l'empreinte du fichier reçu.

```bash
nc -N 10.10.10.20 9001 < ./rapport.txt
```

## Linux vers Windows

### Sur Kali, servir le fichier par HTTP {#http-source}

La commande `python3 -m http.server` sert les fichiers en lecture seule, sans authentification ni TLS. L'interface `10.10.14.10` doit exister sur Kali.

Sur Kali source, laisse ce serveur HTTP ouvert pendant la copie. Le contenu de `partage` est accessible sans authentification sur le réseau de test.

```bash
mkdir -p ./partage
cp ./rapport.txt ./partage/
python3 -m http.server 8000 --bind 10.10.14.10 --directory ./partage
```

### Sur Windows, télécharger le fichier HTTP de Kali avec PowerShell {#lw-http-ps}

L'URL pointe vers Kali (`10.10.14.10`) ; `-OutFile` désigne le chemin local du fichier **sur Windows**.

Sur Windows destination, [démarre d'abord le serveur HTTP de Kali](#http-source). Le dossier `C:\Users\Public` doit exister.

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://10.10.14.10:8000/rapport.txt' -OutFile 'C:\Users\Public\rapport.txt'
```

### Sur Windows, télécharger le fichier HTTP de Kali avec curl.exe {#lw-http-curl}

`curl.exe` évite la confusion avec l'ancien alias PowerShell `curl` ; `--output` écrit le fichier sur le Windows qui lance la commande.

Cette variante utilise `curl.exe` natif sous Windows, depuis PowerShell ou CMD ; `--fail` fait échouer la commande sur une erreur HTTP.

```bat
curl.exe --fail --location --output "C:\Users\Public\rapport.txt" "http://10.10.14.10:8000/rapport.txt"
```

### Sur Kali, partager le fichier par SMB {#lw-smb-kali}

Sur Kali, installer le serveur SMB d'Impacket et vérifier que TCP 445 est libre. Le mot de passe `MotDePasseTemporaire` est un exemple à remplacer ; l'authentification SMB ne chiffre pas nécessairement le contenu des fichiers.

```bash
mkdir -p ./partage
cp ./rapport.txt ./partage/
sudo impacket-smbserver -ip 10.10.14.10 -smb2support -username audit -password 'MotDePasseTemporaire' partage ./partage
```

### Sur Windows, récupérer le fichier du partage SMB de Kali

Sur Windows destination, `net use` demande le mot de passe SMB ; `Copy-Item` lit ensuite le partage Kali. Ferme la connexion après la copie.

```powershell
net use \\10.10.14.10\partage * /user:audit
Copy-Item -LiteralPath '\\10.10.14.10\partage\rapport.txt' -Destination 'C:\Users\Public\rapport.txt'
net use \\10.10.14.10\partage /delete
```

### Sur Kali, envoyer le fichier vers un partage SMB Windows {#lw-smb-windows}

Sur Kali source, `smbclient put` envoie `./rapport.txt` au partage `Depot` de Windows (`10.10.10.30`). Le compte `LAB\etudiant` doit avoir les droits SMB et NTFS d'écriture ; le client demandera son mot de passe.

```bash
smbclient //10.10.10.30/Depot -U 'LAB/etudiant' -c 'put rapport.txt rapport.txt'
```

### Sur Kali, envoyer le fichier à Windows par SCP {#lw-scp}

Sur Kali source, `scp` transfère le fichier au compte `etudiant` sur Windows (`10.10.10.30`). OpenSSH Server doit être actif ; le chemin `rapport.txt` après `:` est relatif au répertoire distant de connexion.

```bash
scp ./rapport.txt etudiant@10.10.10.30:rapport.txt
```

## Windows vers Linux

### Sur Kali, ouvrir un partage SMB de réception {#wl-smb-kali}

Le nom du partage exposé aux clients Windows est `partage` ; son répertoire réel sur Kali est `./reception`.

Sur Kali destination, créer `./reception` avec les permissions d'écriture nécessaires, puis garder Impacket actif pendant la copie. Employer des identifiants temporaires et arrêter le serveur après le test.

```bash
mkdir -p ./reception
sudo impacket-smbserver -ip 10.10.14.10 -smb2support -username audit -password 'MotDePasseTemporaire' partage ./reception
```

### Sur Windows source, envoyer un fichier au partage SMB de Kali

Sur Windows source, `Copy-Item` dépose le fichier dans `./reception/rapport.txt` sur Kali. Le partage Impacket et le répertoire Linux doivent autoriser l'écriture ; `net use` demande le mot de passe.

```powershell
net use \\10.10.14.10\partage * /user:audit
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\10.10.14.10\partage\rapport.txt'
net use \\10.10.14.10\partage /delete
```

### Sur Kali, ouvrir un dossier de réception WebDAV {#wl-webdav}

Le serveur doit rester actif pendant l'envoi depuis Windows. Le fichier reçu doit apparaître dans `./reception/rapport.txt` sur Kali.

Sur Kali destination, installer WsgiDAV et son serveur HTTP Cheroot. Cette configuration accepte des écritures WebDAV anonymes **sans chiffrement** : uniquement en laboratoire isolé, puis arrêter le service.

```bash
mkdir -p ./reception
wsgidav --no-config --host 10.10.14.10 --port 8080 --root ./reception --auth anonymous
```

### Sur Windows source, déposer le fichier sur Kali via WebDAV

`curl.exe --upload-file` envoie le contenu par requête HTTP PUT ; cette méthode nécessite un serveur WebDAV acceptant l'écriture, pas le serveur HTTP Python standard.

```bat
curl.exe --fail --upload-file "C:\Users\Public\rapport.txt" "http://10.10.14.10:8080/rapport.txt"
```

### Sur Windows source, envoyer le fichier à Kali par SCP {#wl-scp}

Le chemin avant `kali@` est local à Windows ; `/tmp/rapport.txt` est le chemin du fichier reçu **sur Kali**.

À exécuter sur Windows source : client OpenSSH disponible, serveur SSH sur Kali destination et compte `kali` autorisé à écrire dans `/tmp`.

```powershell
scp 'C:\Users\Public\rapport.txt' kali@10.10.14.10:/tmp/rapport.txt
```

### Sur Kali, récupérer un fichier du partage Windows par SMB {#wl-smb-windows}

À exécuter sur Kali, destination du fichier : `smbclient get` télécharge `rapport.txt` du partage `Depot` sur Windows (`10.10.10.30`) dans le dossier courant de Kali.

```bash
smbclient //10.10.10.30/Depot -U 'LAB/etudiant' -c 'get rapport.txt rapport.txt'
```

## Windows vers Windows

### Sur Windows destination, créer un partage SMB {#ww-creer}

Sur Windows destination (`10.10.10.30`), ouvrir PowerShell en administrateur pour créer le partage `Depot` s'il n'existe pas. Le compte `LAB\etudiant` doit exister et disposer également des droits NTFS d'écriture sur `C:\Depot`.

```powershell
New-Item -ItemType Directory -Path 'C:\Depot' -Force
New-SmbShare -Name 'Depot' -Path 'C:\Depot' -ChangeAccess 'LAB\etudiant'
```

### Sur Windows source, copier vers le partage SMB du Windows destination {#ww-smb}

Le chemin UNC `\\10.10.10.30\Depot\rapport.txt` désigne le fichier distant ; le chemin `C:\Users\Public\rapport.txt` désigne la source locale.

Sur Windows source, le compte courant doit avoir les permissions SMB et NTFS d'écriture sur `\\10.10.10.30\Depot`.

```powershell
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\10.10.10.30\Depot\rapport.txt'
```

### Sur Windows source, envoyer par SCP au Windows destination {#ww-scp}

Le chemin local `C:\Users\Public\rapport.txt` est lu sur Windows source ; le nom après `:` est créé dans le répertoire distant du compte SSH.

Sur Windows source, utiliser le client OpenSSH ; le Windows destination (`10.10.10.30`) doit exécuter OpenSSH Server et permettre au compte `etudiant` d'écrire dans son répertoire de connexion.

```powershell
scp 'C:\Users\Public\rapport.txt' etudiant@10.10.10.30:rapport.txt
```

## Dossier partagé dans une session RDP

### Sur Kali, ouvrir RDP avec redirection du dossier local {#rdp}

Sur Kali, installer FreeRDP 3 et préparer `./partage`. Le serveur Windows doit autoriser la redirection des lecteurs RDP ; le compte `etudiant` doit être autorisé à ouvrir une session RDP.

```bash
mkdir -p ./partage
xfreerdp3 /v:10.10.10.30 /u:etudiant /dynamic-resolution "/drive:partage,$PWD/partage"
```

### Sur Windows distant, afficher le dossier Kali redirigé par RDP

```powershell
Get-ChildItem -LiteralPath '\\tsclient\partage'
```

### Sur Windows distant, récupérer un fichier du dossier Kali redirigé

```powershell
Copy-Item -LiteralPath '\\tsclient\partage\rapport.txt' -Destination 'C:\Users\Public\rapport.txt'
```

### Sur Windows distant, renvoyer un fichier dans le dossier Kali redirigé

```powershell
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\tsclient\partage\retour.txt'
```

## FTP sur un serveur existant

FTP classique transmet les identifiants et les fichiers en clair. Ces commandes utilisent un compte `etudiant` sur un serveur FTP existant ; l'accès FTP anonyme, s'il est autorisé, est un cas distinct. Préférer SFTP hors laboratoire isolé.

### Sur Kali, télécharger un fichier depuis le serveur FTP distant

`--user etudiant` utilise le compte FTP et demande son mot de passe si nécessaire ; `--output` écrit le fichier localement sur Kali.

```bash
curl --fail --user etudiant --output ./rapport.txt ftp://10.10.10.20/rapport.txt
```

### Sur Kali, envoyer un fichier vers le serveur FTP distant

`--upload-file` lit `./rapport.txt` sur Kali et l'envoie vers le chemin FTP distant. Vérifier les droits d'écriture du compte avant l'essai.

Le serveur FTP doit accepter l'upload et le compte `etudiant` doit disposer des droits d'écriture dans le répertoire distant.

```bash
curl --fail --user etudiant --upload-file ./rapport.txt ftp://10.10.10.20/rapport.txt
```

## Transférer un petit fichier sous forme de texte

Base64 représente les octets sous forme de texte **sans chiffrement**. Réserver cette méthode aux petits fichiers, copier la chaîne complète sans caractères supplémentaires et comparer les empreintes SHA-256 après reconstruction.

### Sur Kali source, encoder un fichier en Base64 pour Windows

```bash
base64 -w 0 ./rapport.txt
```

### Sur Windows destination, reconstruire le fichier depuis Base64

```powershell
[IO.File]::WriteAllBytes('C:\Users\Public\rapport.txt', [Convert]::FromBase64String((Read-Host 'Base64')))
```

### Sur Windows source, encoder un fichier en Base64 pour Linux

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\Users\Public\rapport.txt'))
```

### Sur Kali destination, reconstruire le fichier depuis Base64

```bash
read -r -p 'Base64 : ' contenu
printf '%s' "$contenu" | base64 --decode > ./rapport.txt
```

## Comparer les empreintes SHA-256

Calcule l’empreinte du fichier source puis celle du fichier reçu. Ignore la différence entre majuscules et minuscules lors de la comparaison.

### Sur Linux source et destination

Exécuter la commande sur chaque machine en adaptant le chemin du fichier, puis comparer les deux empreintes SHA-256.

```bash
sha256sum ./rapport.txt
```

### Sur Windows source et destination avec PowerShell

Exécuter sur chaque machine concernée ; le champ `Hash` doit correspondre à l'empreinte calculée sur Linux ou Windows pour le même fichier.

```powershell
Get-FileHash -LiteralPath 'C:\Users\Public\rapport.txt' -Algorithm SHA256
```

## Dépannage

| Symptôme | À vérifier |
| --- | --- |
| Connexion refusée ou expirée | Adresse, port d’écoute, route et pare-feu. |
| HTTP 404 | Nom du fichier et dossier servi par Python. |
| HTTP 501 pendant un envoi | `python3 -m http.server` ne prend pas en charge PUT ; pour recevoir un fichier, démarrer un serveur WebDAV configuré pour l'écriture. |
| SMB refuse la copie | Authentification, permissions du partage, droits NTFS (Windows) ou permissions du répertoire (Linux), et port TCP 445. |
| Empreintes différentes | Vérifier les chemins, la taille et l'intégrité du fichier ; ne pas considérer le transfert comme validé. |

## Sources

[OpenSSH](https://man.openbsd.org/scp) · [SFTP](https://man.openbsd.org/sftp) · [OpenSSH pour Windows](https://learn.microsoft.com/fr-fr/windows-server/administration/openssh/openssh-overview) · [rsync](https://rsync.samba.org/ftp/rsync/rsync.1.html) · [Netcat OpenBSD](https://man.openbsd.org/nc) · [curl](https://curl.se/docs/manpage.html) · [Serveur HTTP Python](https://docs.python.org/3/library/http.server.html).

[Client Samba](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html) · [Serveur SMB d’Impacket](https://github.com/fortra/impacket/blob/master/examples/smbserver.py) · [Partages Windows](https://learn.microsoft.com/powershell/module/smbshare/new-smbshare) · [Copie PowerShell](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/copy-item) · [WsgiDAV](https://wsgidav.readthedocs.io/en/latest/user_guide_cli.html) · [FreeRDP 3](https://manpages.debian.org/trixie/freerdp3-x11/xfreerdp3.1.en.html).

Sources d’origine : [notes de krovs](https://github.com/krovs/oscp-notes/tree/main/docs) et [guide d’Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).
