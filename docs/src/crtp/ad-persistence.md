# AD Persistence

Étude des mécanismes de persistance dans Active Directory et des conséquences d'une compromission des identités privilégiées.

## Golden Ticket

Un Golden Ticket est un TGT falsifié à l'aide du secret du compte krbtgt. Les notes soulignent le rôle de ce compte dans la confiance Kerberos et l'importance d'une procédure de rotation contrôlée.

## Silver Ticket

Un Silver Ticket est un ticket de service falsifié. Son périmètre dépend du service et du secret associé, contrairement au TGT.

## Diamond Ticket

Un Diamond Ticket repose sur la modification d'un TGT existant. Le risque est lié à l'intégrité du ticket et à la compromission de clés Kerberos.

### Inventaire des tickets courants

```cmd
klist
```

Affiche les tickets Kerberos mis en cache dans la session courante.

## Skeleton Key

Le document décrit une modification de LSASS sur un contrôleur de domaine susceptible d'affecter l'authentification. La technique n'est pas persistante après redémarrage dans le scénario décrit.

## DSRM

Directory Services Restore Mode est destiné à la restauration d'AD. Protéger les identifiants de restauration et contrôler les changements de configuration associés.

## Custom SSP

Les Security Support Providers participent à l'authentification Windows. Une modification non autorisée peut exposer des secrets ou affecter la confiance dans le système.

## ACL et AdminSDHolder

Les notes présentent AdminSDHolder, les droits de réplication et les descripteurs de sécurité comme surfaces de persistance. La revue des permissions des objets protégés est essentielle.

## WMI, PowerShell Remoting et Remote Registry

Ces interfaces d'administration disposent de leurs propres permissions. Examiner leurs configurations et les modifications non justifiées.

Voir [AD Defense](./defense.md) pour les événements et mesures de protection.
