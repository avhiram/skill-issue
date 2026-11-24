---
title: Reconnaissance passive
aside: true
prev: false
next: false
---

# Reconnaissance passive

[Retour au parcours](./index.md)

Objectif : recenser les actifs connus, vérifier leur appartenance au programme et préparer un inventaire exploitable.

## Énumération des sous-domaines

### Découverte des sous-domaines

```bash
subfinder -d example.com -all -recursive > subexample.com.txt
```

Effectue une recherche récursive avec Subfinder et enregistre les résultats.

### Amass - découverte passive

```bash
amass enum -passive -d example.com -o amass_passive_subs.txt
```

Collecte les sous-domaines depuis des sources publiques.

### Assetfinder - sous-domaines

```bash
assetfinder --subs-only example.com > assetfinder_subs.txt
```

Collecte les noms de sous-domaines connus.

### Findomain - sous-domaines

```bash
findomain -t example.com -q > findomain_subs.txt
```

Collecte les sous-domaines et écrit les résultats dans un fichier.

### Chaos - données publiques

```bash
chaos -d example.com -silent > chaos_subs.txt
```

Interroge le catalogue Chaos de ProjectDiscovery ; vérifier les prérequis d'accès.

### CRT.sh - certificats publics

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" |
jq -r '.[].name_value' |
sed 's/\*\.//g' |
anew crtsh_subs.txt
```

Extrait les noms des certificats publics avec jq et retire le préfixe wildcard.

### Fusion des résultats passifs

```bash
cat *_subs.txt | sort -u > all_subs.txt
```

Fusionne les fichiers de résultats en supprimant les doublons. Exécuter dans le dossier contenant uniquement les fichiers concernés.

## Sources publiques complémentaires

### HackerTarget - DNS passif

```bash
curl -fsS 'https://api.hackertarget.com/hostsearch/?q=example.com' | cut -d ',' -f1 | sort -u > hackertarget_subs.txt
```

Récupère les noms connus dans la base HackerTarget. Variante corrigée du pipeline de l'article, qui se terminait par un pipe vide.

### URLScan - domaines observés

```bash
curl -fsS 'https://urlscan.io/api/v1/search/?q=domain:example.com' | jq -r '.results[]?.page?.domain // empty' | sort -u > urlscan_subs.txt
```

Extrait les domaines observés dans les résultats historiques de URLScan.

### Common Crawl - index historique

```bash
curl -fsS 'https://index.commoncrawl.org/CC-MAIN-2023-50-index?url=*.example.com&output=json' | jq -r '.url' | sed -E 's#^https?://##; s#/.*##' | sort -u > commoncrawl_subs.txt
```

Extrait les hôtes de l'index 2023-50 indiqué dans l'article. Il s'agit d'un index historique, pas d'un inventaire actuel.

### Wayback CDX - URL historiques

```bash
curl -fsS 'https://web.archive.org/cdx/search/cdx?url=*.example.com/*&output=text&fl=original&collapse=urlkey' | sort -u > wayback_cdx.txt
```

Récupère les URL indexées. Le double suffixe .com du document a été corrigé.

### URLScan - adresses IP observées

```bash
curl -fsS 'https://urlscan.io/api/v1/search/?q=domain:example.com' | jq -r '.results[]?.page?.ip // empty' | sort -u > observed_ips.txt
```

Récupère les IP historiques présentes dans les résultats. Une IP observée n'est pas une preuve d'appartenance au scope.

### AlienVault OTX - adresses IP observées

```bash
curl -fsS 'https://otx.alienvault.com/api/v1/indicators/hostname/example.com/url_list?limit=500&page=1' | jq -r '.url_list[]?.result?.urlworker?.ip // empty' | sort -u > otx_ips.txt
```

Extrait les IP observées dans les données publiques OTX. Cette requête ne traite que la première page.

### Fusion des résultats de collecte

```bash
sort -u amass_passive_subs.txt assetfinder_subs.txt findomain_subs.txt chaos_subs.txt crtsh_subs.txt hackertarget_subs.txt urlscan_subs.txt commoncrawl_subs.txt > inventory_subs.txt
```

Fusionne explicitement les fichiers produits par les différentes sources, lorsqu'ils existent. Évite de mélanger tous les fichiers TXT du dossier.

Les exemples de sources publiques sont adaptés du document Recon to Master. Les réponses d'API, quotas, disponibilité et options n'ont pas été testés.

## Shodan

### Recherche par certificat TLS

```text
Ssl.cert.subject.CN:"example.com" 200
```

Requête Shodan historique fondée sur le nom commun d'un certificat.

## Google Dorks

La fiche archivée ne contient pas de commandes supplémentaires.

### Bonnes pratiques

- Remplacer example.com par le domaine autorisé.
- Utiliser la notation [.] lors de la documentation pour éviter la création automatique de liens.
- Combiner les opérateurs de recherche et utiliser les guillemets pour les expressions exactes.
- Exclure les résultats non pertinents avec `-site:` et utiliser les filtres de date.
- Surveiller les nouvelles expositions dans le périmètre autorisé.
- Documenter et vérifier chaque observation avant le signalement.

Voir également [Exposition de données](./vulnerabilites.md#exposition-de-donnees) pour les requêtes déjà présentes.

## Waybackurls - noms de domaine

```bash
waybackurls example.com | unfurl -u domains > wayback_domains.txt
```

Extrait les noms de domaine des URL historiques. Commande issue de l'article IIS ; Unfurl doit être installé. Les domaines découverts ne sont pas automatiquement autorisés.

## Avant de poursuivre

- Inventaire des actifs recensés.
- Actifs autorisés distingués des pistes à vérifier.

---

[Précédent : Programme et préparation](./preparation.md) · [Parcours](./index.md) · [Suivant : Reconnaissance active](./scan-reseau.md)
