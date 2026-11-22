---
title: "OSCP · Analyse de vulnérabilités"
description: "Évaluer les services exposés et rechercher des faiblesses connues."
---

# Analyse de vulnérabilités

## Nessus

Télécharger le paquet adapté depuis [Tenable](https://www.tenable.com/downloads/nessus). Vérifier le SHA-256 publié avant installation.

<p class="oscp-command-note">Sur Kali : comparer l'empreinte du paquet à celle publiée par Tenable.</p>

```bash
cd ~/Downloads
sha256sum ./Nessus-*.deb
```

Remplacer le nom du paquet par le fichier réellement téléchargé et comparer manuellement l'empreinte.

<p class="oscp-command-note">Sur Kali/Debian : installer le paquet Nessus téléchargé.</p>

```bash
sudo apt install ./Nessus-*.deb

```

<p class="oscp-command-note">Démarrer le service Nessus.</p>

```bash
sudo systemctl start nessusd.service

# Interface : https://127.0.0.1:8834

```

## Nmap NSE

<p class="oscp-command-note">Exécuter un script NSE et consulter son aide.</p>

```bash
# Exécuter un script précis
nmap --script <SCRIPT_NSE> <IP_CIBLE>

# Afficher l’aide du script
nmap --script-help <SCRIPT_NSE>

```

<p class="oscp-command-note">Installer un script NSE local et actualiser l'index.</p>

```bash
# Copier le script dans le répertoire NSE
sudo cp /path/to/script.nse /usr/share/nmap/scripts/

# Actualiser la base de scripts
sudo nmap --script-updatedb

# Exemple ciblé
sudo nmap -sV -p 443 --script "http-vuln-cve2021-41773" 192.168.145.23

```

### Interroger les scripts de vulnérabilité

Lister les scripts installés et sélectionner ceux pertinents pour le produit observé.

```bash
ls /usr/share/nmap/scripts/*vuln*.nse
nmap --script-help <SCRIPT_NSE>
```

### Sauvegarder les résultats

Conserver la sortie XML pour une analyse différée ; ne pas interpréter automatiquement chaque résultat comme une faille confirmée.

```bash
nmap -sV --script <SCRIPT_NSE> -p <PORT> -oX <RAPPORT>.xml <IP_CIBLE>
```

## Rechercher et vérifier des exploits publics

SearchSploit consulte la base locale d'Exploit-DB. La présence d'un résultat ne démontre pas qu'une cible est vulnérable : comparer le produit, sa version, la configuration et les prérequis.

### Chercher une référence précise

Rechercher par nom de produit et version plutôt que lancer automatiquement une preuve de concept.

```bash
searchsploit '<PRODUIT> <VERSION>'
```

### Lire le code d'une preuve de concept

Afficher localement le script correspondant à un identifiant EDB pour examiner ses effets avant toute exécution.

```bash
searchsploit -x <IDENTIFIANT_EDB>
```

### Comparer aux résultats d'un scan Nmap

Rechercher des correspondances dans un rapport XML produit avec l'option -oX de Nmap.

```bash
searchsploit --nmap <RAPPORT_NMAP>.xml
```

**Référence technique complémentaire :** [Notes OSCP de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/13_exploitation.md). Cette synthèse conserve la structure de SKILL-ISSUE et reformule les explications.

<!-- notes-krovs-2026 -->

---

Source documentaire : [OSCP+ Cheatsheet d'Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).

<!-- refined-oscp -->
