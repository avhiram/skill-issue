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

Les collectes sont complémentaires : utiliser les sources disponibles, puis fusionner leurs résultats en fin de chapitre. Il n'est pas nécessaire d'exécuter chaque outil.

### Subfinder - sous-domaines

<BountyCommand :source="&quot;subfinder -d __BOUNTY_DOMAIN__ -all -recursive &gt; subfinder_subs.txt&quot;" language="bash" />

Collecte les noms dans `subfinder_subs.txt`. `-all` sélectionne toutes les sources et `-recursive` limite la collecte aux sources compatibles avec les sous-domaines récursifs. Certaines sources nécessitent des clés API.

### Amass - découverte passive

<BountyCommand :source="&quot;amass enum -passive -d __BOUNTY_DOMAIN__ -o amass_passive_subs.txt&quot;" language="bash" />

Collecte les noms dans `amass_passive_subs.txt`. Les options correspondent à la documentation historique d'Amass ; vérifier leur disponibilité dans la version installée.

### Assetfinder - sous-domaines

<BountyCommand :source="&quot;assetfinder --subs-only __BOUNTY_DOMAIN__ &gt; assetfinder_subs.txt&quot;" language="bash" />

Collecte les sous-domaines connus dans `assetfinder_subs.txt` ; `--subs-only` exclut les domaines simplement associés.

### Findomain - sous-domaines

<BountyCommand :source="&quot;findomain -t __BOUNTY_DOMAIN__ -q &gt; findomain_subs.txt&quot;" language="bash" />

Enregistre les noms dans `findomain_subs.txt`. `-t` indique la cible et `-q` active le mode silencieux.

### Chaos - données publiques

<BountyCommand :source="&quot;chaos -d __BOUNTY_DOMAIN__ -silent &gt; chaos_subs.txt&quot;" language="bash" />

Interroge le catalogue Chaos de ProjectDiscovery. Vérifier les droits d'accès et la configuration de la clé API du client avant utilisation.

### CRT.sh - certificats publics

<BountyCommand :source="&quot;curl -s \&quot;https://crt.sh/?q=%25.__BOUNTY_DOMAIN__&amp;output=json\&quot; |\njq -r '.[].name_value' |\nsed 's/\\*\\.//g' |\nanew crtsh_subs.txt&quot;" language="bash" />

Extrait les noms des certificats publics avec jq, retire les wildcards et ajoute les résultats inédits à `crtsh_subs.txt` avec `anew`. Une réponse vide ou une erreur HTTP ne prouve pas l'absence de certificats.

## Sources publiques complémentaires

### HackerTarget - DNS passif

<BountyCommand :source="&quot;curl -fsS 'https://api.hackertarget.com/hostsearch/?q=__BOUNTY_DOMAIN__' | cut -d ',' -f1 | sort -u &gt; hackertarget_subs.txt&quot;" language="bash" />

Extrait la première colonne du résultat HackerTarget (nom, IP). Vérifier les quotas et les éventuels messages d'erreur avant la fusion.

### URLScan - domaines observés

<BountyCommand :source="&quot;curl -fsS 'https://urlscan.io/api/v1/search/?q=domain:__BOUNTY_DOMAIN__' | jq -r '.results[]?.page?.domain // empty' | sort -u &gt; urlscan_subs.txt&quot;" language="bash" />

Extrait les domaines observés dans les résultats historiques de URLScan. La requête ne traite pas toutes les pages ; vérifier les quotas et les droits d'accès.

### Common Crawl - index historique

<BountyCommand :source="&quot;curl -fsS 'https://index.commoncrawl.org/CC-MAIN-2023-50-index?url=*.__BOUNTY_DOMAIN__&amp;output=json' | jq -r '.url' | sed -E 's#^https?://##; s#/.*##' | sort -u &gt; commoncrawl_subs.txt&quot;" language="bash" />

Extrait la partie hôte des URL de l'index 2023-50. Un port éventuel reste présent dans cette variante ; contrôler le format avant la fusion. Cet index est historique, pas un inventaire actuel.

### Wayback CDX - URL historiques

<BountyCommand :source="&quot;curl -fsS 'https://web.archive.org/cdx/search/cdx?url=*.__BOUNTY_DOMAIN__/*&amp;output=text&amp;fl=original&amp;collapse=urlkey' | sort -u &gt; wayback_cdx.txt&quot;" language="bash" />

Enregistre les URL indexées dans `wayback_cdx.txt`, réutilisé au chapitre Web. Il ne s'agit pas d'une liste de domaines.

### URLScan - adresses IP observées

<BountyCommand :source="&quot;curl -fsS 'https://urlscan.io/api/v1/search/?q=domain:__BOUNTY_DOMAIN__' | jq -r '.results[]?.page?.ip // empty' | sort -u &gt; observed_ips.txt&quot;" language="bash" />

Enregistre les IP historiques dans `observed_ips.txt`. La recherche est limitée aux résultats renvoyés par l'API. Une IP observée ne prouve pas son appartenance au scope.

### AlienVault OTX - adresses IP observées

<BountyCommand :source="&quot;curl -fsS 'https://otx.alienvault.com/api/v1/indicators/hostname/__BOUNTY_DOMAIN__/url_list?limit=500&amp;page=1' | jq -r '.url_list[]?.result?.urlworker?.ip // empty' | sort -u &gt; otx_ips.txt&quot;" language="bash" />

Extrait les IP observées dans `otx_ips.txt`. La requête ne traite que la première page ; le schéma JSON et les droits d'accès restent à confirmer sur une réponse réelle.

## Shodan

### Recherche par certificat TLS

<BountyCommand :source="&quot;Ssl.cert.subject.CN:\&quot;__BOUNTY_DOMAIN__\&quot; 200&quot;" language="text" />

Recherche Shodan à saisir dans l'interface de recherche, pas dans le terminal. Le filtre historique porte sur le nom commun du certificat ; le terme `200` n'est pas une preuve d'un statut HTTP.

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

Extrait les noms d'hôtes des URL historiques avec Unfurl (`-u` déduplique). Les résultats ne constituent pas une liste de cibles autorisées.

## Fusion des résultats passifs

```bash
for f in subfinder_subs.txt amass_passive_subs.txt assetfinder_subs.txt findomain_subs.txt chaos_subs.txt crtsh_subs.txt hackertarget_subs.txt urlscan_subs.txt commoncrawl_subs.txt wayback_domains.txt; do
  if [ -f "$f" ]; then cat "$f"; fi
done | sort -u > inventory_subs.txt
```

Fusion volontaire : Subfinder, Amass, Assetfinder et les autres sources alimentent le même inventaire `inventory_subs.txt`. Les doublons sont supprimés et les sources non utilisées sont ignorées.

Si un ancien programme contient encore `subexample.com.txt`, vérifier son contenu avant de le renommer en `subfinder_subs.txt`. Avant la fusion, contrôler les fichiers sources : les erreurs d'API, ports et autres lignes non conformes ne doivent pas être considérés comme des noms de domaine.

Avant la reconnaissance active, vérifier les résultats au regard du scope et enregistrer uniquement les noms explicitement autorisés dans `all_subs.txt`.

## Formats des résultats

| Fichier | Contenu attendu |
| --- | --- |
| `*_subs.txt`, `wayback_domains.txt` | Noms collectés, à contrôler |
| `inventory_subs.txt` | Fusion dédupliquée, non validée |
| `all_subs.txt` | Noms explicitement autorisés, validés manuellement |
| `wayback_cdx.txt` | URL historiques |
| `observed_ips.txt`, `otx_ips.txt` | IP observées, non validées |

## Avant de poursuivre

<BountyChecklist storage-key="checkpoint-reconnaissance" :items='["Inventaire des actifs recensés.","Actifs autorisés distingués des pistes à vérifier."]' />

---

[Précédent : Programme et préparation](./preparation.md) · [Parcours](./index.md) · [Suivant : Reconnaissance active](./scan-reseau.md)
