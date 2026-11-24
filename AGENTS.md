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
