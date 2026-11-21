---
title: "OSCP · Transferts de fichiers"
description: "Scénarios reproduisibles Linux, Windows, Kali, SCP, SMB, HTTP, WebDAV, RDP et Netcat."
---

# Transferts de fichiers

**But :** trouver immédiatement comment envoyer ou récupérer un fichier, **dans quel sens**, **sur quelle machine** et **où le récupérer**.

Les IP ci-dessous sont des **exemples de laboratoire** à remplacer : **Kali** `10.10.14.10` · **Linux distant** `10.10.10.20` · **Windows distant** `10.10.10.30`. Tous les fichiers et comptes montrés sont fictifs.

## Quelle méthode choisir ?

| Départ → destination | Meilleure option | Condition |
|---|---|---|
| Linux → Linux | SCP / SFTP / rsync | SSH accessible |
| Linux → Windows | HTTP sur Kali, téléchargement sur Windows | Windows atteint Kali en TCP 8000 |
| Windows → Linux / Kali | SMB sur Kali, copie sur Windows | Windows atteint Kali en TCP 445 |
| Linux ↔ Windows | SCP / partage SMB | SSH ou partage disponible |
| Windows → Windows | Partage SMB | Droit d'accès au partage |
| Linux → Linux sans SSH | Netcat | Port TCP autorisé, pas de chiffrement |
| Windows → Kali sans SMB | WebDAV (PUT) | Serveur de réception accessible |
| Session RDP | Dossier redirigé | RDP autorisé |


**À retenir :** `get` = **récupérer** vers la machine locale ; `put` = **envoyer** vers le serveur. Le sens de `scp` dépend de la place de `utilisateur@hôte:`.

## Vérifier la connexion

### Adresse réseau de Kali

Repérer l'interface VPN et la route vers la cible.

<p class="oscp-command-note">Sur Kali</p>

```bash
ip -br address
ip route
```

### Tester le port de la destination

Un service distant doit écouter : 22 pour SSH, 445 pour SMB et 8000 pour notre exemple HTTP.

<p class="oscp-command-note">Sur Kali</p>

```bash
nc -zv 10.10.10.20 22
nc -zv 10.10.10.30 445
```

### Tester un port depuis Windows

Exemple : vérifier que Windows peut atteindre le serveur HTTP de Kali.

<p class="oscp-command-note">Sur Windows — PowerShell</p>

```powershell
Test-NetConnection 10.10.14.10 -Port 8000
```

## Linux vers Linux

### Envoyer un fichier avec SCP

Le fichier est copié dans `/tmp/` sur le Linux distant. SSH doit fonctionner.

<p class="oscp-command-note">Sur le Linux qui possède le fichier</p>

```bash
scp ./rapport.txt etudiant@10.10.10.20:/tmp/
```

### Récupérer un fichier avec SCP

Le chemin `./rapport.txt` correspond à la machine qui exécute la commande.

<p class="oscp-command-note">Sur le Linux qui doit recevoir le fichier</p>

```bash
scp etudiant@10.10.10.20:/tmp/rapport.txt ./rapport.txt
```

### Envoyer un dossier avec SCP

Le paramètre `-r` copie tout un répertoire.

<p class="oscp-command-note">Sur le Linux source</p>

```bash
scp -r ./dossier/ etudiant@10.10.10.20:/tmp/
```

### Synchroniser un dossier avec rsync

Reprise et suivi des transferts. `rsync` doit être disponible sur les deux machines.

<p class="oscp-command-note">Sur le Linux source</p>

```bash
rsync -avP ./dossier/ etudiant@10.10.10.20:/tmp/dossier/
```

### Transférer en mode SFTP

`put` envoie, `get` télécharge ; `bye` ferme la session.

<p class="oscp-command-note">Sur le Linux source — puis dans SFTP</p>

```text
sftp etudiant@10.10.10.20
put rapport.txt
get autre_fichier.txt
bye
```

### Netcat : sans SSH

**Linux de destination :** démarrer d'abord le récepteur.

```bash
nc -lvnp 9001 > rapport.txt
```

**Linux source :** envoyer ensuite le fichier.

```bash
nc 10.10.10.20 9001 < rapport.txt
```

Netcat ne chiffre ni n'authentifie le contenu : **laboratoire isolé seulement**. Fermer le transfert et contrôler le hash après réception.

## Linux vers Windows

**Cas le plus courant :** Kali héberge le fichier, Windows le télécharge.

### Kali : héberger un fichier par HTTP

Créer un dossier et servir son contenu. `0.0.0.0` permet d'être joint depuis une autre machine.

<p class="oscp-command-note">Sur Kali — terminal à laisser ouvert</p>

```bash
mkdir -p ./partage
cp ./outil.exe ./partage/
python3 -m http.server 8000 --bind 0.0.0.0 --directory ./partage
```

### Windows : télécharger avec PowerShell

Récupérer `outil.exe` à partir du serveur Kali.

<p class="oscp-command-note">Sur Windows — PowerShell</p>

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'http://10.10.14.10:8000/outil.exe' -OutFile 'C:\Users\Public\outil.exe'
```

### Windows : alternative avec curl.exe

Même résultat si `Invoke-WebRequest` est indisponible.

<p class="oscp-command-note">Sur Windows — PowerShell / CMD</p>

```powershell
curl.exe -fL 'http://10.10.14.10:8000/outil.exe' -o 'C:\Users\Public\outil.exe'
```

**Important :** `python3 -m http.server` fournit des fichiers par **GET**. Il **ne reçoit pas** un téléversement `POST` ou `PUT` sans implémentation supplémentaire.

### Alternative : SMB depuis Kali

**Sur Kali :** créer un partage SMB authentifié. Le port SMB 445 nécessite généralement `sudo` pour être ouvert par un processus local.

```bash
mkdir -p ./partage
cp ./outil.exe ./partage/
sudo impacket-smbserver -smb2support -username audit -password 'MotDePasseTest' partage ./partage
```

**Sur Windows :** s'authentifier, récupérer puis fermer la connexion.

```powershell
net use \\10.10.14.10\partage /user:audit 'MotDePasseTest'
Copy-Item '\\10.10.14.10\partage\outil.exe' 'C:\Users\Public\outil.exe'
net use \\10.10.14.10\partage /delete
```

Le mot de passe affiché n'est qu'un exemple : utiliser un identifiant dédié au laboratoire.

### Autres possibilités vers Windows

**Si Windows possède un partage SMB `Depot` en écriture**, depuis Linux :

```bash
smbclient //10.10.10.30/Depot -U 'LAB\etudiant' -c 'put rapport.txt rapport.txt'
```

**Si Windows héberge OpenSSH Server**, depuis Linux :

```bash
scp ./rapport.txt etudiant@10.10.10.30:C:/Users/Public/rapport.txt
```

SCP ne fonctionne que si le service SSH distant est actif ; il ne suffit pas que Windows ait le client SSH.

## Windows vers Linux / Kali

**Méthode privilégiée :** Kali ouvre un partage SMB dans un dossier de réception, puis Windows y dépose le fichier. `sudo` est utilisé ici car le serveur écoute sur le port privilégié 445.

### Kali : ouvrir un partage SMB de réception

Le dossier `./reception/` contiendra les fichiers déposés par Windows.

<p class="oscp-command-note">Sur Kali — terminal à laisser ouvert</p>

```bash
mkdir -p ./reception
sudo impacket-smbserver -smb2support -username audit -password 'MotDePasseTest' partage ./reception
```

### Windows : envoyer le fichier à Kali

Le fichier sera récupérable dans `./reception/rapport.txt` sur Kali.

<p class="oscp-command-note">Sur Windows — PowerShell</p>

```powershell
net use \\10.10.14.10\partage /user:audit 'MotDePasseTest'
Copy-Item 'C:\Users\Public\rapport.txt' '\\10.10.14.10\partage\rapport.txt'
net use \\10.10.14.10\partage /delete
```

### Alternative : WebDAV en réception

**Sur Kali :** un serveur WebDAV accepte des requêtes PUT et peut recevoir des fichiers. L'exemple utilise un accès **anonyme et non chiffré**, réservé à un laboratoire isolé.

```bash
mkdir -p ./reception
wsgidav -H 0.0.0.0 -p 8080 -r ./reception --auth anonymous
```

**Sur Windows :** envoyer le fichier avec la commande native `curl.exe`.

```powershell
curl.exe -T 'C:\Users\Public\rapport.txt' 'http://10.10.14.10:8080/rapport.txt'
```

### Alternative : SCP depuis Windows

**Sur Windows :** si le **serveur SSH de Kali** est accessible et si OpenSSH Client est installé.

```powershell
scp 'C:\Users\Public\rapport.txt' kali@10.10.14.10:/tmp/rapport.txt
```

### Récupérer depuis un partage Windows

**Sur Kali :** si Windows expose déjà le partage `Depot` avec un droit de lecture.

```bash
smbclient //10.10.10.30/Depot -U 'LAB\etudiant' -c 'get rapport.txt rapport.txt'
```

## Windows vers Windows

### Copier vers un partage SMB existant

Le compte utilisé doit avoir des droits sur le partage `Depot` et sur le système de fichiers.

<p class="oscp-command-note">Sur le Windows source — PowerShell</p>

```powershell
Copy-Item 'C:\Users\Public\rapport.txt' '\\10.10.10.30\Depot\rapport.txt'
```

### Créer un partage si vous êtes administrateur

Cas de laboratoire seulement. Adapter le compte et les permissions NTFS avant le transfert.

<p class="oscp-command-note">Sur le Windows de destination — PowerShell administrateur</p>

```powershell
New-Item -ItemType Directory -Path 'C:\Depot' -Force
New-SmbShare -Name 'Depot' -Path 'C:\Depot' -ChangeAccess 'LAB\etudiant'
```

### Copier par SCP entre deux Windows

Nécessite OpenSSH Server sur Windows destination.

<p class="oscp-command-note">Sur le Windows source</p>

```powershell
scp 'C:\Users\Public\rapport.txt' etudiant@10.10.10.30:C:/Users/Public/rapport.txt
```

## Via une session RDP

Si RDP est disponible, **FreeRDP peut partager un dossier Kali avec la session Windows** : les transferts fonctionnent dans les deux sens.

### Ouvrir une session RDP avec partage de dossier

L'exemple utilise FreeRDP 3 ; adapter l'option à la version installée.

<p class="oscp-command-note">Sur Kali</p>

```bash
mkdir -p ./partage
xfreerdp3 /v:10.10.10.30 /u:etudiant /dynamic-resolution /drive:partage,$PWD/partage
```

### Récupérer ou déposer un fichier depuis Windows

Le dossier de Kali est visible sous `\\tsclient\partage`.

<p class="oscp-command-note">Sur Windows — dans la session RDP</p>

```powershell
Get-ChildItem '\\tsclient\partage'
Copy-Item '\\tsclient\partage\outil.exe' 'C:\Users\Public\outil.exe'
Copy-Item 'C:\Users\Public\rapport.txt' '\\tsclient\partage\rapport.txt'
```

## FTP : si le service existe déjà

FTP transmet généralement les identifiants et les données sans chiffrement ; privilégier SCP/SFTP lorsque c'est possible.

### Télécharger depuis FTP

Un compte de laboratoire et un droit de lecture sont nécessaires.

<p class="oscp-command-note">Sur Linux — serveur FTP accessible</p>

```bash
curl --user 'etudiant:MotDePasseTest' 'ftp://10.10.10.20/rapport.txt' -o ./rapport.txt
```

### Envoyer vers FTP

Le serveur doit permettre le téléversement.

<p class="oscp-command-note">Sur Linux — serveur FTP avec écriture autorisée</p>

```bash
curl --user 'etudiant:MotDePasseTest' -T ./rapport.txt 'ftp://10.10.10.20/rapport.txt'
```

## Base64 : si le réseau ne permet aucun transfert

Base64 = **représentation du fichier en texte, pas du chiffrement**. À réserver aux petits fichiers car une chaîne tronquée ne se décode plus correctement.

### Encoder sur Linux

Copier la chaîne imprimée jusqu'à son dernier caractère.

<p class="oscp-command-note">Sur Linux source</p>

```bash
base64 -w 0 ./rapport.txt
```

### Reconstruire sur Windows

Remplacer `BASE64_COLLE_ICI` par la chaîne complète.

<p class="oscp-command-note">Sur Windows — PowerShell</p>

```powershell
[IO.File]::WriteAllBytes('C:\Users\Public\rapport.txt', [Convert]::FromBase64String('BASE64_COLLE_ICI'))
```

### Encoder sur Windows

Cette commande affiche les octets du fichier sous forme de texte.

<p class="oscp-command-note">Sur Windows — PowerShell</p>

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes('C:\Users\Public\rapport.txt'))
```

### Reconstruire sur Linux

Remplacer le texte d'exemple par la chaîne complète.

<p class="oscp-command-note">Sur Linux destination</p>

```bash
printf '%s' 'BASE64_COLLE_ICI' | base64 -d > ./rapport.txt
```

## Vérifier que le fichier est identique

Calculer l'empreinte SHA-256 du **même fichier des deux côtés** et comparer les deux valeurs.

### Empreinte SHA-256 sous Linux

Afficher l'empreinte du fichier reçu ou envoyé.

<p class="oscp-command-note">Terminal Linux</p>

```bash
sha256sum ./rapport.txt
```

### Empreinte SHA-256 sous Windows

Afficher l'empreinte du fichier reçu ou envoyé.

<p class="oscp-command-note">PowerShell Windows</p>

```powershell
Get-FileHash -Algorithm SHA256 'C:\Users\Public\rapport.txt'
```

## Dépannage express

| Erreur | Vérification |
|---|---|
| `Connection refused` | Le serveur n'écoute pas sur le port demandé |
| `Timeout` | Route VPN, pare-feu, IP et réseau du pivot |
| HTTP `404` | Dossier servi ou nom du fichier incorrect |
| HTTP `501` sur `POST` / `PUT` | `python3 -m http.server` ne reçoit pas les fichiers : SMB ou WebDAV |
| SMB `Access denied` | Compte, permissions du partage et permissions NTFS/Unix |
| SCP refusé | SSH serveur absent ou port 22 inaccessible |
| Fichier corrompu | Refaire le transfert et comparer les SHA-256 |


**Règle d'examen :** ne pas confondre le terminal de Kali avec celui de la cible, ni le chemin de la source avec celui de la destination. N'exposer un serveur temporaire que pendant le transfert.

## Sources

- [Python — serveur HTTP](https://docs.python.org/3/library/http.server.html)

- [Microsoft — Copy-Item](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/copy-item)

- [Microsoft — New-SmbShare](https://learn.microsoft.com/en-us/powershell/module/smbshare/new-smbshare)

- [WsgiDAV — CLI](https://wsgidav.readthedocs.io/en/stable/user_guide_cli.html)

- [krovs — OSCP Notes](https://github.com/krovs/oscp-notes/tree/main/docs)

- [Emmanuel Solis — OSCP+ Cheatsheet](https://www.emmanuelsolis.com/oscp.html)