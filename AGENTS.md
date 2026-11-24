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

- Avancement de référence : 7 étapes sur 10 traitées. Les étapes 8 (revue individuelle), 9 (options et dépendances) et 10 (contrôle final/publication) restent ouvertes.
- Décompte de la revue individuelle : 31 blocs sur 114 (blocs de code, commandes dynamiques et exemples textuels), lot Programme et préparation (4), Validation et preuves (1), Rapport (1), Suivi (0), IA (10), Reconnaissance passive (15). Ne pas confondre lecture documentaire et exécution.
- Tests locaux réellement exécutés avec des fichiers fictifs : création de deux espaces, reprise et conservation du scope, archives distinctes, contrôle des outils présents/absents, empreintes SHA-256 (fichiers avec espaces, sous-dossiers, rejet du manifeste vide, détection de modification). Syntaxe MCP vérifiée dans la documentation officielle Claude Code, connexion Burp non testée.
- Reprendre par Reconnaissance active (13 blocs), puis Cartographie Web (37), Tests de vulnérabilités (33). Vérifier les prérequis, commenter les limites des exemples historiques et ne pas annoncer d'exécution réseau non réalisée.
- Lot reconnaissance passive : 14 blocs dynamiques et une fusion examinés ; commandes préservées, explications et formats clarifiés. Fusion testée sur fichiers fictifs : doublons supprimés, fichiers absents ignorés, URL et IP exclues de la fusion. Documentation officielle consultée pour Subfinder, Amass historique, Assetfinder, Findomain, Chaos, HackerTarget, URLScan, Common Crawl, Shodan et Unfurl. API externes non exécutées ; schéma OTX, réponse CRT.sh/CDX et compatibilité des versions à confirmer. Correction de la révision 69199cd9ef9cc4b1b3403320cb2fffd3322e1627.
- À chaque lot, donner les étapes terminées, le nombre de blocs revus et les vérifications réellement effectuées. Ne pas prolonger l'audit après le bilan final sauf nouvelle demande.
