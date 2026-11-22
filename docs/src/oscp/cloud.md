---
title: "OSCP · Infrastructures cloud"
description: "Vérifications en lecture seule des services de stockage cloud, avec AWS CLI."
---

# Infrastructures cloud

La rubrique cloud du guide d’Emmanuel Solis est indiquée comme *en attente de rédaction*.

**Le guide principal ne fournit pas de commandes pour cette rubrique.** Les exemples ci-dessous sont des compléments rédigés à partir des notes de krovs et de la documentation officielle d’AWS.

[Consulter cette rubrique dans le guide original](https://www.emmanuelsolis.com/oscp.html#15-cloud-infrastructures).

## Stockage S3 : vérifier les accès en lecture

Vérifier uniquement les buckets inclus dans le périmètre. L'option `--no-sign-request` envoie une requête non signée : une erreur `AccessDenied` ne signifie pas que le service est absent. Les commandes ci-dessous n'écrivent aucun objet.

### Lister les objets d'un bucket public

Déterminer si une liste d'objets est accessible sans authentification. La disponibilité dépend de la politique du bucket.

<p class="oscp-command-note">Examiner le contenu visible d’un bucket S3 autorisé.</p>

```bash
aws s3 ls s3://<NOM_BUCKET>/ --no-sign-request
```

### Consulter la politique du bucket

Vérifier la politique si le service l'autorise. Une politique inaccessible doit être signalée comme telle, sans déduire qu'elle n'existe pas.

<p class="oscp-command-note">Lire la politique d'accès S3 si les permissions l’autorisent.</p>

```bash
aws s3api get-bucket-policy --bucket <NOM_BUCKET> --no-sign-request
```

### Interroger un stockage compatible S3

Préciser l'URL du service lorsque le laboratoire utilise un endpoint compatible S3 autre que celui d'AWS.

<p class="oscp-command-note">Lister les objets à partir d’un endpoint S3 précis.</p>

```bash
aws s3 ls s3://<NOM_BUCKET>/ --endpoint-url <URL_ENDPOINT_S3> --no-sign-request
```

### Vérifier le statut d'accès public

Interroger le statut d'accès public calculé à partir de la politique, si l'API l'autorise. Ce résultat doit être corrélé aux autres paramètres de sécurité S3.

<p class="oscp-command-note">Consulter le statut de la politique d'accès public.</p>

```bash
aws s3api get-bucket-policy-status --bucket <NOM_BUCKET> --no-sign-request
```

**Références :** [krovs: notes pratiques](https://github.com/krovs/oscp-notes/blob/main/docs/index.md) · [AWS CLI : s3 ls](https://docs.aws.amazon.com/cli/latest/reference/s3/ls.html) · [AWS CLI : get-bucket-policy](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-bucket-policy.html).

<!-- notes-krovs-2026 -->
