---
title: "OSCP · Infrastructures cloud"
description: "Contrôler les droits de lecture sur un compartiment S3."
---

# Infrastructures cloud

## Contrôler un compartiment S3

Dans Bash, utilise AWS CLI et le nom d’un compartiment que tu administres. Les exemples de politique concernent les compartiments S3 à usage général.

### Choisir le compartiment

```bash
read -r -p 'Nom du bucket : ' BUCKET
```

### Vérifier si la liste des objets est publique

`--no-sign-request` tente de lister les objets sans identifiants. Un refus ne renseigne pas sur la lecture d’un objet individuel.

```bash
aws s3 ls "s3://${BUCKET:?Renseigner BUCKET}/" --no-sign-request
```

### Lire la politique avec le compte propriétaire

Utilise une identité configurée dans AWS CLI, rattachée au compte propriétaire, avec le droit `s3:GetBucketPolicy`.

```bash
aws s3api get-bucket-policy --bucket "${BUCKET:?Renseigner BUCKET}" --query Policy --output text
```

### Vérifier un service compatible S3

Indique son URL complète, avec `https://`, puis teste la liste anonyme sur ce service.

```bash
read -r -p 'URL du service S3 : ' ENDPOINT_S3
aws s3 ls "s3://${BUCKET:?Renseigner BUCKET}/" --endpoint-url "${ENDPOINT_S3:?Renseigner ENDPOINT_S3}" --no-sign-request
```

### Lire le statut public de la politique

Le droit `s3:GetBucketPolicyStatus` est requis. Le résultat porte sur la politique du compartiment.

```bash
aws s3api get-bucket-policy-status --bucket "${BUCKET:?Renseigner BUCKET}" --query PolicyStatus.IsPublic --output text
```

## Sources

[AWS CLI, liste S3](https://docs.aws.amazon.com/cli/latest/reference/s3/ls.html) · [AWS, lecture de la politique](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketPolicy.html) · [AWS, statut public de la politique](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketPolicyStatus.html).

Sources d’origine : [notes de krovs](https://github.com/krovs/oscp-notes/blob/main/docs/index.md) et [guide d’Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html#15-cloud-infrastructures).

<!-- notes-krovs-2026 -->
