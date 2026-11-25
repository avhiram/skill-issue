---
title: "OSCP · Fondamentaux d’Active Directory"
description: "Domaine, authentification et droits de réplication Active Directory."
---

# Fondamentaux d’Active Directory

## Domaine et contrôleur de domaine

Un domaine regroupe des objets de l’annuaire, dont les comptes, les groupes et les ordinateurs. Un contrôleur de domaine héberge une copie de l’annuaire et fournit notamment les services LDAP et Kerberos.

## Authentification

| Terme | Rôle |
| --- | --- |
| TGT | Ticket initial qui permet au client de demander un ticket pour un service. |
| TGS | Service Kerberos qui délivre les tickets de service. |
| Ticket de service | Ticket présenté au service demandé pour authentifier le client. |
| SPN | Nom qui associe une instance de service au compte sous lequel elle s’exécute. |
| NTLM | Famille de protocoles Windows utilisant notamment un échange de défi et de réponse. |

## Indicateur de compte et droit de réplication

| Nom | Signification |
| --- | --- |
| `DONT_REQ_PREAUTH` | Indicateur de `userAccountControl` qui dispense le compte de préauthentification Kerberos. |
| `DS-Replication-Get-Changes` | Droit étendu permettant de répliquer les modifications d’une partition de l’annuaire. |

[Fonctionnement de Kerberos](https://datatracker.ietf.org/doc/html/rfc4120) · [Indicateurs de compte Microsoft](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/useraccountcontrol-manipulate-account-properties) · [Droit de réplication Microsoft](https://learn.microsoft.com/en-us/windows/win32/adschema/r-ds-replication-get-changes).

## Vérifier l’horloge du poste Linux {#heure-linux}

Sur un poste Linux utilisant systemd, le service de gestion de l’heure doit être accessible.

### Afficher l’heure et le fuseau du poste

Lis l’heure locale, le fuseau et l’état de la synchronisation affichés par systemd.

```bash
timedatectl status
```

### Lire les propriétés de synchronisation

`NTPSynchronized` indique si l’horloge est synchronisée et `TimeUSec` donne l’heure du système.

```bash
timedatectl show -p NTPSynchronized -p TimeUSec
```

[Manuel de timedatectl](https://www.freedesktop.org/software/systemd/man/latest/timedatectl.html) · [Propriétés de timedate1](https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.timedate1.html).

## Time Synchronization & Clock Skew

Kerberos vérifie la cohérence des horodatages. La tolérance habituelle est de 5 minutes, selon la politique du domaine. Un décalage excessif peut provoquer l’erreur `KRB_AP_ERR_SKEW` (Clock skew too great).

### Afficher l’heure UTC

```bash
date -u
```

Affiche l’heure UTC du poste pour comparer les horloges sans confusion liée au fuseau horaire.

### Vérifier le décalage NTP

```bash
ntpdate -q ntp.example.org
```

Interroge un serveur NTP autorisé et affiche le décalage sans modifier l’horloge locale. Remplace le nom d’exemple par celui de ton serveur de temps.

### Activer la synchronisation de l’heure

```bash
sudo timedatectl set-ntp true
```

Active la synchronisation automatique sur un poste Linux compatible systemd disposant d’un service NTP configuré.

### Installer faketime

```bash
sudo apt install faketime
```

Installe faketime sur Debian et les distributions compatibles.

### Simuler une date et une heure

```bash
faketime '2026-11-25 09:30:00' date
```

Simule une date pour la commande `date`, sans modifier l’horloge du système. Utile pour les tests de comportement temporel dans un environnement de laboratoire.

### Simuler un décalage horaire

```bash
faketime '+2h' date
```

Simule un décalage de deux heures pour ce processus uniquement.

### Vérifier que l’heure réelle est inchangée

```bash
date
```

Affiche de nouveau l’heure réelle du système après le test. Faketime ne remplace pas la synchronisation NTP et ne fonctionne pas avec tous les programmes.

[Politique Kerberos Microsoft](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/maximum-tolerance-for-computer-clock-synchronization) · [Manuel faketime](https://manpages.debian.org/trixie/faketime/faketime.1.en.html) · [Manuel ntpdate](https://manpages.debian.org/trixie/ntpsec-ntpdate/ntpdate.8.en.html).

## Fiches associées

- [Énumération Active Directory](ad-enumeration.md)
- [Techniques Active Directory](ad-techniques.md)
- [Mouvement latéral](ad-lateral.md)

Source d’origine : [guide d’Emmanuel Solis](https://www.emmanuelsolis.com/oscp.html).
