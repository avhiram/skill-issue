---
title: Reconnaissance active
aside: true
prev: false
next: false
---

# Reconnaissance active

[Retour au parcours](./index.md)

Identifier les services, ports et technologies des actifs autorisés par le programme.

## Validation DNS et HTTP

Vérifier l'appartenance des noms collectés au scope avant les requêtes actives. Les exemples de fichiers historiques utilisent plusieurs noms ; sélectionner explicitement les fichiers de la méthode choisie.

### DNSX - validation DNS

```bash
dnsx -l all_subs.txt -silent -o resolved_subs.txt
```

Identifie les noms qui répondent aux requêtes DNS.

### DNSX - résolution inverse

```bash
dnsx -ptr -l resolved_subs.txt -resp-only -o reverse_dns.txt
```

Interroge les enregistrements PTR ; utiliser une liste d'adresses IP pour une résolution inverse pertinente, plutôt qu'une liste de noms.

### HTTPX - métadonnées des services

```bash
httpx -l resolved_subs.txt -p 80,443,8080,8443 -silent -title -sc -ip -o live_websites.txt
```

Identifie les services HTTP répondants et collecte titres, codes et adresses IP. Utiliser HTTPX de ProjectDiscovery.

### Filtrage des sous-domaines actifs

```bash
cat subexample.com.txt | httpx-toolkit -ports 80,443,8080,8000,8888 -threads 200 > subexample.coms_alive.txt
```

Vérifie les réponses HTTP sur plusieurs ports et enregistre les hôtes répondants.

> La commande emploie une concurrence élevée. Respecter les limites du programme.

### Httprobe - services Web

```bash
cat resolved_subs.txt | httprobe > live_websites.txt
```

Alternative de détection des services HTTP et HTTPS. Le fichier de sortie est écrasé.

## Scan réseau

### Inventaire des ports avec Naabu

```bash
naabu -list ip.txt -c 50 -nmap-cli 'nmap -sV -SC' -o naabu-full.txt
```

Associe Naabu et Nmap pour identifier des ports et services.

### Scan complet avec Nmap

```bash
nmap -p- --min-rate 1000 -T4 -A example.com -oA fullscan
```

Analyse l'ensemble des ports TCP et collecte des informations sur les services.

> Débit et options intrusives à vérifier selon les règles du programme.

### Scan avec Masscan

```bash
masscan -p0-65535 example.com --rate 100000 -oG masscan-results.txt
```

Exemple historique de scan de ports à débit très élevé.

> Débit extrêmement élevé dans l'original ; ne pas exécuter sur des systèmes tiers.

## Reconnaissance visuelle

### Aquatone - captures des services Web

```bash
cat hosts.txt | aquatone
```

Génère des captures et un rapport visuel à partir d'une liste de services Web autorisés. Préparer `hosts.txt` avec les hôtes validés et vérifier les dépendances du logiciel. Aquatone est un outil historique ; sa compatibilité actuelle n'a pas été testée.

### Cartographie ASN et IP

Identifier les réseaux et les systèmes autonomes associés à une organisation, puis comparer les résultats avec le périmètre explicitement autorisé. Une association ASN, DNS ou IP ne suffit pas à établir qu'un actif peut être testé. Cette étape complète l'énumération des sous-domaines sans répéter les commandes existantes.

### Checklist de reconnaissance

- [ ] Collecte passive et déduplication des sous-domaines.
- [ ] Validation DNS et contrôle du scope.
- [ ] Inventaire HTTP et identification des technologies.
- [ ] Cartographie ASN/IP et reconnaissance visuelle.
- [ ] Collecte des URL, paramètres et références JavaScript.
- [ ] Inventaire des interfaces API et des fonctionnalités.
- [ ] Vérification manuelle des observations et préparation du rapport.

## Nmap - rapport XML local

```bash
nmap -sV -p 8000,8080 -oX nmap_out.xml 127.0.0.1
```

Produit un inventaire XML des deux ports du laboratoire local. Adaptation pour alimenter le parseur Nmap présenté dans le workflow de scanning.

## Workflow de scanning et fuzzing

L'article organise le travail en six étapes. Les commandes déjà documentées dans la cheatsheet ne sont pas répétées.

1. **Chaos** : collecte des sous-domaines.
2. **HTTPX** : validation HTTP et inventaire, déduplication des résultats.
3. **Naabu** : inventaire des ports expressément autorisés.
4. **Nmap** : identification des services et production de résultats XML.
5. **Nuclei** : contrôle des configurations et vulnérabilités connues dans le périmètre de test.
6. **FFUF** : découverte de contenu dans un laboratoire autorisé.

Ne pas assimiler une adresse IP partagée, un CDN ou un service tiers à un actif autorisé. Vérifier le scope avant tout scan. Comparer les codes HTTP, la taille des réponses et le nombre de mots pour distinguer les réponses génériques des résultats pertinents ; un 403 doit être respecté.

### Nmap - conversion XML en HTML

```bash
./nmap-parse-output nmap_out.xml html > scan.html
```

Convertit un rapport Nmap XML déjà produit en document HTML, sans effectuer de nouvelle requête. Adapter le chemin au fichier local. La syntaxe est reprise de l'article avec un chemin générique.

[Script nmap-parse-output](https://github.com/ernw/nmap-parse-output)

## Avant de poursuivre

- Inventaire des services et technologies observés.
- Périmètre confirmé avant de poursuivre.

---

[Précédent : Reconnaissance passive](./reconnaissance.md) · [Parcours](./index.md) · [Suivant : Cartographie Web et API](./cartographie-web.md)
