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

<TransferSelector />

## Vérifier la connexion

### Afficher les adresses et les routes de Kali

```bash
ip -br address
ip route
```

### Depuis Kali, vérifier les ports SSH et SMB

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

```bash
scp -r ./dossier etudiant@10.10.10.20:/tmp/
```

### Sur Kali, synchroniser un dossier vers le second Linux avec rsync {#ll-rsync}

`rsync` doit être installé sur Kali et le second Linux, avec SSH accessible. Le `/` final de `./dossier/` copie son contenu dans `/tmp/dossier/` ; `-P` affiche la progression et conserve les transferts partiels.

```bash
rsync -avP ./dossier/ etudiant@10.10.10.20:/tmp/dossier/
```

### Sur Kali, ouvrir une session SFTP vers le second Linux {#ll-sftp}

```bash
sftp etudiant@10.10.10.20
```

### Dans SFTP, envoyer et récupérer un fichier

À saisir dans l'invite `sftp>` : `put` envoie un fichier local et `get` récupère un fichier distant. Ce ne sont pas des commandes Bash.

```text
put rapport.txt
get autre_fichier.txt
bye
```

### Sur le second Linux, télécharger le fichier HTTP servi par Kali {#ll-http}

Démarre le serveur HTTP sur Kali (`10.10.14.10`) avec [la commande dédiée](#http-source), puis exécute `curl` sur le second Linux (`10.10.10.20`). Le port 8000 doit être joignable depuis ce dernier.

```bash
curl --fail --show-error --location --output ./rapport.txt http://10.10.14.10:8000/rapport.txt
```

### Sur la destination, recevoir avec Netcat {#ll-netcat}

Avec `netcat-openbsd`, démarre l'écoute sur Linux destination avant l'envoi. `>` écrase le fichier existant ; le transfert est en clair.

```bash
nc -l 9001 > ./rapport.txt
```

### Depuis la source, envoyer avec Netcat

Avec `netcat-openbsd`, `-N` ferme le flux réseau après la fin de l'entrée standard ; exécuter sur Linux source.

```bash
nc -N 10.10.10.20 9001 < ./rapport.txt
```

## Linux vers Windows

### Sur Kali, servir le fichier par HTTP {#http-source}

Sur Kali source, laisse ce serveur HTTP ouvert pendant la copie. Le contenu de `partage` est accessible sans authentification sur le réseau de test.

```bash
mkdir -p ./partage
cp ./rapport.txt ./partage/
python3 -m http.server 8000 --bind 10.10.14.10 --directory ./partage
```

### Depuis Windows, télécharger avec PowerShell {#lw-http-ps}

Sur Windows destination, [démarre d'abord le serveur HTTP de Kali](#http-source). Le dossier `C:\Users\Public` doit exister.

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://10.10.14.10:8000/rapport.txt' -OutFile 'C:\Users\Public\rapport.txt'
```

### Depuis Windows, télécharger avec curl.exe {#lw-http-curl}

Cette variante utilise `curl.exe` natif sous Windows, depuis PowerShell ou CMD ; `--fail` fait échouer la commande sur une erreur HTTP.

```bat
curl.exe --fail --location --output "C:\Users\Public\rapport.txt" "http://10.10.14.10:8000/rapport.txt"
```

### Sur Kali, partager le fichier par SMB {#lw-smb-kali}

Sur Kali, Impacket SMB doit être installé et le port TCP 445 libre. Définis un mot de passe de laboratoire pour le compte `audit` avant le démarrage.

```bash
mkdir -p ./partage
cp ./rapport.txt ./partage/
sudo impacket-smbserver -ip 10.10.14.10 -smb2support -username audit -password 'MotDePasseTemporaire' partage ./partage
```

### Depuis Windows, récupérer le fichier du partage Kali

Sur Windows destination, `net use` demande le mot de passe SMB ; `Copy-Item` lit ensuite le partage Kali. Ferme la connexion après la copie.

```powershell
net use \\10.10.14.10\partage * /user:audit
Copy-Item -LiteralPath '\\10.10.14.10\partage\rapport.txt' -Destination 'C:\Users\Public\rapport.txt'
net use \\10.10.14.10\partage /delete
```

### Depuis Linux, déposer le fichier sur un partage Windows {#lw-smb-windows}

Depuis Linux source, `smbclient` envoie `rapport.txt` vers Windows. Le compte `LAB\etudiant` doit avoir les droits d'écriture SMB et NTFS.

```bash
smbclient //10.10.10.30/Depot -U 'LAB/etudiant' -c 'put rapport.txt rapport.txt'
```

### Depuis Linux, envoyer le fichier à Windows par SCP {#lw-scp}

Depuis Linux source, Windows destination doit exécuter OpenSSH Server. `rapport.txt` après `:` est relatif au dossier de connexion distant.

```bash
scp ./rapport.txt etudiant@10.10.10.30:rapport.txt
```

## Windows vers Linux

### Sur Kali, ouvrir un partage SMB de réception {#wl-smb-kali}

Sur Kali destination, garde Impacket actif pendant l'envoi ; utilise un compte temporaire dédié et supprime le partage après le test.

```bash
mkdir -p ./reception
sudo impacket-smbserver -ip 10.10.14.10 -smb2support -username audit -password 'MotDePasseTemporaire' partage ./reception
```

### Depuis Windows, déposer le fichier dans le partage Kali

Depuis Windows source, le fichier est déposé dans `./reception/rapport.txt` sur Kali. Le partage doit autoriser l'écriture.

```powershell
net use \\10.10.14.10\partage * /user:audit
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\10.10.14.10\partage\rapport.txt'
net use \\10.10.14.10\partage /delete
```

### Sur Kali, ouvrir un dossier de réception WebDAV {#wl-webdav}

Sur Kali destination, WsgiDAV et Cheroot doivent être installés. L'écriture anonyme HTTP est réservée à un réseau isolé et doit être désactivée après le transfert.

```bash
mkdir -p ./reception
wsgidav --no-config --host 10.10.14.10 --port 8080 --root ./reception --auth anonymous
```

### Depuis Windows source, envoyer le fichier vers le serveur WebDAV de Kali

```bat
curl.exe --fail --upload-file "C:\Users\Public\rapport.txt" "http://10.10.14.10:8080/rapport.txt"
```

### Depuis Windows, envoyer le fichier à Kali par SCP {#wl-scp}

À exécuter sur Windows source : client OpenSSH disponible, serveur SSH sur Kali destination et compte `kali` autorisé à écrire dans `/tmp`.

```powershell
scp 'C:\Users\Public\rapport.txt' kali@10.10.14.10:/tmp/rapport.txt
```

### Depuis Linux, récupérer le fichier d’un partage Windows {#wl-smb-windows}

À exécuter sur Linux destination : `get` télécharge depuis le partage Windows `Depot` vers le dossier courant Linux.

```bash
smbclient //10.10.10.30/Depot -U 'LAB/etudiant' -c 'get rapport.txt rapport.txt'
```

## Windows vers Windows

### Sur la destination, créer le partage SMB {#ww-creer}

Sur Windows destination, exécuter PowerShell en administrateur uniquement si le partage `Depot` n'existe pas. Accorder également les permissions NTFS nécessaires.

```powershell
New-Item -ItemType Directory -Path 'C:\Depot' -Force
New-SmbShare -Name 'Depot' -Path 'C:\Depot' -ChangeAccess 'LAB\etudiant'
```

### Depuis la source, copier vers le partage SMB {#ww-smb}

Sur Windows source, le compte courant doit avoir les permissions SMB et NTFS d'écriture sur `\\10.10.10.30\Depot`.

```powershell
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\10.10.10.30\Depot\rapport.txt'
```

### Depuis la source, envoyer le fichier par SCP {#ww-scp}

Sur Windows source, lancer le client OpenSSH ; Windows destination doit héberger OpenSSH Server et autoriser l'écriture dans le dossier du compte `etudiant`.

```powershell
scp 'C:\Users\Public\rapport.txt' etudiant@10.10.10.30:rapport.txt
```

## Dossier partagé dans une session RDP

### Depuis Kali, ouvrir la session avec un dossier partagé {#rdp}

Depuis Kali, FreeRDP 3 doit être disponible et la stratégie RDP Windows doit autoriser la redirection de lecteurs. Place les fichiers à envoyer dans `partage`.

```bash
mkdir -p ./partage
xfreerdp3 /v:10.10.10.30 /u:etudiant /dynamic-resolution "/drive:partage,$PWD/partage"
```

### Dans la session RDP Windows, afficher le dossier partagé de Kali

```powershell
Get-ChildItem -LiteralPath '\\tsclient\partage'
```

### Dans la session RDP Windows, copier un fichier depuis Kali

```powershell
Copy-Item -LiteralPath '\\tsclient\partage\rapport.txt' -Destination 'C:\Users\Public\rapport.txt'
```

### Dans la session RDP Windows, renvoyer un fichier vers Kali

```powershell
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\tsclient\partage\retour.txt'
```

## FTP sur un serveur existant

FTP classique transmet les identifiants et les fichiers en clair. Ces commandes concernent un serveur FTP existant, pas un partage anonyme ; réserver les identifiants de test à un réseau isolé.

### Depuis Linux destination, récupérer un fichier depuis le serveur FTP

```bash
curl --fail --user etudiant --output ./rapport.txt ftp://10.10.10.20/rapport.txt
```

### Depuis Linux source, déposer un fichier sur le serveur FTP

Le serveur FTP doit accepter l'upload et le compte `etudiant` doit disposer des droits d'écriture dans le répertoire distant.

```bash
curl --fail --user etudiant --upload-file ./rapport.txt ftp://10.10.10.20/rapport.txt
```

## Transférer un petit fichier sous forme de texte

Base64 encode les octets en texte, sans les chiffrer. Pour un petit fichier seulement, copier toute la chaîne sans retour à la ligne ajouté, puis comparer SHA-256 après décodage.

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
