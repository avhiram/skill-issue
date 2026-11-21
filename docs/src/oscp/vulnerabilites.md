---
title: "OSCP · Analyse de vulnérabilités"
description: "Évaluer les services exposés et rechercher des faiblesses connues."
---

# OSCP · Analyse de vulnérabilités

Évaluer les services exposés et rechercher des faiblesses connues.


## Nessus


<p class="oscp-command-note">Exemple avec l&#x27;outil go.</p>

```text
Go to the Nessus website https://www.tenable.com/downloads/nessus?loginAttempted=true and select the platform.

Download the installer to your local machine.
```


<p class="oscp-command-note">Exemple avec l&#x27;outil cd.</p>

```bash
#  It's important to verify the integrity of the download with `sha256sum`.
cd ~/Downloads
echo "[sha256_sum_found_in_website] Nessus-10.5.0-debian10_amd64.deb" > sha256sum_nessus
sha256sum -c sha256sum_nessus

# Expected Output: OK
```


<p class="oscp-command-note">Exemple avec l&#x27;outil apt.</p>

```bash
sudo apt install ./Nessus-10.5.0-debian10_amd64.deb
```


<p class="oscp-command-note">Exemple avec l&#x27;outil systemctl.</p>

```bash
sudo systemctl start nessusd.service

# Then, visit the Nessus GUI at https://127.0.0.1:8834 to configure the scanner.
```


## Nmap NSE (Nmap Scripting Engine)

Vérifier les ports et les services de la cible autorisée.


<p class="oscp-command-note">Examiner le service avec les scripts NSE sélectionnés.</p>

```bash
# Run specific script
nmap --script [scriptName] [IP]

# Get help on what a script does
nmap --script-help [scriptName]
```


<p class="oscp-command-note">Exemple avec l&#x27;outil cp.</p>

```bash
# Scripts are located in /usr/share/nmap/scripts; we can add new scripts by copying them into this directory
sudo cp /path/to/script.nse /usr/share/nmap/scripts/

# Update the script database
sudo nmap --script-updatedb

# Usage example
sudo nmap -sV -p 443 --script "http-vuln-cve2021-41773" 192.168.145.23
```

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
