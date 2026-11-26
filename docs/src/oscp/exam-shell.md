---
title: "OSCP · Shell interactif"
description: "Pseudo-terminal Linux et référence de dépannage."
prev: false
next: false
---

# Shell interactif (TTY)

Dans une session shell Linux existante du laboratoire, Python 3 peut ouvrir un pseudo-terminal Bash. Cela ne change pas les privilèges du compte.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

Nécessite Python 3 et Bash. Le pseudo-terminal ne garantit pas une connexion stable.

[Référence complète : terminaux interactifs](./utilitaires.md#améliorer-les-shells-interactifs)

[Retour à Exam Mode](./exam.md)
