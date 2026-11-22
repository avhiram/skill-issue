# Notes CRTO  

**liham** · [Certification CRTO](https://certs.zeropointsecurity.co.uk/97e8bb4c-2937-4c21-bf35-ad5cc17f6cb0#acc.pYBlWQqt)

## Repères OPSEC  

🔴 UNSAFE  
🟠 CAUTION  
🟢 SAFE  

* Les opérations Red Team doivent rester ***undetected*** et éviter de déclencher des ***alertes de sécurité***.  
* Privilégier des techniques **stealthy** qui se fondent dans l’activité normale du système.  
* Exploiter les processus légitimes et les outils natifs avec une approche **Living off the Land (LotL)**.  
* Réutiliser les **credentials**, **tokens** et **tickets** pour effectuer une **impersonation** sans connaître les mots de passe.  
* Imiter l’activité normale afin de limiter les détections par l’**antivirus**.  
* Contourner les protections **endpoint** sans déclencher d’alertes.  

## Préparation à l’examen CRTO — Labs  

1. Installer et préparer Cobalt Strike  
[Cobalt Strike Primer Setup Lab 🕒 30 Minutes | Attacker Desktop | User: Attacker](/labs/2-Cobalt-Strike-Primer.md)  

2. Configurer le **Malleable C2 Profile**, préparer les **payloads** et contrôler les binaires avec **ThreatCheck**.  
[Defence Evasion Lab 🕒 45 Minutes | Attacker, DC, Workstation, Web Server | User: pchilds](/labs/defence-evasion-lab-Malleable.md)  

3. Énumérer les politiques **AppLocker**, **UAC** et **antivirus** du poste avec les credentials fournis.  
[AppLocker Challenge 🕒 45 Minutes | Attacker, DC, Workstation | User: pchilds](/labs/applocker-challenge.md)  

4. Obtenir un **Beacon SYSTEM** depuis le premier poste en utilisant l’accès privilégié.  
[Initial Access Lab 🕒 45 Minutes | Attacker, DC, Workstation | User: pchilds](/labs/Initial-Access-lab.md)  

5. Réaliser une **user impersonation** depuis un Beacon SYSTEM sur la workstation.  
[User Impersonation Lab 🕒 30 Minutes | Attacker, DC, Workstation, Web Server | Users: pchilds, rsteel](/labs/User-Impersonation-lab.md)  

6. Effectuer un **jump** avec l’identité de l’utilisateur et lancer un Beacon sur la cible suivante.  
[Lateral Movement Lab 🕒 30 Minutes | Attacker, DC, Workstation, Web Server | Users: pchilds, rsteel](/labs/Lateral-Movement-lab.md)  

7. Utiliser **S4U** sur un serveur pour effectuer une **admin impersonation**.  
[Constrained Delegation Kerberos Lab 🕒 30 Minutes | Attacker, Workstation, DC, Web Server, File Server | User: pchilds](/labs/Constrained-Delegation-kerberos-lab.md)  

8. Utiliser les permissions du **SQL DB owner** pour effectuer une impersonation avec un payload.  
[SQL Server Lab 🕒 45 Minutes (Attacker, Workstation, DC, SQL 1, SQL 2 | Users: pchilds, rsteel](labs/SQL-Servers-lab.md)  

9. Exploiter **SeImpersonatePrivilege** sur le serveur et se connecter à localhost.  
[SQL Server Lab 🕒 45 Minutes (Attacker, Workstation, DC, SQL 1, SQL 2 | Users: pchilds, rsteel](labs/SQL-Servers-lab.md)  

10. Utiliser une **Parent-Child Trust** et un **Golden Ticket** pour effectuer une impersonation et créer un Beacon.  
[Parent Child Trust Lab 🕒 30 minutes | Attacker, Dublin Workstation, Contoso DC, Dublin DC | User: DUBLIN\sguest](/labs/Parent-Child-Trusts.md)  

11. Mettre en place un **DNS Beacon** sur le Domain Controller pour renforcer la résilience.  
[Elevated Persistence Lab 🕒 30 Minutes | Attacker, DC, Workstation | User: pchilds](/labs/Elevated-Persistence-lab.md)  

12. Utiliser la clé d’une **inter-realm trust** et un Golden Ticket pour lancer un Beacon avec impersonation.  
[Inbound Trust Lab 🕒 30 minutes | Attacker, Contoso Workstation, Partner Jump Server, Contoso DC, Partner DC | User: PARTNER\vwebber](/labs/Inbound-Trusts-lab.md)  

13. Effectuer la phase **Active Directory Discovery**.  
[Discovery Lab 🕒 30 Minutes | Attacker, DC, Workstation | Users: pchilds, rsteel](/labs/Discovery-lab.md)  

15. Utiliser **S4U Constrained Delegation** et l’attribut **Allowed To Delegate To**.  
[Constrained Delegation Kerberos Lab 🕒 30 Minutes | Attacker, Workstation, DC, Web Server, File Server | User: pchilds](/labs/Constrained-Delegation-kerberos-lab.md)  

16. Configurer un **SOCKS proxy** pour réaliser du **pivoting** vers d’autres sous-réseaux.  
[SOCKS Lab 🕒 30 Minutes | Attacker, Workstation, DC | Users: pchilds, rsteel](/labs/pivoting-SOCKS-lab.md)  

17. Étudier **RBCD** et la propriété **Allowed To Act On Behalf Of Other Identity**.  
[Kerberos Resource-Based Constrained Delegation Lab 🕒 30 Minutes | Attacker, Workstation, DC, File Server | User: pchilds](/labs/RBCD-lab.md)  

18. Étudier la **Kerberos Constrained Delegation**, la **Service Name Substitution** et l’option **S4U /altservice**.  
[Kerberos Service Name Substitution Lab 🕒 30 Minutes | Attacker, Workstation, DC, File Server, Web Server | Users: pchilds,rsteel](/labs/Service-Name-Substitution-Kerberos-lab.md)

19. Étudier **S4U2self** et la récupération d’un **TGT**.
[Kerberos S4U2self 🕒 30 Minutes | Attacker, Workstation, DC, Web Server | Users: pchilds,rsteel](/labs/S4U2self-lab.md)  

20. Identifier une mauvaise configuration **Kerberos**, puis effectuer un **Lateral Movement** vers le Domain Controller.  
[Kerberos Challenge 🕒 60 Minutes 🖥️ Attacker, LON-WKSTN-1, LON-DC-1 | Users: pchilds, Administrator, Machine Account 3e7 ](/labs/kerberos-challenge.md)  

## Labs CRTO essentiels  

* [Persistence lab 🕒 30 Minutes 🖥️ Attacker, Workstation, DC | Users: pchilds](/labs/Persistence-lab.md)  
* [Credential Access Challenge 🕒 30 Minutes 🖥️ Attacker, Workstation, DC | Users: pchilds](/labs/credential-access-challenge-commands.md)  
* [Privilege Escalation lab 🕒 30 Minutes 🖥️ Attacker, Workstation, DC | Users: pchilds](/labs/Privilege-Escalation-lab.md)  
* [Kerberos Unconstrained Delegation Lab 🕒 30 Minutes 🖥️ Attacker, Workstation, DC, Web Server | Users: pchilds, dyork](/labs/Unconstrained-Delegation-Kerberos-lab.md)  
* [ESC1 Misconfigured Client Authentication Templates 🕒 30 Minutes 🖥️ Attacker, Workstation, DC, Certificate Authority | User: Administrator](/labs/esc1.md)  
* [ESC8 NTLM Relay to ADCS HTTP Endpoints](/labs/esc8.md)  
* [DPERSIST1 Golden Certificates](/labs/dpersist1.md)  
* [Outbound Trust Lab](/labs/Outbound-Trusts-lab.md)  

----  

## Cours Red Team Ops    

* [Cobalt Strike Primer](/cheatsheets/cobalt-strike-primer.md)  
* [AppLocker](/cheatsheets/applocker.md)  
* [Defence Evasion](/cheatsheets/defense-evasion.md)  
* [Initial Access](/cheatsheets/initial-access.md)  
* [Persistence](/cheatsheets/persistence.md)  
* [Post-Exploitation](/cheatsheets/post-exploitation.md)  
* [Privilege Escalation](/cheatsheets/privilege-escalation.md)  
* [Elevated Persistence](/cheatsheets/elevated-persistence.md)  
* [Credential Access](/cheatsheets/credential-access.md)  
* [User Impersonation](/cheatsheets/user-impersonation.md)  
* [Discovery](/cheatsheets/discovery.md)  
* [Lateral Movement](/cheatsheets/lateral-movement.md)  
* [Pivoting](/cheatsheets/pivoting.md)
* [Kerberos](/cheatsheets/kerberos.md)  
* [Microsoft SQL Server](/cheatsheets/ms-sql-server.md)  
* [Domain Dominance](/cheatsheets/domain-dominance.md)  
* [Active Directory Certificate Services ADCS](/cheatsheets/adcs.md)  
* [Forest & Domain Trusts](/cheatsheets/forest-domain-trusts.md)  

----  

## Informations sur l’examen  

* [Zero Point Security Red Team Ops Course Content](https://www.zeropointsecurity.co.uk/course/red-team-ops)  
* [Consignes de l’examen](/notes/Exam-Instructions.md)  
* [Bibliothèque de commandes](/crto-command-library.md)  

----  

## Outils et ressources de l’Attacker Desktop  

* [DRSAT avec MMC sur un Attacker Desktop hors domaine](https://github.com/CCob/DRSAT/tree/master)  
* [Certify](https://github.com/GhostPack/Certify)  
* [Crystal-Kit Rasta-Mouse evasion primitives](https://github.com/rasta-mouse/Crystal-Kit)  
* [ThreadCheck- Artifact Kit](https://github.com/rasta-mouse/ThreatCheck)  
* [Audit des politiques Windows Defender Application Control — WDACTools](https://github.com/NathanJepson/WDAC-Framework)  
* [.NET Marshal.Copy method called to copy Beacon shellcode](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.copy)  
* [API native WriteProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory)  
* [Obfuscation avec Invoke-Obfuscation](https://github.com/danielbohannon/Invoke-Obfuscation)  
* [Beacon Memory — exporter la DLL Beacon avant obfuscation](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_hooks.htm#BEACON_RDLL_GENERATE)
* [Comportement des commandes Beacon — import de BOF](https://github.com/trustedsec/CS-Situational-Awareness-BOF)  
* [Cobalt Strike User Guide - PowerShell_Command & _Compress](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_hooks.htm#POWERSHELL_COMMAND)  
* [Elevate Kit](https://github.com/Cobalt-Strike/ElevateKit)  
* [Cobalt Strike User Guide - beacon_exploit_register](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics_aggressor-scripts/as-resources_functions.htm#beacon_exploit_register)  
* [Template de payload pour DLL side-loading](https://github.com/FuzzySecurity/DLL-Template)  
* [Rasta Mouse - .NET Startup Hooks](https://rastamouse.me/net-startup-hooks/)  
* [GadgetToJScript — créer un dropper JavaScript depuis une assembly .NET](https://github.com/med0x2e/GadgetToJScript)  
* [Exploitation d’un fichier batch exécuté par double-clic](https://github.com/frostb1ten/CVE-2024-24576-PoC)  
* [GrimResource — exécution JavaScript via un fichier .msc spécialement conçu](https://gist.github.com/joe-desimone/2b0bbee382c9bdfcac53f2349a379fa4)  
* [CyberChef — payload XML avec VBScript et cmd.exe](https://gchq.github.io/CyberChef/#recipe=URL_Encode(false)&input=PD94bWwgdmVyc2lvbj0nMS4wJz8%2BDQo8c3R5bGVzaGVldA0KICAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L1hTTC9UcmFuc2Zvcm0iIHhtbG5zOm1zPSJ1cm46c2NoZW1hcy1taWNyb3NvZnQtY29tOnhzbHQiDQogICAgeG1sbnM6dXNlcj0icGxhY2Vob2xkZXIiDQogICAgdmVyc2lvbj0iMS4wIj4NCiAgICA8b3V0cHV0IG1ldGhvZD0idGV4dCIvPg0KICAgIDxtczpzY3JpcHQgaW1wbGVtZW50cy1wcmVmaXg9InVzZXIiIGxhbmd1YWdlPSJWQlNjcmlwdCI%2BDQogICAgPCFbQ0RBVEFbDQogICAgICAgIFNldCB3c2hzaGVsbCA9IENyZWF0ZU9iamVjdCgiV1NjcmlwdC5TaGVsbCIpDQogICAgICAgIHdzaHNoZWxsLnJ1biAiQzpcXFdpbmRvd3NcXFN5c3RlbTMyXFxjbWQuZXhlIg0KXV0%2BPC9tczpzY3JpcHQ%2BDQo8L3N0eWxlc2hlZXQ%2B&ieol=CRLF&oeol=CRLF)  
* [SharpUp GhostPack](https://github.com/GhostPack/SharpUp)  
* [PowerSploit](https://github.com/PowerShellMafia/PowerSploit)  
* [Ghidra](https://github.com/NationalSecurityAgency/ghidra)  
* [IDA free](https://hex-rays.com/ida-free)  
* [dotPeek jetbrains decompiler](https://www.jetbrains.com/decompiler/)  
* [dnSpy](https://github.com/dnSpy/dnSpy)  
* [ysoserial](https://github.com/pwntester/ysoserial.net)  
* [ired.team notes](https://www.ired.team/)  
* [Kerbeus-BOF — Beacon Object Files pour Kerberos](https://github.com/RalfHacker/Kerbeus-BOF)  
* [BOFHound — convertir les résultats LDAP en JSON compatible BloodHound](https://github.com/coffeegist/bofhound)  
* [pyldapsearch](https://github.com/Tw1sm/pyldapsearch)
* [ldapsearch](https://github.com/trustedsec/CS-Situational-Awareness-BOF/tree/master)  
* [AzureHound pour le Cloud](https://bloodhound.specterops.io/collect-data/ce-collection/azurehound)  
* [RustHound-CE](https://github.com/g0h4n/RustHound-CE)  
* [LOLBAS - Living Off The Land Binaries, Scripts and Libraries](https://lolbas-project.github.io/)  
* [Version BOF de SCShell pour Cobalt Strike, alternative à PsExec](https://github.com/Mr-Un1k0d3r/SCShell/tree/master/CS-BOF)  
* [Considérations OPSEC pour les commandes Beacon](https://www.cobaltstrike.com/blog/opsec-considerations-for-beacon-commands)  
* [PowerUpSQL](https://github.com/NetSPI/PowerUpSQL)  
* [SQLRecon](https://github.com/skahwah/SQLRecon)  
* [SQL-BOF](https://github.com/Tw1sm/SQL-BOF)  
* [go sqlcmd](https://github.com/microsoft/go-sqlcmd)  
* [HeidiSQL](https://github.com/heidisql/heidisql)  
* [SSMS](https://learn.microsoft.com/en-us/ssms/install/install)  


## AdaptixC2  
  
* [AdaptixC2 — Framework GitHub](https://github.com/Adaptix-Framework/AdaptixC2)  
* [AdaptixC2 — Guide d’installation](https://adaptix-framework.gitbook.io/adaptix-framework)

<img src="/images/RedTeamOperationsPractitioner.png" width=400>  

