---
title: "OSCP · Références"
description: "Consignes officielles de l’examen OSCP+."
---

# Références

## Consignes de l’examen

- [Guide officiel de l’OSCP+](https://help.offsec.com/hc/en-us/articles/360040165632-OSCP-Exam-Guide)
- [Critères du rapport d’examen](https://help.offsec.com/hc/en-us/articles/360046787731-OSCP-Reporting-Requirements)

## Rappels essentiels

- L’examen est à livre ouvert : notes et ressources documentaires autorisées, mais pas de chatbot IA ni de LLM avec accès direct aux prompts.
- Les outils d’exploitation automatique, les outils commerciaux et les techniques de spoofing sont interdits. Vérifier les restrictions précises dans le guide officiel.
- Metasploit et Meterpreter : modules et payload Meterpreter limités à une seule cible ; pivot via Metasploit interdit. Le parcours principal n’en dépend pas. Consulter le guide pour les exceptions (msfvenom et multi/handler).
- Lire les preuves depuis leur emplacement d’origine dans un shell interactif de la cible avec `cat` ou `type` ; une webshell ne suffit pas. Conserver les captures avec l’adresse IP de la cible et soumettre les preuves avant la fin de l’épreuve.
- Un pivot peut être nécessaire ; vérifier les fonctionnalités et restrictions de chaque outil. Ligolo-ng n’est pas explicitement nommé dans la liste non exhaustive de la FAQ.
- Consulter les notes sur la machine surveillée par le proctoring, pas sur un téléphone ou un autre appareil.

[FAQ officielle OSCP+](https://help.offsec.com/hc/en-us/articles/4412170923924-OSCP-Exam-FAQ)

[FAQ proctoring](https://help.offsec.com/hc/en-us/articles/15295546432148-Proctored-Exam-Requirements-FAQ)
