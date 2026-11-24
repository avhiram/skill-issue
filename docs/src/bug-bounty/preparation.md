---
title: Programme et préparation
aside: true
prev: false
next: false
---

# Programme et préparation

[Retour au parcours](./index.md)

<BountyTarget />

Objectif : choisir un programme, comprendre les règles et préparer son environnement avant toute requête.

## Choisir un programme

- Identifier un programme ouvert aux signalements et vérifier s'il prévoit une prime.
- Lire les actifs inclus et exclus, les catégories éligibles, les restrictions sur l'automatisation et les consignes de signalement.
- Conserver une copie datée du scope et des règles. Un VDP n'est pas nécessairement rémunéré.
- Séparer chaque programme dans un dossier de travail et utiliser des comptes de test dédiés.

## Dossier de travail

<BountyCommand :source="&quot;mkdir -p \&quot;$HOME/bug-bounty/__BOUNTY_WORKSPACE__\&quot;/{scope,recon,requests,preuves,rapports,javascript} &amp;&amp;\ncd \&quot;$HOME/bug-bounty/__BOUNTY_WORKSPACE__\&quot; &amp;&amp;\ntouch scope/domains.txt&quot;" language="bash" />

Crée un dossier distinct pour la cible et le nom du programme renseignés, puis s'y place. Relancer cette commande lors d'un changement de programme ou de terminal. Les fichiers existants sont conservés.

Renseigner `scope/domains.txt` avec les domaines réellement autorisés, un par ligne. Les inventaires TXT restent à la racine du programme pour préserver les enchaînements. Utiliser `requests/` pour les exports HTTP et JSON, `javascript/` pour les scripts locaux, `preuves/` pour les preuves et `rapports/` pour les signalements. Les anciennes variantes qui utilisent des chemins différents indiquent leurs prérequis propres.

### Reprendre un programme existant

<BountyCommand :source="&quot;cd \&quot;$HOME/bug-bounty/__BOUNTY_WORKSPACE__\&quot; &amp;&amp; pwd&quot;" language="bash" />

Ouvre le dossier sélectionné et affiche le chemin courant. Si le dossier n'existe pas encore, utiliser la commande de création ci-dessus.

### Archiver les inventaires

```bash
(
  set -e
  archive=$(mktemp -d recon/inventaires-XXXXXX)
  for f in inventory_subs.txt all_subs.txt resolved_subs.txt http_metadata.txt live_websites.txt all_archived_urls.txt allurls.txt js_inventory.txt; do
    if [ -f "$f" ]; then cp -p -- "$f" "$archive/"; fi
  done
  printf 'Dossier : %s\n' "$archive"
)
```

Copie les inventaires existants dans un nouveau sous-dossier de `recon/`. En cas d'erreur de copie, la commande s'arrête et le dossier partiel reste disponible pour inspection. Les fichiers de travail restent à leur emplacement pour ne pas casser les pipelines. À lancer avec Bash depuis la racine du programme après avoir produit les inventaires.

## Préparer les outils

Consulter [Security Tools et Browser Extensions](./ressources.md). Vérifier les versions installées, les dépendances et les permissions des extensions avant utilisation.

## Vérifier la disponibilité des outils

```bash
for tool in subfinder amass assetfinder findomain chaos dnsx httpx httprobe katana gau waybackurls urlfinder gospider arjun nmap nuclei ffuf curl jq sort grep anew unfurl urldedupe gf dig mktemp cp sha256sum; do
  command -v "$tool" >/dev/null 2>&1 || printf 'Manquant : %s\n' "$tool"
done
```

Liste les outils absents du PATH. Installer seulement ceux utilisés dans la méthode choisie. `httpx` désigne ProjectDiscovery, pas le client Python.

## Avant de poursuivre

<BountyChecklist storage-key="checkpoint-preparation" :items='["Scope et exclusions enregistrés.","Règles du programme vérifiées.","Dossier de travail et comptes de test prêts."]' />

---

[Parcours](./index.md) · [Suivant : Reconnaissance passive](./reconnaissance.md)
