# Suivi de l’audit OSCP du 22 novembre 2026

**Audit technique partiel.** Les 20 rubriques et l’accueil ont été inventoriés. Sur **1 721 blocs Markdown d’origine**, **105** ont fait l’objet d’un examen individuel et **1 616** restent sans validation technique. Le sélecteur de transferts contenait également **21 encarts** relus, qui ont été réunis avec la fiche.

[Sources de départ](https://github.com/avhiram/skill-issue/tree/4f5c5da5eef7578b5c0f1c5de011392850c10c21/docs/src/oscp) · [Corrections des sources](https://github.com/avhiram/skill-issue/commit/990fe1bdd8e34e6b42fd39a7d89097a3e03d397c) · [Version compilée](https://github.com/avhiram/skill-issue/commit/6e864a33eb17b723952d2030ede2161f14c799d7) · [Compilation GitHub Actions](https://github.com/avhiram/skill-issue/actions/runs/44972088657).

## Fichiers et blocs

[Inventaire exhaustif](inventaire.csv) · [Entrées examinées et justificatifs](commandes.csv) · [Comparaison du site publié](publication.csv) · [Disponibilité des liens de la bibliographie](ressources.csv).

Les numéros et les plages de lignes de l’inventaire permettent de retrouver chaque bloc dans les deux versions ci-dessus. Une entrée désigne une instruction saisie au terminal ou un pipeline complet. Les programmes à l’intérieur d’un pipeline ont été examinés ensemble. Une correction est comptée une fois par bloc initial si son contenu, son explication, son titre ou son emplacement a été corrigé. Les retouches de page, de thème et de bibliographie sont consignées séparément.

| Fichier | Blocs initiaux | Blocs après | Blocs examinés | Entrées initiales examinées | Blocs corrigés | Blocs à examiner | État et motif |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [reconnaissance.md](../../docs/src/oscp/reconnaissance.md) | 222 | 223 | 1 | 2 | 1 | 221 | Partiel · RECO |
| [vulnerabilites.md](../../docs/src/oscp/vulnerabilites.md) | 10 | 10 | 3 | 4 | 3 | 7 | Partiel · VUL |
| [applications-web.md](../../docs/src/oscp/applications-web.md) | 275 | 275 | 0 | 0 | 0 | 275 | Inventaire seul · WEB · restriction d’examen ajoutée |
| [attaques-client.md](../../docs/src/oscp/attaques-client.md) | 45 | 46 | 4 | 6 | 4 | 41 | Partiel · CLIENT |
| [antivirus-metasploit.md](../../docs/src/oscp/antivirus-metasploit.md) | 43 | 43 | 0 | 0 | 0 | 43 | Inventaire seul · EV |
| [mots-de-passe.md](../../docs/src/oscp/mots-de-passe.md) | 137 | 137 | 0 | 0 | 0 | 137 | Inventaire seul · CRED |
| [privileges-windows.md](../../docs/src/oscp/privileges-windows.md) | 247 | 248 | 4 | 5 | 4 | 243 | Partiel · PRIV |
| [privileges-linux.md](../../docs/src/oscp/privileges-linux.md) | 89 | 89 | 2 | 2 | 2 | 87 | Partiel · PRIV |
| [redirection-ports.md](../../docs/src/oscp/redirection-ports.md) | 14 | 14 | 0 | 0 | 0 | 14 | Inventaire seul · PIV |
| [tunneling.md](../../docs/src/oscp/tunneling.md) | 33 | 33 | 0 | 0 | 0 | 33 | Inventaire seul · PIV |
| [ad-theorie.md](../../docs/src/oscp/ad-theorie.md) | 0 | 2 | 0 | 0 | 0 | 0 | Notions relues, deux commandes déplacées ici et documentées |
| [ad-enumeration.md](../../docs/src/oscp/ad-enumeration.md) | 210 | 211 | 3 | 4 | 3 | 207 | Partiel · AD |
| [ad-techniques.md](../../docs/src/oscp/ad-techniques.md) | 103 | 101 | 2 | 2 | 2 | 101 | Partiel · AD |
| [ad-lateral.md](../../docs/src/oscp/ad-lateral.md) | 55 | 55 | 0 | 0 | 0 | 55 | Inventaire seul · LAT |
| [cloud.md](../../docs/src/oscp/cloud.md) | 4 | 5 | 4 | 4 | 4 | 0 | Toutes les commandes relues, AWS simulé |
| [rapport.md](../../docs/src/oscp/rapport.md) | 2 | 3 | 2 | 2 | 2 | 0 | Toutes les commandes relues, capture GNOME documentée |
| [transferts.md](../../docs/src/oscp/transferts.md) | 36 | 40 | 36 | 55 | 36 | 0 | Toutes les commandes relues, Windows natif non testé |
| [utilitaires.md](../../docs/src/oscp/utilitaires.md) | 104 | 112 | 44 | 53 | 44 | 60 | Partiel · MIX |
| [methodologie.md](../../docs/src/oscp/methodologie.md) | 92 | 92 | 0 | 0 | 0 | 92 | Inventaire seul · METH |
| [references.md](../../docs/src/oscp/references.md) | 0 | 0 | 0 | 0 | 0 | 0 | Bibliographie relue, réponses HTTP détaillées |
| [index.md](../../docs/src/oscp/index.md) | 0 | 0 | 0 | 0 | 0 | 0 | Accueil relu, 20 liens de rubrique |
| **Total Markdown** | **1 721** | **1 739** | **105** | **139** | **105** | **1 616** | **Audit partiel** |
| [TransferSelector.vue](../../docs/.vitepress/theme/components/TransferSelector.vue) | 21 | 0 | 21 | 28 | 21 | 0 | Encarts relus et renvoyés aux exemples canoniques |

Une paire de délimiteurs dans le texte source compte pour un bloc d’origine. Dans `mots-de-passe.md`, les fragments aux lignes 179–182 et 186–189 sont accolés à du HTML. VitePress interprète les lignes 182–189 comme un seul bloc. Cela explique l’écart entre les **1 721 paires de délimiteurs** et les **1 720 blocs de code rendus** dans la version de départ. Après modification, on obtient **1 739** paires et **1 738** blocs rendus. Les exemples embarqués du composant Vue sont comptés à part.

## Lecture des statuts

Un bloc « Examiné » a été relu dans son contexte avec son titre, son interpréteur, ses arguments et ses prérequis. Les renvois documentaires et le type d’essai figurent dans `commandes.csv`. Les opérations non exécutées sur leur plateforme sont identifiées. Les essais sur Bash et PowerShell sous Linux ne constituent pas des essais sur Kali ou sur Windows natifs.

Les blocs « Inventorié » gardent leur position et un motif par fichier. Les codes ci-dessous décrivent le contexte de la séquence. Certains blocs de ces séquences peuvent contenir des opérations ordinaires qui n’ont pas été vérifiées séparément. Aucune validation technique n’est attribuée par comptage, comparaison de texte ou rendu du site.

| Motif | Portée du contrôle restant |
| --- | --- |
| AD | Séquences d’énumération et d’attaque AD. Seuls les contrôles administratifs indiqués ont été isolés. |
| LAT | Déplacements latéraux et accès distants en contexte d’intrusion. |
| EV | Évasion antivirus et exploitation avec Metasploit. |
| WEB | Fiche mêlant découverte web, reproduction de vulnérabilités et exploitation. |
| CLIENT | Procédures offensives côté client, hors contrôles de pièces jointes et de raccourcis. |
| METH | Enchaînements opérationnels de la méthodologie offensive. |
| CRED | Procédures de test, d’obtention et de réutilisation d’identifiants. |
| PRIV | Séquences d’élévation de privilèges et exemples qui les entourent. |
| RECO | Reconnaissance et collecte de services en contexte de parcours offensif. |
| PIV | Séquences de redirection, d’accès à d’autres réseaux ou de pivot. |
| MIX | Exemples mélangés à l’accès distant, aux charges utiles ou à l’élévation de privilèges. |
| VUL | Sélection de scripts, recherche et inspection d’exploits dans cette fiche. |

## Corrections principales

- **Transferts**. Les quatre couples de systèmes renvoient aux mêmes exemples que la fiche. Le sens de `get`, de `put` et de SCP est précisé. Les instructions SFTP ont leur propre bloc. Le serveur HTTP sert un dossier dédié. Les mots de passe SMB et FTP sont saisis à l’invite. La procédure Netcat indique la variante OpenBSD et ferme le flux après le dernier octet.
- **AWS S3**. Les tests de liste anonyme sont distingués de la consultation signée des politiques et de leur statut. Les noms de compartiment et les URL ne sont plus interprétés comme des redirections Bash.
- **Active Directory et systèmes**. Les commandes Microsoft RSAT sont regroupées dans leur module. Contrôleurs et approbations ont des titres distincts. Les deux lectures de l’horloge Linux figurent dans les fondamentaux. Les journaux cron, les entrées Run et la portée de Get-HotFix ont été précisés.
- **Utilitaires et rapport**. Les exemples de conversion conservent les octets de départ. L’encodage de formulaire, les cookies, les réponses HTTP et la reprise de transfert ont des libellés propres. Les exemples SHA-256 utilisent un chemin réel. Les raccourcis Windows utilisent le dossier Bureau du profil.
- **Examen**. L’accueil et les fiches concernées signalent les restrictions OffSec relatives à Nessus et SQLmap. La page Rapports renvoie aux consignes officielles de preuve et de remise. [Guide OffSec](https://help.offsec.com/hc/en-us/articles/360040165632-OSCP-Exam-Guide).

## Contrôles exécutés

Le journal des commandes cite un résultat d’exécution sur **79 blocs corrigés ou ajoutés distincts**, dont 22 dans Transferts. La vérification des sorties a été réalisée avec des fichiers témoins et des services locaux. Les numéros ci-dessous sont ceux des blocs après correction.

| Contrôle | Résultat observé | Environnement |
| --- | --- | --- |
| Transferts Linux | SCP envoi, réception et dossier, session SFTP avec `put` et `get`, rsync via SSH, Netcat, HTTP, FTP et WebDAV. Les octets ont été comparés après copie. | Processus Linux distincts sur boucle locale, adresses et ports adaptés. |
| PowerShell | Base64, `Invoke-WebRequest` et `Get-FileHash` ont produit les fichiers ou empreintes attendus. | PowerShell 7.7.0 sur Linux avec chemins adaptés. |
| PowerShell, analyse syntaxique | 27 blocs ont été acceptés par le parseur. | Cette analyse ne charge pas les modules Windows et n’exécute aucune commande AD. |
| S3 | AWS CLI a émis les requêtes signées ou anonymes prévues et interprété les réponses. | AWS CLI 1.46.3, serveur HTTP local simulant S3. Aucun appel à un compte AWS réel. |
| Utilitaires | Valeurs décodées, méthodes, en-têtes, formulaires, cookies, reprise d’un fichier, empreintes, PDF, ELF et certificat ont été contrôlés. | Fichiers témoins et points de terminaison HTTP/HTTPS locaux. Le test `--http2` a observé un repli HTTP/1.1. |
| Portée des tests | Aucune session Windows native, aucun domaine AD, aucun échange SMB/RDP avec un poste Windows et aucune instance Nessus utilisés. | L’accès netlink a empêché `ip -br address` de réussir. Aucune réussite d’exécution n’est inscrite pour ce bloc. |

La preuve d’exécution de `commandes.csv` concerne le **bloc corrigé** désigné dans la même ligne. Un envoi exécuté par curl sous Linux ne valide pas l’exécutable Windows. Le serveur WebDAV, les transferts FTP et SCP, ainsi que les exemples rsync utilisaient des données temporaires. Aucune procédure d’intrusion n’a été exécutée.

## Interface et publication

Chromium a chargé les 21 pages aux largeurs de **320, 390 et 1 440 pixels**. Les 63 combinaisons présentaient un seul titre H1 et aucun débordement horizontal de page après correction. Les quatre couples du sélecteur pointaient vers des ancres présentes. Le bouton de copie du bloc SCP Windows a reproduit le texte attendu aux trois largeurs. Le menu mobile et la recherche en français ont été ouverts et utilisés.

Libellés H2 à H4 identiques relevés à plusieurs endroits d’une même page : `ad-lateral` (2), `applications-web` (6), `methodologie` (2), `mots-de-passe` (1), `privileges-linux` (1), `utilitaires` (6). Le nombre entre parenthèses compte les occurrences au-delà de la première. Ces libellés restent à revoir dans leur contexte.

Pour le commit compilé `6e864a33eb17`, le contenu de 21/21 articles correspond à la reconstruction locale des sources. Les URL normales ont servi un HTML strictement identique pour **21/21 pages**. Les feuilles de style et scripts directement référencés contrôlés totalisent **26/26** fichiers identiques. Les empreintes de chaque HTML figurent dans [publication.csv](publication.csv).

La bibliographie contient 31 liens externes. Lors du GET, 25 ont répondu HTTP 200. Les autres réponses et les redirections sont consignées dans [ressources.csv](ressources.csv). Un code HTTP documente la disponibilité observée et ne valide pas le contenu technique de la ressource.
