# Active Directory Certificate Services

## De la demande à l’authentification

Un demandeur sollicite un certificat. Le certificate template définit notamment qui peut s’inscrire, comment l’identité est déterminée et quels usages sont prévus. La Certification Authority (CA) traite la demande et signe le certificat si les conditions sont remplies. Lors d’une authentification ultérieure, le service destinataire décide s’il accepte le certificat et à quel compte il l’associe.

Pour expliquer un événement, conserver trois identités distinctes : le demandeur, le sujet inscrit dans le certificat et le compte reconnu par le service. Elles peuvent différer dans un processus d’inscription délégué légitime.

## Lire les catégories ESC

| Catégorie | Point de configuration à examiner | Question de revue |
|---|---|---|
| ESC1 | Identité fournie dans la demande et usage d’authentification | Qui est habilité à inscrire une identité, et qui la contrôle avant émission ? |
| ESC2 | Usages autorisés par le template | Les applications acceptent-elles ce certificat pour davantage d’usages que prévu ? |
| ESC3 | Enrollment Agent | Qui peut demander un certificat pour autrui, et pour quels modèles ? |
| ESC4 | Permissions de modification du template | Quels responsables sont habilités à changer les règles d’émission ? |
| ESC8 | Authentification des services web d’inscription | Comment le point d’accès protège-t-il l’authentification contre le relais NTLM ? |

## Relire une émission

Un journal de la CA peut documenter la demande, le template et la décision d’émission. Il ne prouve pas que le certificat a ensuite servi. Pour établir cet usage, rechercher un événement d’authentification correspondant sur le service concerné et conserver les identifiants disponibles pour rapprocher les observations.

[Exercice sur une demande de certificat](../labs/certificat)
