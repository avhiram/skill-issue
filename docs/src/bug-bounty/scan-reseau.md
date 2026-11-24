---
title: Reconnaissance active
aside: true
prev: false
next: false
---

# Reconnaissance active

[Retour au parcours](./index.md)

<BountyTarget />

Identifier les services, ports et technologies des actifs autorisés par le programme.

## Validation DNS et HTTP

Vérifier l'appartenance des noms collectés au scope avant les requêtes actives. Le fichier all_subs.txt doit contenir uniquement les noms validés au chapitre précédent.

### DNS - résolution d'un domaine

<BountyCommand :source="&quot;dig +short __BOUNTY_DOMAIN__ A&quot;" language="bash" />

Interroge les enregistrements A avec `dig`. Le résultat peut également contenir un alias CNAME ; une réponse vide ne prouve pas l'absence du domaine.

### HTTP - en-têtes de réponse

<BountyCommand :source="&quot;curl -I '__BOUNTY_ORIGIN__'&quot;" language="bash" />

Effectue une requête HTTP HEAD et affiche les en-têtes de réponse. Certains serveurs ne traitent pas HEAD comme GET.

### DNSX - validation DNS

```bash
dnsx -l all_subs.txt -silent -o resolved_subs.txt
```

Interroge les enregistrements A par défaut. `resolved_subs.txt` contient les noms résolus, pas une liste d'IP. Une absence de réponse ne démontre pas que l'hôte est inexistant.

### DNSX - résolution inverse

```bash
dnsx -ptr -l ip.txt -resp-only -o reverse_dns.txt
```

Interroge les enregistrements PTR des IP autorisées dans `ip.txt`. `-resp-only` conserve les réponses DNS seules ; `reverse_dns.txt` ne constitue pas une liste d'actifs autorisés.

### HTTPX - métadonnées des services

```bash
httpx -l resolved_subs.txt -p 80,443,8080,8443 -silent -title -sc -ip -o http_metadata.txt
```

Produit `http_metadata.txt` avec URL, titres, codes HTTP et IP. Ce fichier contient des métadonnées, pas uniquement des URL. Le binaire ProjectDiscovery se nomme `httpx-toolkit` dans le paquet Kali, et `httpx` dans l'installation amont ; vérifier le binaire avant utilisation pour éviter la confusion avec Python HTTPX.

### Filtrage des sous-domaines actifs

```bash
cat resolved_subs.txt | httpx-toolkit -ports 80,443,8080,8000,8888 -threads 200 > subexample.coms_alive.txt
```

Variante du même outil ProjectDiscovery, distribuée sous le nom `httpx-toolkit` par Kali. Sortie historique : `subexample.coms_alive.txt`, reprise par la variante Katana. Les ports sélectionnés diffèrent du bloc précédent ; ce n'est pas un deuxième moteur indépendant.

> Exemple historique : concurrence élevée et absence de mode silencieux explicite. Ne pas utiliser tel quel ; vérifier les limites du programme et le contenu du fichier avant toute réutilisation.

### Httprobe - services Web

```bash
cat resolved_subs.txt | httprobe > httprobe_urls.txt
```

Alternative ou complément à HTTPX pour vérifier les services HTTP et HTTPS. Par défaut, Httprobe examine les ports 80 et 443. Sortie : `httprobe_urls.txt`, une URL par ligne.

### Préparer la liste HTTP du chapitre suivant

HTTPX et Httprobe peuvent produire des résultats complémentaires. Regrouper les URL pertinentes, supprimer les doublons, puis conserver uniquement les URL autorisées, une par ligne, dans `live_websites.txt`. Extraire les URL seules des résultats contenant des métadonnées. Ce fichier commun alimente le chapitre Web.

## Scan réseau

### Inventaire des ports avec Naabu

```bash
naabu -list ip.txt -c 50 -nmap-cli 'nmap -sV -SC' -o naabu-full.txt
```

Exemple historique, non validé : `-SC` ne correspond pas à une option Nmap documentée. `-c` règle les workers de Naabu et non le débit réseau. Le fichier `naabu-full.txt` correspond à la sortie Naabu, pas à un rapport Nmap complet. Ne pas exécuter ce bloc tel quel ; Nmap doit être installé et `ip.txt` préparé à partir du périmètre explicitement autorisé.

### Scan complet avec Nmap

```bash
nmap -p- --min-rate 1000 -T4 -A example.com -oA fullscan
```

Exemple historique de scan TCP étendu. `-A` active plusieurs familles de détection et `-oA` produit trois fichiers (`fullscan.nmap`, `fullscan.xml`, `fullscan.gnmap`). Les sorties existantes peuvent être écrasées.

> Exemple historique réservé à l'étude en laboratoire. `--min-rate` est un minimum demandé, pas une limite maximale de débit.

### Scan avec Masscan

```bash
masscan -p0-65535 example.com --rate 100000 -oG masscan-results.txt
```

Exemple historique non exécutable tel quel : Masscan attend une adresse IP ou une plage, pas un nom DNS. `-oG` désigne un rapport au format greppable.

> Débit extrêmement élevé dans l'original ; ne pas exécuter sur des systèmes tiers.

## Reconnaissance visuelle

### Aquatone - captures des services Web

```bash
cat hosts.txt | aquatone
```

Génère des captures et un rapport visuel. Prérequis : `hosts.txt` préparé séparément à partir des services autorisés et navigateur compatible installé. Aquatone est historique ; la compatibilité actuelle n'a pas été testée.

### Cartographie ASN et IP

Identifier les réseaux et les systèmes autonomes associés à une organisation, puis comparer les résultats avec le périmètre explicitement autorisé. Une association ASN, DNS ou IP ne suffit pas à établir qu'un actif peut être testé. Cette étape complète l'énumération des sous-domaines sans répéter les commandes existantes.

### Checklist de reconnaissance

<BountyChecklist storage-key="reconnaissance-generale" :items='["Collecte passive et déduplication des sous-domaines.","Validation DNS et contrôle du scope.","Inventaire HTTP et identification des technologies.","Cartographie ASN/IP et reconnaissance visuelle.","Collecte des URL, paramètres et références JavaScript.","Inventaire des interfaces API et des fonctionnalités.","Vérification manuelle des observations et préparation du rapport."]' />

## Nmap - rapport XML local

```bash
nmap -sV -p 8000,8080 -oX nmap_out.xml 127.0.0.1
```

Produit `nmap_out.xml` avec les observations sur les deux ports du laboratoire local. Les services de test doivent être démarrés pour obtenir des résultats pertinents.

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

Convertit `nmap_out.xml` en `scan.html` sans nouvelle requête. Le script `nmap-parse-output` doit être disponible et exécutable, avec ses dépendances (dont `xsltproc`). La syntaxe de conversion est documentée par son auteur ; le script n'a pas été exécuté ici.

[Script nmap-parse-output](https://github.com/ernw/nmap-parse-output)

## Fichiers du chapitre

- `all_subs.txt` : noms validés manuellement au chapitre précédent.
- `resolved_subs.txt` : noms DNS résolus.
- `http_metadata.txt` : métadonnées HTTPX.
- `subexample.coms_alive.txt` : résultat HTTPX Toolkit, repris par Katana.
- `httprobe_urls.txt` : résultat de la variante Httprobe.
- `live_websites.txt` : liste d'URL validées manuellement pour le chapitre Web.
- `ip.txt`, `hosts.txt` : listes spécifiques à préparer selon le scope.
- `nmap_out.xml` : résultat du scan du laboratoire utilisé par le convertisseur HTML.

## Documentation des outils

- [DNSX](https://docs.projectdiscovery.io/opensource/dnsx/usage) · [HTTPX](https://docs.projectdiscovery.io/opensource/httpx/usage) · [HTTPX Toolkit sous Kali](https://www.kali.org/tools/httpx-toolkit/)
- [Httprobe](https://github.com/tomnomnom/httprobe) · [Naabu](https://docs.projectdiscovery.io/opensource/naabu/usage) · [Nmap](https://nmap.org/book/man.html)
- [Masscan](https://github.com/robertdavidgraham/masscan) · [Aquatone](https://github.com/michenriksen/aquatone)

## Avant de poursuivre

<BountyChecklist storage-key="checkpoint-scan-reseau" :items='["Inventaire des services et technologies observés.","Périmètre confirmé avant de poursuivre."]' />

---

[Précédent : Reconnaissance passive](./reconnaissance.md) · [Parcours](./index.md) · [Suivant : Cartographie Web et API](./cartographie-web.md)
