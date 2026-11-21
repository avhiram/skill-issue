# CRTO — Fiches de laboratoire en français

Documentation intégrée à skill-issue. Adaptation des sections consultées dans [CRTO Study Notes](https://github.com/botesjuan/CRTO-Study-Notes), avec attribution. Utiliser uniquement en laboratoire autorisé. Les identifiants et secrets d'exemple du dépôt source ne sont pas reproduits.

## 1. Découverte Active Directory

**Objectif :** inventorier le domaine, ses machines, ses utilisateurs et ses relations, puis examiner la cartographie dans BloodHound.

### Préparer le contexte

La source rappelle que les requêtes LDAP depuis une session Cobalt Strike dépendent du contexte d'authentification Kerberos. Un jeton de connexion réseau peut ne pas transmettre les informations nécessaires aux connexions suivantes.

### Inventorier les machines

```text
ldapsearch (samAccountType=805306369) --attributes name,dnsHostName,operatingSystem
```

- `samAccountType=805306369` : sélectionne les objets ordinateurs.
- `name` : nom de l'objet.
- `dnsHostName` : nom DNS de la machine.
- `operatingSystem` : système déclaré dans Active Directory.

### Inventorier les stratégies de groupe

```text
ldapsearch (&(objectClass=groupPolicyContainer)) --attributes displayName,gPCFileSysPath
```

La requête recherche les objets GPO et renvoie leur nom ainsi que le chemin des fichiers de stratégie.

### Examiner les relations d'approbation

```text
ldapsearch (objectClass=trustedDomain) --attributes trustPartner,trustDirection,trustAttributes,flatName
```

- `trustPartner` : domaine partenaire.
- `trustDirection` : sens de l'approbation.
- `trustAttributes` : propriétés de la relation.

### Visualiser dans BloodHound

Le laboratoire source utilise BOFHound pour convertir les journaux LDAP en données exploitables par BloodHound. Après import, cette requête Cypher liste les GPO :

```cypher
MATCH (n:GPO) RETURN n
```

**Point d'attention :** un résultat LDAP vide ne signifie pas nécessairement que le domaine ne contient aucun objet. Vérifier le contexte d'authentification et les droits.

Source : [Discovery Lab](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/labs/Discovery-lab.md).

## 2. AppLocker — Diagnostic des règles

**Objectif de la fiche :** comprendre le diagnostic de la stratégie AppLocker d'un poste de laboratoire.

### Vérifier le mode PowerShell

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Le résultat peut notamment indiquer `ConstrainedLanguage`. Ce mode ne suffit pas, à lui seul, à décrire toutes les règles AppLocker.

### Afficher la stratégie effective

```powershell
$policy = Get-AppLockerPolicy -Effective
$policy.RuleCollections
```

La stratégie effective permet d'inspecter les collections de règles. Les résultats dépendent du contexte d'exécution et de la configuration du poste.

### Examiner les autorisations des dossiers

```cmd
icacls C:\Windows\Tasks
icacls C:\Windows\Temp
```

`icacls` affiche les listes de contrôle d'accès. Ne pas supposer qu'un dossier est accessible en écriture sans examiner la sortie réelle.

Le laboratoire d'origine va ensuite jusqu'à l'exécution d'une charge Beacon. Cette fiche se concentre sur les contrôles et le diagnostic de configuration.

Source : [AppLocker Challenge](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/labs/applocker-challenge.md).

## 3. Cobalt Strike — Préparation et contrôle du laboratoire

**Objectif :** comprendre les composants nécessaires à la préparation d'un environnement de simulation Red Team.

La source distingue :
1. Le serveur d'équipe et la connexion client.
2. Les profils de communication.
3. Les listeners HTTP, SMB et TCP.
4. Les scripts d'extension.
5. Les étapes de validation du laboratoire.

### Vérifier le fonctionnement du conteneur de laboratoire

```bash
sudo docker logs cobaltstrike-cs-1
```

Cette commande lit les journaux du conteneur nommé dans le laboratoire source. Le nom doit être adapté à l'environnement réel.

### Identifier les paramètres à documenter

Pour chaque listener, noter son **nom**, son **protocole**, son **port**, son **interface d'écoute** et les règles réseau applicables. Ne pas copier des adresses, identifiants ou mots de passe d'un autre laboratoire.

Source : [Cobalt Strike Primer](https://github.com/botesjuan/CRTO-Study-Notes/blob/main/labs/2-Cobalt-Strike-Primer.md).

---

**Statut :** première intégration de trois sections réellement consultées, pas encore traduction exhaustive du dépôt. Les autres sections doivent être inspectées avant intégration.
