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


<p class="oscp-command-note">Se placer dans le répertoire utilisé pour «Nessus».</p>

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


<p class="oscp-command-note">Nmap NSE : lancer un script choisi et afficher sa documentation avec --script-help.</p>

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

# Exemple d'utilisation
sudo nmap -sV -p 443 --script "http-vuln-cve2021-41773" 192.168.145.23

```



### Interroger les scripts de vulnérabilité

Lister les scripts installés et sélectionner ceux pertinents pour le produit observé.

<p class="oscp-command-note">Interroger les scripts de vulnérabilité.</p>

```bash
ls /usr/share/nmap/scripts/*vuln*.nse
nmap --script-help <SCRIPT_NSE>
```

### Sauvegarder les résultats

Conserver la sortie XML pour une analyse différée ; ne pas interpréter automatiquement chaque résultat comme une faille confirmée.

<p class="oscp-command-note">Sauvegarder les résultats.</p>

```bash
nmap -sV --script <SCRIPT_NSE> -p <PORT> -oX <RAPPORT>.xml <IP_CIBLE>
```

## Rechercher et vérifier des exploits publics

SearchSploit consulte la base locale d'Exploit-DB. La présence d'un résultat ne démontre pas qu'une cible est vulnérable : comparer le produit, sa version, la configuration et les prérequis.

### Chercher une référence précise

Rechercher par nom de produit et version plutôt que lancer automatiquement une preuve de concept.

<p class="oscp-command-note">Chercher une référence précise.</p>

```bash
searchsploit '<PRODUIT> <VERSION>'
```

### Lire le code d'une preuve de concept

Afficher localement le script correspondant à un identifiant EDB pour examiner ses effets avant toute exécution.

<p class="oscp-command-note">Lire le code d'une preuve de concept.</p>

```bash
searchsploit -x <IDENTIFIANT_EDB>
```

### Comparer aux résultats d'un scan Nmap

Rechercher des correspondances dans un rapport XML produit avec l'option -oX de Nmap.

<p class="oscp-command-note">Comparer aux résultats d'un scan Nmap.</p>

```bash
searchsploit --nmap <RAPPORT_NMAP>.xml
```

**Référence technique complémentaire :** [Notes OSCP de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/13_exploitation.md). Cette synthèse conserve la structure de SKILL-ISSUE et reformule les explications.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
