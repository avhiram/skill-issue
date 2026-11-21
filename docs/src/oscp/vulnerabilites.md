---
title: "OSCP · Analyse de vulnérabilités"
description: "Évaluer les services exposés et rechercher des faiblesses connues."
---

# OSCP · Analyse de vulnérabilités

Évaluer les services exposés et rechercher des faiblesses connues.


## Nessus




```text
Go to the Nessus website https://www.tenable.com/downloads/nessus?loginAttempted=true and select the platform.

Download the installer to your local machine.
```


<p class="oscp-command-note">Changer de répertoire.</p>

```bash
# Il est important de vérifier l'intégrité du téléchargement avec `sha256sum`.
cd ~/Downloads
echo "[sha256_sum_found_in_website] Nessus-10.5.0-debian10_amd64.deb" > sha256sum_nessus
sha256sum -c sha256sum_nessus

# Expected Output: OK
```


<p class="oscp-command-note">Gérer les paquets Debian/Ubuntu.</p>

```bash
sudo apt install ./Nessus-10.5.0-debian10_amd64.deb
```


<p class="oscp-command-note">Examiner l&#x27;état des services Linux.</p>

```bash
sudo systemctl start nessusd.service

# Ensuite, visitez le Nesus GUI à https://127.0.0.1:8834 pour configurer le scanner.
```


## Nmap NSE (moteur de script Nmap)

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Examiner les services avec les scripts NSE sélectionnés.</p>

```bash
# Exécuter un script précis
nmap --script [scriptName] [IP]

# Afficher l’aide du script
nmap --script-help [scriptName]
```


<p class="oscp-command-note">Copier les fichiers indiqués.</p>

```bash
# Les scripts sont situés dans /usr/share/nmap/scripts; nous pouvons ajouter de nouveaux scripts en les copiant dans ce répertoire
sudo cp /path/to/script.nse /usr/share/nmap/scripts/

# Actualiser la base de scripts
sudo nmap --script-updatedb

# Usage example
sudo nmap -sV -p 443 --script "http-vuln-cve2021-41773" 192.168.145.23
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
