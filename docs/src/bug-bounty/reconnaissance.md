---
title: Reconnaissance passive
aside: true
prev: false
next: false
---

# Reconnaissance passive

[Retour au parcours](./index.md)

<BountyTarget />

Objectif : recenser les actifs connus, vérifier leur appartenance au programme et préparer un inventaire exploitable.

## Énumération des sous-domaines

### Découverte des sous-domaines

<BountyCommand :source="&quot;subfinder -d __BOUNTY_DOMAIN__ -all -recursive &gt; subexample.com.txt&quot;" language="bash" />

Effectue une recherche récursive avec Subfinder et enregistre les résultats.

### Amass - découverte passive

<BountyCommand :source="&quot;amass enum -passive -d __BOUNTY_DOMAIN__ -o amass_passive_subs.txt&quot;" language="bash" />

Collecte les sous-domaines depuis des sources publiques.

### Assetfinder - sous-domaines

<BountyCommand :source="&quot;assetfinder --subs-only __BOUNTY_DOMAIN__ &gt; assetfinder_subs.txt&quot;" language="bash" />

Collecte les noms de sous-domaines connus.

### Findomain - sous-domaines

<BountyCommand :source="&quot;findomain -t __BOUNTY_DOMAIN__ -q &gt; findomain_subs.txt&quot;" language="bash" />

Collecte les sous-domaines et écrit les résultats dans un fichier.

### Chaos - données publiques

<BountyCommand :source="&quot;chaos -d __BOUNTY_DOMAIN__ -silent &gt; chaos_subs.txt&quot;" language="bash" />

Interroge le catalogue Chaos de ProjectDiscovery ; vérifier les prérequis d'accès.

### CRT.sh - certificats publics

<BountyCommand :source="&quot;curl -s \&quot;https://crt.sh/?q=%25.__BOUNTY_DOMAIN__&amp;output=json\&quot; |\njq -r '.[].name_value' |\nsed 's/\\*\\.//g' |\nanew crtsh_subs.txt&quot;" language="bash" />

Extrait les noms des certificats publics avec jq et retire le préfixe wildcard.

## Sources publiques complémentaires

### HackerTarget - DNS passif

<BountyCommand :source="&quot;curl -fsS 'https://api.hackertarget.com/hostsearch/?q=__BOUNTY_DOMAIN__' | cut -d ',' -f1 | sort -u &gt; hackertarget_subs.txt&quot;" language="bash" />

Récupère les noms connus dans la base HackerTarget. Variante corrigée du pipeline de l'article, qui se terminait par un pipe vide.

### URLScan - domaines observés

<BountyCommand :source="&quot;curl -fsS 'https://urlscan.io/api/v1/search/?q=domain:__BOUNTY_DOMAIN__' | jq -r '.results[]?.page?.domain // empty' | sort -u &gt; urlscan_subs.txt&quot;" language="bash" />

Extrait les domaines observés dans les résultats historiques de URLScan.

### Common Crawl - index historique

<BountyCommand :source="&quot;curl -fsS 'https://index.commoncrawl.org/CC-MAIN-2023-50-index?url=*.__BOUNTY_DOMAIN__&amp;output=json' | jq -r '.url' | sed -E 's#^https?://##; s#/.*##' | sort -u &gt; commoncrawl_subs.txt&quot;" language="bash" />

Extrait les hôtes de l'index 2023-50 indiqué dans l'article. Il s'agit d'un index historique, pas d'un inventaire actuel.

### Wayback CDX - URL historiques

<BountyCommand :source="&quot;curl -fsS 'https://web.archive.org/cdx/search/cdx?url=*.__BOUNTY_DOMAIN__/*&amp;output=text&amp;fl=original&amp;collapse=urlkey' | sort -u &gt; wayback_cdx.txt&quot;" language="bash" />

Récupère les URL indexées. Le double suffixe .com du document a été corrigé.

### URLScan - adresses IP observées

<BountyCommand :source="&quot;curl -fsS 'https://urlscan.io/api/v1/search/?q=domain:__BOUNTY_DOMAIN__' | jq -r '.results[]?.page?.ip // empty' | sort -u &gt; observed_ips.txt&quot;" language="bash" />

Récupère les IP historiques présentes dans les résultats. Une IP observée n'est pas une preuve d'appartenance au scope.

### AlienVault OTX - adresses IP observées

<BountyCommand :source="&quot;curl -fsS 'https://otx.alienvault.com/api/v1/indicators/hostname/__BOUNTY_DOMAIN__/url_list?limit=500&amp;page=1' | jq -r '.url_list[]?.result?.urlworker?.ip // empty' | sort -u &gt; otx_ips.txt&quot;" language="bash" />

Extrait les IP observées dans les données publiques OTX. Cette requête ne traite que la première page.

## Shodan

### Recherche par certificat TLS

<BountyCommand :source="&quot;Ssl.cert.subject.CN:\&quot;__BOUNTY_DOMAIN__\&quot; 200&quot;" language="text" />

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

<BountyCommand :source="&quot;waybackurls __BOUNTY_DOMAIN__ | unfurl -u domains &gt; wayback_domains.txt&quot;" language="bash" />

Extrait les noms de domaine des URL historiques. Commande issue de l'article IIS ; Unfurl doit être installé. Les domaines découverts ne sont pas automatiquement autorisés.

## Fusion des résultats passifs

```bash
for f in subexample.com.txt amass_passive_subs.txt assetfinder_subs.txt findomain_subs.txt chaos_subs.txt crtsh_subs.txt hackertarget_subs.txt urlscan_subs.txt commoncrawl_subs.txt wayback_domains.txt; do
  if [ -f "$f" ]; then cat "$f"; fi
done | sort -u > inventory_subs.txt
```

Fusionne uniquement les fichiers effectivement produits. Les fichiers absents sont ignorés et le fichier de sortie ne peut pas se réinjecter dans la fusion. L'inventaire contient des pistes, pas une autorisation de test.

Avant la reconnaissance active, vérifier les résultats au regard du scope et enregistrer uniquement les noms explicitement autorisés dans `all_subs.txt`.

## Avant de poursuivre

- Inventaire des actifs recensés.
- Actifs autorisés distingués des pistes à vérifier.

---

[Précédent : Programme et préparation](./preparation.md) · [Parcours](./index.md) · [Suivant : Reconnaissance active](./scan-reseau.md)
