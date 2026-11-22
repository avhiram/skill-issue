# Discovery dans Active Directory

## Situer un objet

Le domaine définit une partition de l’annuaire. Une Organizational Unit (OU) sert à organiser des objets et peut délimiter une délégation d’administration ou le champ d’une Group Policy. Un groupe de sécurité sert notamment à attribuer des droits. Déplacer un compte dans une OU et l’ajouter à un groupe ont donc des effets différents.

| Champ | Utilité dans un relevé |
|---|---|
| Distinguished Name (DN) | Situer l’objet dans l’arborescence au moment de la collecte. |
| Object GUID | Rapprocher deux observations d’un même objet déplacé ou renommé dans le domaine. |
| SID | Identifier un principal de sécurité dans un access token ou une règle d’accès. |
| SPN | Associer une instance de service à un compte pour Kerberos. |

## Lire une relation

Une appartenance directe relie un compte à un groupe. Une appartenance indirecte passe par un ou plusieurs groupes imbriqués. Pour documenter un droit, conserver la chaîne d’appartenance, la règle d’accès sur l’objet et le contexte de sécurité effectivement utilisé. Une arête sur un graphe d’annuaire décrit une relation issue d’une collecte réalisée à une date donnée.

## Interpréter une Group Policy

Le lien d’une GPO à une OU indique où la stratégie peut s’appliquer. Le résultat sur le poste dépend aussi du périmètre, du filtrage et de l’ordre d’application. Pour un lab, comparer le réglage défini, le résultat de stratégie sur la machine et le comportement observé. Ces trois observations permettent de distinguer une erreur de configuration d’un écart entre stratégie attendue et effective.
