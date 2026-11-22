---
title: "OSCP · Transferts de fichiers"
description: "Transferts Linux et Windows avec SCP, SFTP, SMB, HTTP ou HTTPS. Choisir la source, la destination et la machine qui lance la commande."
---

# Transferts de fichiers entre Linux et Windows {#transferts-de-fichiers}

La **source** possède le fichier et la **destination** le reçoit. Choisis le sens du transfert, puis adapte les adresses, les comptes et les chemins du fichier témoin `rapport.txt`.

<TransferSelector />

| Machine d’exemple | Adresse |
| --- | --- |
| Kali | `10.10.14.10` |
| Second Linux | `10.10.10.20` |
| Windows distant | `10.10.10.30` |

Pour les transferts **Windows vers Windows**, `10.10.10.30` représente le poste de destination. Les commandes Windows utilisent `C:\Users\Public\rapport.txt`. Si tu copies depuis un autre dossier, adapte le chemin à chaque étape.

## Ports et prérequis

| Méthode | Ports par défaut ou d’exemple | Service et droits |
| --- | --- | --- |
| SCP, SFTP et rsync via SSH | TCP 22 | Serveur SSH sur la machine jointe. Le compte lit ou écrit le fichier selon le sens de la copie. |
| SMB | TCP 445 | Partage existant ou serveur SMB local. Vérifie les permissions du partage et du dossier. |
| HTTP et HTTPS | TCP 8000 ou 443 dans les exemples | Serveur sur la source pour un téléchargement. En HTTPS, il lui faut un certificat reconnu par le client. |
| WebDAV | TCP 8080 dans l’exemple | Serveur sur la destination qui accepte l’écriture en HTTP PUT. |
| FTP | TCP 21 pour le contrôle et ports de données passifs du serveur | Serveur FTP existant. Ouvre aussi la plage passive pour permettre le transfert. |
| RDP | TCP 3389 par défaut | Connexion RDP, avec redirection des lecteurs autorisée. |
| Netcat | TCP 9001 dans l’exemple | Écoute côté destination et connexion côté source. |

## Linux vers Linux

### Sur Kali, envoyer un fichier au second Linux par SCP {#ll-scp}

Sur Kali source, envoie le fichier dans `/tmp/rapport.txt` sur le second Linux. Le compte SSH `etudiant` doit avoir le droit d’écrire dans `/tmp`.

```bash
scp ./rapport.txt etudiant@10.10.10.20:/tmp/
```

### Sur Kali, récupérer un fichier du second Linux par SCP {#ll-scp-reception}

Sur Kali destination, télécharge `/tmp/rapport.txt` depuis le second Linux avec un compte SSH autorisé à le lire. Choisis un autre nom de sortie si `./rapport.txt` existe déjà et doit être conservé.

```bash
scp etudiant@10.10.10.20:/tmp/rapport.txt ./rapport.txt
```

### Sur Kali, envoyer un dossier complet au second Linux par SCP {#ll-scp-dossier}

Le dossier `./dossier` doit exister sur Kali ; `-r` copie récursivement son contenu vers `/tmp/dossier` sur le second Linux.

```bash
scp -r ./dossier etudiant@10.10.10.20:/tmp/
```

### Sur Kali, synchroniser un dossier vers le second Linux avec rsync {#ll-rsync}

Installe `rsync` sur les deux Linux et lance la copie depuis Kali source avec un accès SSH en écriture. Le `/` final de `./dossier/` copie son contenu dans `/tmp/dossier/` et `-P` conserve les transferts partiels et affiche la progression.

```bash
rsync -avP ./dossier/ etudiant@10.10.10.20:/tmp/dossier/
```

### Sur Kali, ouvrir une session SFTP vers le second Linux {#ll-sftp}

Le serveur SSH/SFTP doit être actif sur `10.10.10.20` ; la connexion demande l'authentification du compte `etudiant`.

```bash
sftp etudiant@10.10.10.20
```

### Dans SFTP, envoyer et récupérer un fichier

Dans l’invite `sftp>` ouverte sur Kali, vérifie les répertoires local et distant. `put` envoie `rapport.txt` depuis Kali et `get` récupère `autre_fichier.txt` dans le répertoire local.

```text
lpwd
pwd
put rapport.txt
get autre_fichier.txt
bye
```

### Sur le second Linux, télécharger le fichier HTTP servi par Kali {#ll-http}

Démarre d’abord [le serveur HTTP sur Kali](#http-source). Sur le second Linux destination, télécharge le fichier dans le dossier courant. `--fail` signale les erreurs HTTP 4xx et 5xx.

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

Sur Kali source, Python 3.7 ou plus récent sert le dossier `./partage` en lecture seule sur TCP 8000. Utilise un dossier dédié aux fichiers à partager et garde le terminal ouvert. L’accès se fait en clair et sans authentification.

```bash
mkdir -p ./partage
cp ./rapport.txt ./partage/
python3 -m http.server 8000 --bind 10.10.14.10 --directory ./partage
```

### Sur Windows, télécharger le fichier HTTP de Kali avec PowerShell {#lw-http-ps}

Après avoir [démarré le serveur HTTP sur Kali](#http-source), exécute la commande sur Windows destination. Le fichier est écrit dans `C:\Users\Public\rapport.txt`.

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://10.10.14.10:8000/rapport.txt' -OutFile 'C:\Users\Public\rapport.txt'
```

### Sur Windows, télécharger le fichier HTTP de Kali avec curl.exe {#lw-http-curl}

Sur Windows destination, lance la commande dans CMD ou PowerShell après avoir [démarré le serveur sur Kali](#http-source). Le nom `curl.exe` appelle le binaire Windows, y compris dans les versions de PowerShell où `curl` est un alias.

```bat
curl.exe --fail --location --output "C:\Users\Public\rapport.txt" "http://10.10.14.10:8000/rapport.txt"
```

### Sur Kali, partager le fichier par SMB {#lw-smb-kali}

Sur Kali source, lance ce bloc dans Bash pour publier `./partage` sur TCP 445 avec le serveur SMB d’Impacket. Choisis un mot de passe temporaire réservé à ce service, transmis au processus comme argument.

```bash
mkdir -p ./partage
cp ./rapport.txt ./partage/
read -r -s -p 'Mot de passe SMB temporaire : ' mot_de_passe
printf '\n'
if [ -n "$mot_de_passe" ]; then
  sudo impacket-smbserver -ip 10.10.14.10 -smb2support -username audit -password "$mot_de_passe" partage ./partage
fi
unset mot_de_passe
```

### Sur Windows, récupérer le fichier du partage SMB de Kali

Après avoir [ouvert le partage sur Kali](#lw-smb-kali), lance les commandes sur Windows destination. `net use` demande le mot de passe et `Copy-Item` écrit le fichier dans `C:\Users\Public\rapport.txt`.

```powershell
net use \\10.10.14.10\partage * /user:audit
Copy-Item -LiteralPath '\\10.10.14.10\partage\rapport.txt' -Destination 'C:\Users\Public\rapport.txt'
net use \\10.10.14.10\partage /delete
```

### Sur Kali, envoyer le fichier vers un partage SMB Windows {#lw-smb-windows}

Sur Kali source, connecte-toi au partage Windows `Depot`. Le client demande le mot de passe du compte `LAB\etudiant`, qui doit disposer des droits d’écriture SMB et NTFS.

```bash
smbclient //10.10.10.30/Depot -U 'LAB/etudiant'
```

Dans l’invite `smb: \>`, envoie le fichier local sous le même nom dans le dossier distant.

```text
put rapport.txt rapport.txt
exit
```

### Sur Kali, envoyer le fichier à Windows par SCP {#lw-scp}

Sur Kali source, envoie `./rapport.txt` dans le répertoire de connexion du compte `etudiant` sur Windows. OpenSSH Server doit y être actif et le compte autorisé à écrire.

```bash
scp ./rapport.txt etudiant@10.10.10.30:rapport.txt
```

## Windows vers Linux

### Sur Windows source, envoyer le fichier à Kali par SCP {#wl-scp}

Sur Windows source, utilise le client OpenSSH pour écrire `/tmp/rapport.txt` sur Kali. Le serveur SSH de Kali doit être joignable et le compte `kali` doit pouvoir écrire dans `/tmp`.

```powershell
scp 'C:\Users\Public\rapport.txt' kali@10.10.14.10:/tmp/rapport.txt
```

### Sur Kali, récupérer un fichier du partage Windows par SMB {#wl-smb-windows}

Sur Kali destination, connecte-toi au partage Windows `Depot` avec un compte autorisé à lire le fichier.

```bash
smbclient //10.10.10.30/Depot -U 'LAB/etudiant'
```

Dans l’invite `smb: \>`, récupère le fichier dans le dossier courant de Kali. Le deuxième nom passé à `get` indique le nom de sortie local.

```text
get rapport.txt rapport.txt
exit
```

### Sur Kali, ouvrir un partage SMB de réception {#wl-smb-kali}

Sur Kali destination, lance ce bloc dans Bash pour publier `./reception` en écriture sur TCP 445 avec Impacket. Saisis un mot de passe temporaire, transmis au processus comme argument, et laisse le serveur actif pendant la copie.

```bash
mkdir -p ./reception
read -r -s -p 'Mot de passe SMB temporaire : ' mot_de_passe
printf '\n'
if [ -n "$mot_de_passe" ]; then
  sudo impacket-smbserver -ip 10.10.14.10 -smb2support -username audit -password "$mot_de_passe" partage ./reception
fi
unset mot_de_passe
```

### Sur Windows source, envoyer un fichier au partage SMB de Kali

Après avoir [ouvert le partage sur Kali](#wl-smb-kali), lance les commandes sur Windows source. `net use` demande le mot de passe et `Copy-Item` dépose le fichier dans `./reception/rapport.txt` sur Kali.

```powershell
net use \\10.10.14.10\partage * /user:audit
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\10.10.14.10\partage\rapport.txt'
net use \\10.10.14.10\partage /delete
```

### Sur Kali, ouvrir un dossier de réception WebDAV {#wl-webdav}

Sur Kali destination, installe WsgiDAV et Cheroot, puis laisse le serveur actif sur TCP 8080. Cette configuration autorise l’écriture dans `./reception` en clair et sans authentification sur un réseau de test isolé.

```bash
mkdir -p ./reception
wsgidav --no-config --host 10.10.14.10 --port 8080 --root ./reception --auth anonymous
```

### Sur Windows source, déposer le fichier sur Kali via WebDAV

Après avoir [ouvert le dossier de réception sur Kali](#wl-webdav), lance `curl.exe` sous Windows. La requête HTTP PUT écrit le fichier dans `./reception/rapport.txt` sur Kali.

```bat
curl.exe --fail --upload-file "C:\Users\Public\rapport.txt" "http://10.10.14.10:8080/rapport.txt"
```

## Windows vers Windows

### Depuis Windows, copier vers un partage SMB {#ww-smb}

Sur Windows source, copie le fichier local vers le partage `Depot` du poste distant. Le compte courant doit y disposer des droits d’écriture SMB et NTFS. Si le partage est absent, [crée-le sur Windows destination](#ww-creer).

```powershell
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\10.10.10.30\Depot\rapport.txt'
```

### Depuis Windows, envoyer vers Windows par SCP {#ww-scp}

Sur Windows source, utilise le client OpenSSH. OpenSSH Server doit être actif sur Windows destination et le compte `etudiant` doit pouvoir écrire dans son répertoire de connexion.

```powershell
scp 'C:\Users\Public\rapport.txt' etudiant@10.10.10.30:rapport.txt
```

### Sur Windows destination, créer un partage SMB {#ww-creer}

Sur Windows destination, ouvre PowerShell en administrateur et crée le partage `Depot` s’il est absent. Accorde séparément au compte existant `LAB\etudiant` les droits d’écriture NTFS sur `C:\Depot`.

```powershell
New-Item -ItemType Directory -Path 'C:\Depot' -Force
New-SmbShare -Name 'Depot' -Path 'C:\Depot' -ChangeAccess 'LAB\etudiant'
```

## Téléchargement HTTPS

Ces exemples utilisent un serveur HTTPS existant sur la machine source, accessible sur TCP 443. Remplace `transferts.example.org` par le nom couvert par le certificat du serveur et vérifie que le fichier est accessible à cette URL.

### Sur Linux destination, télécharger avec curl {#https-linux}

Le client vérifie le nom du serveur et la chaîne du certificat avant d’écrire `./rapport.txt`. Pour une autorité interne, utilise le magasin de confiance du système ou indique à curl le certificat de l’autorité avec `--cacert`.

```bash
curl --fail --show-error --output ./rapport.txt 'https://transferts.example.org/rapport.txt'
```

### Sur Windows destination, télécharger avec PowerShell {#https-windows}

Le certificat du serveur doit être reconnu par Windows. La commande écrit le fichier dans `C:\Users\Public`.

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'https://transferts.example.org/rapport.txt' -OutFile 'C:\Users\Public\rapport.txt'
```

## Dossier partagé dans une session RDP

### Sur Kali, ouvrir RDP avec redirection du dossier local {#rdp}

Sur Kali, ouvre la session avec FreeRDP 3. Si Windows autorise la redirection de lecteurs, le répertoire Kali devient accessible dans la session sous `\\tsclient\partage`.

```bash
mkdir -p ./partage
xfreerdp3 /v:10.10.10.30 /u:etudiant /dynamic-resolution "/drive:partage,$PWD/partage"
```

### Sur Windows distant, afficher le dossier Kali redirigé par RDP

Depuis PowerShell dans la session RDP, liste les fichiers du dossier redirigé. La présence de `rapport.txt` indique que le fichier est accessible dans cette session.

```powershell
Get-ChildItem -LiteralPath '\\tsclient\partage'
```

### Sur Windows distant, récupérer un fichier du dossier Kali redirigé

La source `\\tsclient\partage\rapport.txt` reste sur Kali ; `Copy-Item` crée la copie locale sur le Windows de la session RDP.

```powershell
Copy-Item -LiteralPath '\\tsclient\partage\rapport.txt' -Destination 'C:\Users\Public\rapport.txt'
```

### Sur Windows distant, renvoyer un fichier dans le dossier Kali redirigé {#rdp-retour}

Après avoir [ouvert la session RDP depuis Kali](#rdp), lance la copie dans le PowerShell du poste Windows. Si la redirection autorise l’écriture, le fichier apparaît dans `./partage/retour.txt` sur Kali.

```powershell
Copy-Item -LiteralPath 'C:\Users\Public\rapport.txt' -Destination '\\tsclient\partage\retour.txt'
```

## FTP sur un serveur existant

FTP transmet les identifiants et les fichiers en clair. Les exemples utilisent un compte sur un serveur FTP existant. Pour un service explicitement public, voir [FTP Anonymous](./reconnaissance.md#accès-ftp-anonyme).

### Sur Kali, télécharger un fichier depuis le serveur FTP distant {#ftp}

`--user etudiant` utilise le compte FTP et demande son mot de passe si nécessaire ; `--output` écrit le fichier localement sur Kali.

```bash
curl --fail --user etudiant --output ./rapport.txt ftp://10.10.10.20/rapport.txt
```

### Sur Kali, envoyer un fichier vers le serveur FTP distant

Sur Kali source, lis `./rapport.txt` et envoie-le au serveur FTP. Le compte `etudiant` doit être autorisé à écrire dans le répertoire distant.

```bash
curl --fail --user etudiant --upload-file ./rapport.txt ftp://10.10.10.20/rapport.txt
```

## Transférer un petit fichier sous forme de texte

Base64 représente les octets sous forme de texte **sans chiffrement**. Réserver cette méthode aux petits fichiers, copier la chaîne complète sans caractères supplémentaires et comparer les empreintes SHA-256 après reconstruction.

### Sur Kali source, encoder un fichier en Base64 pour Windows {#base64-linux}

Sur Kali source, GNU `base64` affiche une ligne à copier dans l’invite PowerShell sur Windows destination.

```bash
base64 -w 0 ./rapport.txt
```

### Sur Windows destination, reconstruire le fichier depuis Base64

Sur Windows destination, colle la ligne encodée quand PowerShell affiche l’invite. La commande crée ou remplace le fichier local.

```powershell
[IO.File]::WriteAllBytes('C:\Users\Public\rapport.txt', [Convert]::FromBase64String((Read-Host 'Base64')))
```

### Sur Windows source, encoder un fichier en Base64 pour Linux {#base64-windows}

Sur Windows source, PowerShell affiche une ligne à transmettre à Kali.

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\Users\Public\rapport.txt'))
```

### Sur Kali destination, reconstruire le fichier depuis Base64

Sur Kali destination, colle la ligne encodée à l’invite Bash. La redirection écrit les octets décodés dans le fichier local, en remplaçant son contenu éventuel.

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

### Comparer les empreintes sous Windows avec PowerShell

Exécuter sur chaque machine concernée ; le champ `Hash` doit correspondre à l'empreinte calculée sur Linux ou Windows pour le même fichier.

```powershell
Get-FileHash -LiteralPath 'C:\Users\Public\rapport.txt' -Algorithm SHA256
```

### Calculer l’empreinte sous Windows avec certutil

Dans CMD, utilise `certutil` pour afficher l’empreinte SHA-256 du fichier de la machine courante. Compare-la à celle calculée sur l’autre machine.

```bat
certutil -hashfile "C:\Users\Public\rapport.txt" SHA256
```

## Vérifier la connexion

### Afficher les adresses et les routes de Kali

Sur Kali, repère l’adresse de l’interface utilisée pour le transfert et la route vers l’autre machine.

```bash
ip -br address
ip route
```

### Sur Kali, vérifier l'accès TCP aux services SSH et SMB

Sur Kali, teste le serveur SSH Linux (TCP 22) et le partage SMB Windows (TCP 445). Une connexion TCP établie permet ensuite de tester l’authentification et les droits de copie.

```bash
nc -zv 10.10.10.20 22
nc -zv 10.10.10.30 445
```

### Sur Windows, vérifier l'accès TCP au serveur HTTP de Kali

Sur Windows, cherche `TcpTestSucceeded : True` dans la sortie. Une réponse HTTP 404 à l’étape suivante indique que le serveur est joignable et que le chemin du fichier est à vérifier.

```powershell
Test-NetConnection 10.10.14.10 -Port 8000
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

[Invoke-WebRequest](https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/invoke-webrequest) · [Get-FileHash](https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/get-filehash) · [Certutil](https://learn.microsoft.com/windows-server/administration/windows-commands/certutil).

Sources d’origine : [notes de krovs](https://github.com/krovs/oscp-notes/tree/main/docs) et [guide d’Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).
