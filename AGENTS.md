# Consignes permanentes SKILL-ISSUE

## Academy / Cyber University

- Ne jamais modifier la présentation sans autorisation explicite du propriétaire.
- Conserver la longue page dark purple minimaliste, les chapitres et listes de liens, la boîte à outils, et les deux boutons Parcours gratuit / Parcours complet.
- Ne jamais réintroduire les cartes, la timeline, les boutons de progression ou la présentation historique.
- Pour une demande de contenu, modifier uniquement les données ou la logique de sélection nécessaires, pas le template ni le CSS.
- Vérifier le HTML compilé et les assets référencés, puis le déploiement GitHub Pages. Ne pas confondre un commit de compilation et un déploiement public réussi.

## Publication GitHub Pages - toutes les rubriques

- Incident du 24 novembre 2026 : l'ancienne introduction Bug Bounty restait affichée sur le site public alors que les sources, le HTML et le JavaScript compilés étaient à jour. La republication du HTML et une URL versionnée ont rétabli l'affichage ; la cause exacte (cache ou concurrence des publications) n'a pas été confirmée.
- Ne jamais annoncer une correction publique sur la seule base d'un commit. Vérifier le HTML compilé, le JavaScript associé et la page publique à l'URL réellement utilisée par le visiteur.
- Conserver les protections du workflow pages.yml : contrôle des contenus attendus, identification de la révision source dans le HTML, refus des déploiements obsolètes, vérification de la révision publique après publication.
- Si la publication est bloquée, consulter GitHub Actions et Settings > Pages avant de modifier les contenus. Ne pas réintroduire d'ancienne version pour tenter de résoudre un problème de cache.
- Préférer une seule source de publication (GitHub Actions). Ne retirer la compatibilité avec la publication depuis main qu'après confirmation du réglage Pages. Ne jamais changer le design ou supprimer des sources pour corriger un déploiement.
- Bug Bounty : conserver l'introduction « Cheatsheet, méthodologie, outils et ressources pour le Bug Bounty. », le parcours chronologique avec Reconnaissance passive et Reconnaissance active, et les termes techniques en anglais avec explications en français.

## Cohérence des commandes Bug Bounty

- Distinguer les collectes complémentaires des variantes alternatives et des écrasements accidentels.
- Préserver les pipelines et les fusions volontaires, notamment les ajouts avec anew ou >> et les listes communes dédupliquées.
- Avant de renommer un fichier, vérifier toutes ses références dans les autres chapitres, les commandes et les commentaires.
- Identifier le producteur, le format, les prérequis et le consommateur de chaque fichier. Ne pas confondre domaines, IP, URL, métadonnées et fichiers locaux.
- Conserver les contrôles de scope entre la collecte et les requêtes actives. Ne pas modifier une commande fonctionnelle sans raison.
- Distinguer la vérification documentaire des tests réels ; ne pas affirmer avoir exécuté ou validé les commandes si ce n'est pas le cas.

## Espaces de travail Bug Bounty

- Utiliser un dossier distinct sous ~/bug-bounty pour chaque cible et nom de programme. Le champ dynamique détermine le dossier de préparation ; ne jamais écraser les fichiers de scope existants lors de sa création.
- Les commandes existantes utilisent des chemins relatifs depuis ce dossier. Préserver les enchaînements et avertir de changer de répertoire lors d'un changement de programme. Les inventaires restent à la racine tant que tous leurs producteurs et consommateurs n'ont pas été adaptés ensemble.
- Conserver les checklists locales séparées par programme.

## Suivi de l'audit Bug Bounty

- Avancement de référence : 9 étapes sur 10 traitées. Revue documentaire et contrôle transversal terminés ; la vérification finale du HTML et des assets est réussie, mais l'accès public et les interactions réelles restent non confirmés.
- Décompte de la revue individuelle : 114 blocs sur 114 (blocs de code, commandes dynamiques et exemples textuels), lot Programme et préparation (4), Validation et preuves (1), Rapport (1), Suivi (0), IA (10), Reconnaissance passive (15), Reconnaissance active (13), Cartographie Web (37), Vulnérabilités (33). Ne pas confondre lecture documentaire et exécution.
- Tests locaux réellement exécutés avec des fichiers fictifs : création de deux espaces, reprise et conservation du scope, archives distinctes, contrôle des outils présents/absents, empreintes SHA-256 (fichiers avec espaces, sous-dossiers, rejet du manifeste vide, détection de modification). Syntaxe MCP vérifiée dans la documentation officielle Claude Code, connexion Burp non testée.
- Audit documentaire clôturé. Ne pas relancer des lots de revue sans nouvelle demande. Les variantes historiques non validées restent signalées ; la disponibilité des outils, la connexion aux API, les extensions et la compatibilité des versions nécessitent des tests dans l'environnement utilisateur.
- Lot reconnaissance passive : 14 blocs dynamiques et une fusion examinés ; commandes préservées, explications et formats clarifiés. Fusion testée sur fichiers fictifs : doublons supprimés, fichiers absents ignorés, URL et IP exclues de la fusion. Documentation officielle consultée pour Subfinder, Amass historique, Assetfinder, Findomain, Chaos, HackerTarget, URLScan, Common Crawl, Shodan et Unfurl. API externes non exécutées ; schéma OTX, réponse CRT.sh/CDX et compatibilité des versions à confirmer. Correction de la révision 69199cd9ef9cc4b1b3403320cb2fffd3322e1627.
- Lot reconnaissance active : 13 blocs revus, syntaxe Bash vérifiée (bash -n, 13/13, sans exécution des commandes). Documentation DNSX, HTTPX, paquet Kali, Httprobe, Naabu, Nmap, Masscan, Aquatone et parseur Nmap consultée. Clarification du binaire Kali, des formats et des limitations ; erreurs des variantes historiques Naabu (-SC) et Masscan (nom DNS) signalées, variantes non exécutables telles quelles. Aucun scan réseau ni exécution des outils. Révision 34af0831adad691a2413ab794b5807599009d86d.
- Lot Cartographie Web : 37 blocs lus et examinés statiquement ; mode passif Katana retiré depuis 1.1.1, variantes Arjun avec méthode multiple non documentée signalées. Prérequis, formats et limites précisés, commandes historiques conservées sans les rendre opérationnelles. Documentation consultée : Katana, GAU, Gospider, Hakrawler, Arjun et GF. Cinq contrôles exécutés localement sur fichiers fictifs : fusion archives, filtre paramètres, filtre JS, extensions HTML et en-têtes MIME. Aucun outil réseau ni script tiers exécuté. Révision b1170a217c692f704ffdb18ef9fd78f8228e57d9.
- Lot Vulnérabilités : 33 blocs examinés statiquement, 8 tests locaux effectivement réussis avec des données fictives (git grep, diff, décodage JWS, jq OpenAPI, fichier de test upload, en-têtes frame et cache, extraction URL depuis une sortie fictive). Documentation S3Scanner, WPScan, Git, jq et PortSwigger consultée ; outils de test réseau non exécutés et variantes historiques non validées. La revue documentaire est complète, pas la validation en conditions réelles.
- Bilan final : 114 blocs (92 statiques et 22 dynamiques), 9 checklists, 11 pages sources et compilées contrôlées à la révision fbe2ad37a5be92c1b18d5e84972806f91e7afe9c. Aucun titre strictement répété, bloc de clôture Markdown déséquilibré ou lien/ancre interne manquant détecté dans le contrôle effectué. Les assets lean et complets des cinq pages avec champ cible ont été retrouvés. Tests locaux du dernier lot sur données fictives : deux dossiers indépendants, reprise avec scope et inventaire conservés, deux archives distinctes, empreinte SHA-256 d'un fichier avec espace et détection d'une modification. Accès à trois URL publiques tenté mais indisponible via l'outil web ; ne pas déduire que le site est en panne ni annoncer sa publication confirmée. Les liens externes, les interactions Vue en navigateur et les commandes réseau ne sont pas validés de bout en bout.
- À chaque lot, donner les étapes terminées, le nombre de blocs revus et les vérifications réellement effectuées. Ne pas prolonger l'audit après le bilan final sauf nouvelle demande.
