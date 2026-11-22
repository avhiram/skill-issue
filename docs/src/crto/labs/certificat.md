# Relire une demande de certificat

## Objectif et prérequis

Reconstituer une émission de certificat à partir du dossier fictif ci-dessous. L’exercice se fait sur papier. Les deux systèmes concernés sont une CA d’entreprise et un service applicatif.

| Source | Observation |
|---|---|
| CA, 10 h 02 | Le compte LAB-INSCRIPTION demande un certificat pour LAB-ALICE. |
| CA, 10 h 04 | La demande est approuvée. Le numéro de série attribué est 42. |
| Application, 10 h 09 | Le compte LAB-ALICE ouvre une session. Le journal ne précise aucun mode d’authentification. |

## Procédure

1. Relever le demandeur, l’identité portée par le certificat et l’identité enregistrée par l’application.
2. Identifier l’événement qui prouve l’émission du certificat.
3. Déterminer quelle pièce supplémentaire permettrait de relier le certificat à la session.

## Résultat attendu

La CA a émis le certificat après approbation. L’application a enregistré une session pour LAB-ALICE cinq minutes plus tard. Le rapprochement temporel ne démontre pas que le certificat a servi à ouvrir cette session.

## Vérification et dépannage

Dans un relevé réel, chercher le mode d’authentification et un identifiant de certificat dans les journaux appropriés. Un numéro de série s’interprète avec l’identité de la CA émettrice. Si les pièces ne contiennent pas ces informations, conserver les deux événements séparément.

[Relire le fonctionnement d’AD CS](../notes/adcs)
