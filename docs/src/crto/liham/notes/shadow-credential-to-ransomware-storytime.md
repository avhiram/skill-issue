# Shadow Credentials vers Ransomware — Kill Chain

## Lundi matin

Un e-mail de **phishing** arrive dans la boîte d’une employée des ressources humaines. Elle clique sur un lien et saisit ses credentials sur une fausse page de connexion. L’attaquant obtient son identifiant et son mot de passe, mais le compte utilise la **MFA** : le mot de passe seul ne suffit pas.

## Foothold

⚠️ *L’attaquant dispose également d’un foothold grâce à une macro dans la pièce jointe qu’elle a ouverte.*

## Énumération

💬 **L’attaquant possède désormais un accès peu privilégié à la workstation.**

Il lance **BloodHound** en arrière-plan et analyse les relations Active Directory. Il découvre que le compte de service `svc_backup` dispose du droit **GenericWrite** sur un objet ordinateur nommé `FS01`, le serveur de fichiers.

Il ne connaît pas le mot de passe de `svc_backup`. Dans ce scénario, il n’en a pas besoin.

👉 **C’est ici qu’interviennent les Shadow Credentials.**

Imagine que chaque compte utilisateur ou ordinateur d’Active Directory possède un petit coffre. Habituellement, seule la clé connue du domaine permet de l’ouvrir : un secret associé au hash du mot de passe.

Microsoft a ajouté à Active Directory la fonctionnalité **Key Trust**, utilisée pour l’authentification sans mot de passe. Elle permet d’associer *une clé supplémentaire* à un compte. Celui-ci peut alors accepter le mot de passe d’origine **ou** cette nouvelle clé.

## Exploitation

Dans cette histoire, l’attaquant exploite le droit `GenericWrite` sur `FS01` pour **ajouter sa propre clé**, sans changer le mot de passe du compte. Aucun reset de mot de passe n’a lieu et l’activité passe inaperçue dans le scénario.

🏢 Il dispose désormais d’une clé que le serveur `FS01` peut accepter comme preuve d’identité.

**Il utilise cette clé pour demander un ticket Kerberos au nom de FS01.**

Le Domain Controller reconnaît la clé et délivre un **TGT**. L’attaquant récupère ensuite le **hash NTLM** du compte machine.

Il obtient ainsi les credentials du compte machine `FS01`, sans ouvrir de session interactive sur le serveur ni accéder directement à LSASS.

## Persistence

**Les comptes machines sont des identités du domaine.**

🧱 Avec les credentials de `FS01$`, l’attaquant réalise, dans ce scénario, une attaque de type **DCSync** : certains comptes disposant des permissions nécessaires peuvent demander des données de réplication au Domain Controller. Il récupère le hash `krbtgt` et plusieurs hashes de comptes Domain Admin.

Le domaine est désormais compromis dans cette histoire. Aucun brute force ni nouveau service n’a été nécessaire.

**Vendredi soir : déploiement du ransomware.**

## Ransomware

🎯 Avec les credentials Domain Admin, l’attaquant atteint les serveurs de sauvegarde, puis ceux de production. Il supprime les **Shadow Copies**, chiffre les file shares et dépose une demande de rançon.

Le lundi matin suivant, 3 000 partages sont chiffrés et le serveur de sauvegarde est indisponible.

---

## Pourquoi Shadow Credentials a été décisif

| Étape | Ce qui s’est passé |
|---|---|
| Initial Access | Phishing puis foothold peu privilégié |
| Pivot | Découverte du droit `GenericWrite` sur un objet ordinateur |
| **Abus de Shadow Credentials** | **Ajout d’une clé sur FS01 sans modifier le mot de passe** |
| Escalation | Clé ajoutée → Kerberos TGT → hash NTLM du compte machine |
| Compromission du domaine | Hash machine → DCSync → hashes Domain Admin |
| Impact | Déploiement du ransomware dans le domaine |

---

## L’idée essentielle, sans jargon

> Shadow Credentials ressemble à la création d’une **copie d’un passe-partout** grâce à une fonction prévue pour simplifier l’accès. La serrure et la clé d’origine restent inchangées : personne ne remarque forcément qu’une seconde clé existe.

Les défenseurs surveillent les changements de mots de passe, les nouveaux comptes ou les échecs de connexion. Dans cette histoire, aucun de ces événements ne se produit : l’attaquant a simplement *ajouté une clé supplémentaire à un compte qu’il pouvait modifier*.

---

## Détection et remédiation

La Blue Team peut notamment rechercher :

- `Event ID 5136` — **DS Object Modified**, modification de l’attribut `msDS-KeyCredentialLink`.
- Des requêtes **Kerberos PKINIT** inhabituelles pour des comptes machines.
- La relation BloodHound `AddKeyCredentialLink`.

## Questions pour l’investigation forensique

### Identity & Access

- 🔍 Un compte pouvait-il écrire dans l’attribut `KeyCredentialLink` d’autres objets ?
- Quelle paire de clés a été créée, et par quel compte compromis a-t-elle été ajoutée ?
- Quel compte a été compromis après l’Initial Access pour obtenir les permissions d’écriture ?
- Quels comptes détenaient `GenericWrite` ou `WriteProperty` sur les objets utilisateurs ou ordinateurs ? Ces droits étaient-ils attendus ?
- Des modifications légitimes de `msDS-KeyCredentialLink` existaient-elles déjà dans cet environnement ?
- Quels comptes ont réalisé une authentification **PKINIT** (Certificate / Key Trust Kerberos) ? Était-ce habituel ?

### Timeline & Scope

- ⚠️ Quel est le premier `Event ID 5136` concernant `msDS-KeyCredentialLink` ? Combien de temps avant le ransomware est-il survenu ?
- Plusieurs objets utilisateurs ou ordinateurs ont-ils été ciblés par des Shadow Credentials, ou un seul pivot ?
- Quel délai sépare l’ajout de Shadow Credentials du premier événement DCSync ? La séquence semble-t-elle automatisée ?

### Lateral Movement & Privilege Escalation

- Quel DC a traité la demande de TGT PKINIT ? Son journal KDC (`Event ID 4768`) révèle-t-il une pré-authentification par certificat sur un compte machine ?
- Le compte machine `FS01$` a-t-il réalisé des requêtes de réplication LDAP inhabituelles (`Event ID 4662` et GUID de réplication) ?
- 🔥 D’autres comptes machines ont-ils été utilisés après le premier DCSync, ou l’attaquant est-il passé directement aux credentials Domain Admin ?

### Persistence & Cleanup

- 🧩 Des clés Shadow Credentials sont-elles restées en place après l’attaque ? Vérifier les valeurs `msDS-KeyCredentialLink` dans le contexte de l’environnement.
- Des Golden Tickets ou Silver Tickets ont-ils été créés à partir du hash `krbtgt` ? Vérifier les événements `4769` et les types de chiffrement inhabituels (par exemple `0x17`, RC4).
- Des comptes Domain Admin ou Scheduled Tasks ont-ils été créés pour la persistence avant le ransomware ?

### Initial Access — Phishing Chain

- Quel processus a lancé la macro : `WINWORD.EXE` ou `EXCEL.EXE` ? Quel child process a été créé ?
- 💡 Les logs de la messagerie permettent-ils d’identifier l’expéditeur du phishing et d’éventuelles autres cibles ?

---

> [Shadow Credentials — Hacker Recipes](https://www.thehacker.recipes/ad/movement/kerberos/shadow-credentials)
