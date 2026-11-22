---
title: "OSCP · Transferts de fichiers"
description: "Copier un fichier entre Linux et Windows, depuis la machine qui l’envoie ou celle qui le reçoit."
---

# Transferts de fichiers

La **source** possède le fichier, la **destination** le reçoit. Adapte les adresses et les comptes. Les exemples utilisent `rapport.txt` dans le dossier courant sous Linux et dans `C:\Users\Public` sous Windows.

| Machine d’exemple | Adresse |
| --- | --- |
| Kali | `10.10.14.10` |
| Second Linux | `10.10.10.20` |
| Windows distant | `10.10.10.30` |

<TransferSelector />

## Vérifier la connexion

### Afficher les adresses et les routes de Kali

```bash
ip -br address
ip route
```

### Depuis Kali, tester SSH ou SMB

Teste uniquement le port du service que tu comptes utiliser.

```bash
nc -zv 10.10.10.20 22
nc -zv 10.10.10.30 445
```

### Depuis Windows, tester le port HTTP de Kali

`TcpTestSucceeded` indique si PowerShell a pu ouvrir la connexion TCP.

```powershell
Test-NetConnection 10.10.14.10 -Port 8000
```

## Linux vers Linux

### Depuis la source, envoyer un fichier par SCP {#ll-scp}

Le serveur SSH/SFTP distant doit être joignable et le compte `etudiant` doit pouvoir écrire dans `/tmp`.

```bash
scp ./rapport.txt etudiant@10.10.10.20:/tmp/
```

### Depuis la destination, récupérer un fichier par SCP {#ll-scp-reception}

Ici, `10.10.10.20` possède déjà le fichier et le Linux qui exécute la commande le reçoit.

```bash
scp etudiant@10.10.10.20:/tmp/rapport.txt ./rapport.txt
```

### Depuis la source, envoyer un dossier par SCP {#ll-scp-dossier}

```bash
scp -r ./dossier etudiant@10.10.10.20:/tmp/
```

### Depuis la source, synchroniser un dossier avec rsync {#ll-rsync}

Installe `rsync` des deux côtés. La barre finale de `./dossier/` copie son contenu.

```bash
rsync -avP ./dossier/ etudiant@10.10.10.20:/tmp/dossier/
```

### Depuis Linux, ouvrir une session SFTP {#ll-sftp}

```bash
sftp etudiant@10.10.10.20
```

### Dans SFTP, envoyer et récupérer un fichier

`put` envoie le fichier local et `get` récupère un fichier déjà présent dans le dossier distant.

```text
put rapport.txt
get autre_fichier.txt
bye
```

### Depuis la destination, télécharger par HTTP {#ll-http}

[Ouvre le serveur HTTP sur le Linux source](#http-source), puis télécharge le fichier sur le second Linux.

```bash
curl --fail --show-error --location --output ./rapport.txt http://10.10.14.10:8000/rapport.txt
```

### Sur la destination, recevoir avec Netcat {#ll-netcat}

Avec `netcat-openbsd` sur un réseau isolé, démarre cette écoute avant l’envoi. Le fichier local est écrasé et le transfert circule en clair.

```bash
nc -l 9001 > ./rapport.txt
```

### Depuis la source, envoyer avec Netcat

`-N` ferme le flux réseau à la fin du fichier.

```bash
nc -N 10.10.10.20 9001 < ./rapport.txt
```

## Linux vers Windows

### Sur Kali, servir le fichier par HTTP {#http-source}

Laisse le terminal ouvert pendant le téléchargement. Seul le contenu de `partage` doit être destiné au réseau de test.

```bash
mkdir -p ./partage
cp ./rapport.txt ./partage/
python3 -m http.server 8000 --bind 10.10.14.10 --directory ./partage
```

### Depuis Windows, télécharger avec PowerShell {#lw-http-ps}

[Démarre le serveur HTTP de Kali](#http-source) avant la copie.

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://10.10.14.10:8000/rapport.txt' -OutFile 'C:\Users\Public\rapport.txt'
```

### Depuis Windows, télécharger avec curl.exe {#lw-http-curl}

Cette variante utilise le même serveur HTTP et fonctionne dans PowerShell ou CMD.

```bat
curl.exe --fail --location --output "C:\Users\Public\rapport.txt" "http://10.10.14.10:8000/rapport.txt"
```

### Sur Kali, partager le fichier par SMB {#lw-smb-kali}

Le serveur SMB d’Impacket demande le mot de passe du compte temporaire `audit`. Le port 445 doit être libre.

```bash
mkdir -p ./partage
cp ./rapport.txt ./partage/
sudo impacket-smbserver -ip 10.10.14.10 -smb2support -username audit partage ./partage
```

### Depuis Windows, récupérer le fichier du partage Kali

Dans PowerShell, saisis le même mot de passe à l’invite de `net use`.

```powershell
net use \\10.10.14.10\partage * /user:audit
Copy-Item -LiteralPath '\\10.10.14.10\partage\rapport.txt' -Destination 'C:\Users\Public\rapport.txt'
net use \\10.10.14.10\partage /delete
```

### Depuis Linux, déposer le fichier sur un partage Windows {#lw-smb-windows}

Le compte `LAB\etudiant` doit pouvoir écrire dans le partage `Depot` et dans son dossier Windows.

```bash
smbclient //10.10.10.30/Depot -U 'LAB/etudiant' -c 'put rapport.txt rapport.txt'
```

### Depuis Linux, envoyer le fichier à Windows par SCP {#lw-scp}

OpenSSH Server doit être actif sur Windows. Le chemin après `:` est relatif au dossier de connexion du compte distant.

```bash
scp ./rapport.txt etudiant@10.10.10.30:rapport.txt
```

## Windows vers Linux

### Sur Kali, ouvrir un partage SMB de réception {#wl-smb-kali}

Laisse le serveur ouvert pendant la copie. Impacket demande le mot de passe temporaire de `audit`.

```bash
mkdir -p ./reception
sudo impacket-smbserver -ip 10.10.14.10 -smb2support -username audit partage ./reception
```

### Depuis Windows, déposer le fichier dans le partage Kali

Le fichier arrive dans `./reception/rapport.txt` sur Kali.

```powershell
net use \\10.10.14.10\partage * /user:audit
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\10.10.14.10\partage\rapport.txt'
net use \\10.10.14.10\partage /delete
```

### Sur Kali, ouvrir un dossier de réception WebDAV {#wl-webdav}

WsgiDAV et Cheroot doivent être installés. Cet exemple autorise l’écriture anonyme en clair sur un réseau isolé.

```bash
mkdir -p ./reception
wsgidav --no-config --host 10.10.14.10 --port 8080 --root ./reception --auth anonymous
```

### Depuis Windows, déposer le fichier par WebDAV

```bat
curl.exe --fail --upload-file "C:\Users\Public\rapport.txt" "http://10.10.14.10:8080/rapport.txt"
```

### Depuis Windows, envoyer le fichier à Kali par SCP {#wl-scp}

Il faut le client OpenSSH sur Windows, le serveur SSH/SFTP sur Kali et un compte pouvant écrire dans `/tmp`.

```powershell
scp 'C:\Users\Public\rapport.txt' kali@10.10.14.10:/tmp/rapport.txt
```

### Depuis Linux, récupérer le fichier d’un partage Windows {#wl-smb-windows}

Le fichier doit déjà se trouver sur le partage `Depot` et le compte doit pouvoir le lire.

```bash
smbclient //10.10.10.30/Depot -U 'LAB/etudiant' -c 'get rapport.txt rapport.txt'
```

## Windows vers Windows

### Sur la destination, créer le partage SMB {#ww-creer}

PowerShell administrateur. Cette étape est utile si `Depot` n’existe pas encore. Le compte doit aussi disposer du droit d’écriture NTFS.

```powershell
New-Item -ItemType Directory -Path 'C:\Depot' -Force
New-SmbShare -Name 'Depot' -Path 'C:\Depot' -ChangeAccess 'LAB\etudiant'
```

### Depuis la source, copier vers le partage SMB {#ww-smb}

Le compte utilisé par PowerShell doit pouvoir écrire sur `\\10.10.10.30\Depot`.

```powershell
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\10.10.10.30\Depot\rapport.txt'
```

### Depuis la source, envoyer le fichier par SCP {#ww-scp}

Le client OpenSSH s’exécute sur le premier Windows. Le serveur OpenSSH du second reçoit le fichier dans le dossier de connexion de `etudiant`.

```powershell
scp 'C:\Users\Public\rapport.txt' etudiant@10.10.10.30:rapport.txt
```

## Dossier partagé dans une session RDP

### Depuis Kali, ouvrir la session avec un dossier partagé {#rdp}

FreeRDP 3 et la redirection de lecteurs doivent être disponibles. Place dans `partage` les fichiers à envoyer.

```bash
mkdir -p ./partage
xfreerdp3 /v:10.10.10.30 /u:etudiant /dynamic-resolution "/drive:partage,$PWD/partage"
```

### Dans Windows, afficher le dossier de Kali

```powershell
Get-ChildItem -LiteralPath '\\tsclient\partage'
```

### Dans Windows, copier de Kali vers Windows

```powershell
Copy-Item -LiteralPath '\\tsclient\partage\rapport.txt' -Destination 'C:\Users\Public\rapport.txt'
```

### Dans Windows, copier de Windows vers Kali

```powershell
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\tsclient\partage\retour.txt'
```

## FTP sur un serveur existant

FTP transmet les identifiants et le fichier en clair. Utilise ici un compte de test sur un réseau isolé.

### Depuis Linux, télécharger par FTP

```bash
curl --fail --user etudiant --output ./rapport.txt ftp://10.10.10.20/rapport.txt
```

### Depuis Linux, envoyer par FTP

Le compte FTP doit pouvoir écrire dans le dossier distant.

```bash
curl --fail --user etudiant --upload-file ./rapport.txt ftp://10.10.10.20/rapport.txt
```

## Transférer un petit fichier sous forme de texte

Base64 représente les octets sous forme de texte. Copie toute la chaîne et compare les empreintes après décodage.

### Sur Linux source, encoder en Base64

```bash
base64 -w 0 ./rapport.txt
```

### Sur Windows destination, décoder la chaîne copiée

```powershell
[IO.File]::WriteAllBytes('C:\Users\Public\rapport.txt', [Convert]::FromBase64String((Read-Host 'Base64')))
```

### Sur Windows source, encoder en Base64

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\Users\Public\rapport.txt'))
```

### Sur Linux destination, décoder la chaîne copiée

```bash
read -r -p 'Base64 : ' contenu
printf '%s' "$contenu" | base64 --decode > ./rapport.txt
```

## Comparer les empreintes SHA-256

Calcule l’empreinte du fichier source puis celle du fichier reçu. Ignore la différence entre majuscules et minuscules lors de la comparaison.

### Sous Linux

```bash
sha256sum ./rapport.txt
```

### Sous Windows avec PowerShell

```powershell
Get-FileHash -LiteralPath 'C:\Users\Public\rapport.txt' -Algorithm SHA256
```

## Dépannage

| Symptôme | À vérifier |
| --- | --- |
| Connexion refusée ou expirée | Adresse, port d’écoute, route et pare-feu. |
| HTTP 404 | Nom du fichier et dossier servi par Python. |
| HTTP 501 pendant un envoi | Le serveur `http.server` de Python sert les fichiers en lecture. Pour recevoir, utilise le serveur WebDAV. |
| SMB refuse la copie | Compte, droits du partage et droits du dossier. |
| Empreintes différentes | Chemins source et destination, intégralité de la copie. |

## Sources

[OpenSSH](https://man.openbsd.org/scp) · [SFTP](https://man.openbsd.org/sftp) · [OpenSSH pour Windows](https://learn.microsoft.com/fr-fr/windows-server/administration/openssh/openssh-overview) · [rsync](https://rsync.samba.org/ftp/rsync/rsync.1.html) · [Netcat OpenBSD](https://man.openbsd.org/nc) · [curl](https://curl.se/docs/manpage.html) · [Serveur HTTP Python](https://docs.python.org/3/library/http.server.html).

[Client Samba](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html) · [Serveur SMB d’Impacket](https://github.com/fortra/impacket/blob/master/examples/smbserver.py) · [Partages Windows](https://learn.microsoft.com/powershell/module/smbshare/new-smbshare) · [Copie PowerShell](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/copy-item) · [WsgiDAV](https://wsgidav.readthedocs.io/en/latest/user_guide_cli.html) · [FreeRDP 3](https://manpages.debian.org/trixie/freerdp3-x11/xfreerdp3.1.en.html).

Sources d’origine : [notes de krovs](https://github.com/krovs/oscp-notes/tree/main/docs) et [guide d’Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).
