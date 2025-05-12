# Machine virtuelle

La machine virtuelle décrite dans cette page concerne les sept épreuves suivantes :

* `Poète` (_intro_)
* `Milles Fautes` (_intro_)
* `Il etait une bergere` (_misc_)
* `Atomic Secable` (_Side-Channel and Fault Attacks_)
* `No Divide Just Conquer (1/3)` (_Side-Channel and Fault Attacks_)
* `No Divide Just Conquer (2/3)` (_Side-Channel and Fault Attacks_)
* `No Divide Just Conquer (3/3)` (_Side-Channel and Fault Attacks_)

Ces sept épreuves partagent trois fichiers :
* [`machine.py`](https://fichiers.fcsc.fr/dl/vm/machine.py) : le fichier Python évaluant les instructions de cette machine.
* [`assembly.py`](https://fichiers.fcsc.fr/dl/vm/assembly.py) : un assembleur décrit plus bas.
* [`crypto_accelerator.py`](https://fichiers.fcsc.fr/dl/vm/crypto_accelerator.py) : le fichier contient une implémentation
d'arithmétique modulaire de Montgomery.

L'épreuve d'introduction `Mille Fautes` et l'épreuve `Atomic Secable` utilisent en plus le fichier suivant :
* [`machine_faulted.py`](https://fichiers.fcsc.fr/dl/vm/machine_faulted.py) : le fichier contient une classe fille de la machine pour simuler des fautes (écriture d'une valeur aléatoire dans le registre de destination).

L'épreuve `No Divide Just Conquer` utilise également les deux fichiers suivants :
* [`machine_restricted.py`](https://fichiers.fcsc.fr/dl/no-divide-just-conquer/machine_restricted.py) : le fichier contient des classes filles de la machine afin de restreindre les opérations supportées.
* [`no-divide-just-conquer.py`](https://fichiers.fcsc.fr/dl/no-divide-just-conquer/no-divide-just-conquer.py) : le fichier principal de la série de trois épreuves.

## Assembleur

Un assembleur sommaire écrit en Python est fourni (`assembly.py`) afin de générer le code machine qui sera interprêté (_bytecode_).
Cet assembleur supporte la reconnaissance des étiquettes afin de faciliter les sauts dans le code.
Le caractère pour les commentaires est le `;`.

## Description de la machine virtuelle

La machine contient 16 registres pouvant contenir des nombres d'une taille maximale (par défaut 8192 bits).
Les registres sont numérotés de `0` à `F`.
On utilise un système hexadécimal pour désigner les registres (`RA` au lieu de `R10` par exemple).

Lors de son initialisation, la machine s'attend à recevoir :
1. des valeurs initiales dans ses registres d'entrées, selon les épreuves.
2. une séquence d'instructions qui sera le code interprété par la machine. Cette séquence est découpée en mots de 16 bits dans un tableau, le premier mot étant à l'indice `0` du tableau.

La machine se comporte comme un petit processeur, dont la liste d'opérations supportées est donnée
dans le tableau synthétique suivant.

## Exécution de la machine virtuelle

La machine virtuelle interprète la séquence en commençant par le premier mot de 16 bits qui se trouve à l'adresse `0` de la séquence.

La machine virtuelle positionne toujours le compteur du programme (`PC`) sur la prochaine instruction après le chargement et le décodage d'une instruction.
Après ce chargement, l'instruction est exécutée, mettant à jour les valeurs des registres de la machine.

Afin de prévenir les boucles infinies, le nombre d'instructions pouvant être exécutées est limité (65536 par défaut).

Si la machine rencontre une erreur, elle arrête son exécution. Une erreur peut
être le dépassement de capacité des registres ou bien une des conditions listées
dans le tableau synthétique ci-dessous.

## Débogage

En local, il est possible de déboguer la machine virtuelle à l'aide de la méthode `debugCode`.
Cette méthode affiche l'état de la machine pour chaque instruction.
Libre aux utilisateurs de rediriger cet affichage dans un fichier,
ou de modifier la fonction pour faire du pas à pas sur l'exécution du programme.

## Liste des instructions

### Tableau synthétique

| Family             |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| Operation                  |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| Assembler       | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Updates |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Action                |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| Error |
|--------------------|------------------------------------------------|----------------------------|------------------------------------------------|:----------------|--------------------------------------------------|:-------:|-------------------------------------------------|-----------------------|------------------------------------------------|-------|
| Move               |                                                | Move                       |                                                | `MOV Rj, op2`    |                                                  |    -    |                                                 | `Rj = op2`                       |                                                |                                  |
|                    |                                                | Get RR from coprocessor    |                                                | `MOVRR Rj`       |                                                  |    -    |                                                 | `Rj = RR`                        |                                                | no prior FP                      |
| Load               |                                                | Move from code (`1` word)  |                                                | `MOVCW Rj`       |                                                  |    -    |                                                 | `Rj = @Rj`                       |                                                | `Rj < 0` or `Rj>=l`              |
|                    |                                                | Move from code (`Ri` words)|                                                | `MOVC Rj, Ri`    |                                                  |    -    |                                                 | `Rj = @Rj`                       |                                                | `Rj < 0` or `Rj+Ri>=l` or `Ri<=0`|
| Logical            |                                                | AND                        |                                                | `AND Ro, Rm, Rn` |                                                  |    -    |                                                 | `Ro = Rm & Rn`                   |                                                | `Rm < 0` or `Rn < 0`             |
|                    |                                                | OR                         |                                                | `OR  Ro, Rm, Rn` |                                                  |    -    |                                                 | `Ro = Rm \| Rn`                  |                                                | `Rm < 0` or `Rn < 0`             |
|                    |                                                | XOR                        |                                                | `XOR Ro, Rm, Rn` |                                                  |    -    |                                                 | `Ro = Rm ^ Rn`                   |                                                | `Rm < 0` or `Rn < 0`             |
|                    |                                                | Shift right                |                                                | `SRL Ro, Rm, Rn` |                                                  |    -    |                                                 | `Ro = Rm >> Rn`                  |                                                | `Rn < 0`                         |
|                    |                                                | Shift left                 |                                                | `SLL Ro, Rm, Rn` |                                                  |    -    |                                                 | `Ro = Rm << Rn`                  |                                                | `Rn < 0`                         |
| Arithmetic         |                                                | Bit length                 |                                                | `BTL Rj, Ri`     |                                                  |    -    |                                                 | `Rj = bit_length(Ri)`            |                                                |                                  |
|                    |                                                | Add                        |                                                | `ADD Ro, Rm, Rn` |                                                  |    -    |                                                 | `Ro = Rm + Rn`                   |                                                |                                  |
|                    |                                                | Subtract                   |                                                | `SUB Ro, Rm, Rn` |                                                  | `Z` `C` |                                                 | `Ro = Rm - Rn`                   |                                                |                                  |
|                    |                                                | Comparison                 |                                                | `CMP Rj, Ri`     |                                                  | `Z` `C` |                                                 | `Rj - Ri`                        |                                                |                                  |
|                    |                                                | Multiplication             |                                                | `MUL Ro, Rm, Rn` |                                                  | `Z`     |                                                 | `Ro = Rm * Rn`                   |                                                |                                  |
|                    |                                                | Division                   |                                                | `DIV Ro, Rm, Rn` |                                                  |    -    |                                                 | `Ro = Rm // Rn`                  |                                                | `Rn=0`                           |
|                    |                                                | Exact Division             |                                                | `EDIV Ro, Rm, Rn`|                                                  |    -    |                                                 | `Ro = Rm // Rn`                  |                                                | `Rn<=0` or `Rm<0` or `Rm!=0[Rn]` |
|                    |                                                | GCD                        |                                                | `GCD Ro, Rm, Rn` |                                                  |    -    |                                                 | `Ro = gcd(Rm,Rn)`                |                                                |                                  |
|                    |                                                | Primality Test             |                                                | `MR Rj`          |                                                  | `Z`     |                                                 | `Z=True` if `Rj`is prime         |                                                |                                  |
| Modular            |                                                | Modular reduction          |                                                | `MOD Rj, Ri`     |                                                  |    -    |                                                 | `Rj = Ri mod RD`                 |                                                | `RD<=0`                          |
|                    |                                                | Modular exponentiation     |                                                | `POW Rj, Ri`     |                                                  |    -    |                                                 | `Rj = Ri**RC mod RD`             |                                                | `RD<=0` or `RC < 0`              |
|                    |                                                | Modular inversion          |                                                | `INV Rj, Ri`     |                                                  |    -    |                                                 | `Rj = Ri**(-1) mod RD`           |                                                | `RD<=0`                          |
|                    |                                                | Coprocessor initialisation |                                                | `FP  Rj, Ri`     |                                                  |    -    |                                                 | `FPmodule: Rj` `size: Ri`        |                                                | `Rj&1=0` or `Rj<=0` or `Ri=0`    |
|                    |                                                | Coprocessor initialisation |                                                | `FPRR Ro, Rm, Rn`|                                                  |    -    |                                                 | `RR:Ro` `FPmodule: Rm` `size: Rn`|                                                | `Rm&1=0` or `Rm<=0` or `Rn=0`    |
|                    |                                                | Montgomery Multiplication  |                                                | `MM Ro, Rm, Rn`  |                                                  |    -    |                                                 | `Ro = Rm*Rn/R mod FPmodule`      |                                                |  no prior FP or `Rm<0` or `Rn<0` |
|                    |                                                | Montgomery Multiplication  |                                                | `MM1 Rj, Ri`     |                                                  |    -    |                                                 | `Rj = Ri/R mod FPmodule`         |                                                |  no prior FP or `Rm<0` or `Rn<0` |
|                    |                                                | Montgomery Exponentiation  |                                                | `MPOW Rj, Ri`    |                                                  |    -    |                                                 | `Rj = (Ri/R)**RC*R mod FPmodule` |                                                |  no prior FP or `RC < 0`         |
| Random             |                                                | Random                     |                                                | `RND Rj`         |                                                  |    -    |                                                 | `Rj = rand < 2**(Rj)`            |                                                | `Rj<=0`                          |
| Branch (Absolute)  |                                                | Jump if `Z` set            |                                                | `JZA adest`      |                                                  |    -    |                                                 | `PC = adest if Z=True`           |                                                | `PC>=l` or `PC < 0`              |
|                    |                                                | Jump if `Z` not set        |                                                | `JNZA adest`     |                                                  |    -    |                                                 | `PC = adest if Z=False`          |                                                | `PC>=l` or `PC < 0`              |
|                    |                                                | Jump if `C` set            |                                                | `JCA adest`      |                                                  |    -    |                                                 | `PC = adest if C=True`           |                                                | `PC>=l` or `PC < 0`              |
|                    |                                                | Jump if `C` not set        |                                                | `JNCA adest`     |                                                  |    -    |                                                 | `PC = adest if C=False`          |                                                | `PC>=l` or `PC < 0`              |
|                    |                                                | Jump                       |                                                | `JA adest`       |                                                  |    -    |                                                 | `PC = adest`                     |                                                | `PC>=l` or `PC < 0`              |
| Branch (Relative)  |                                                | Jump if `Z` set            |                                                | `JZR rdest`      |                                                  |    -    |                                                 | `PC += rdest if Z=True`          |                                                | `PC>=l` or `PC < 0`              |
|                    |                                                | Jump if `Z` not set        |                                                | `JNZR rdest`     |                                                  |    -    |                                                 | `PC += rdest if Z=False`         |                                                | `PC>=l` or `PC < 0`              |
|                    |                                                | Jump if `C` set            |                                                | `JCR rdest`      |                                                  |    -    |                                                 | `PC += rdest if C=True`          |                                                | `PC>=l` or `PC < 0`              |
|                    |                                                | Jump if `C` not set        |                                                | `JNCR rdest`     |                                                  |    -    |                                                 | `PC += rdest if C=False`         |                                                | `PC>=l` or `PC < 0`              |
|                    |                                                | Jump                       |                                                | `JR rdest`       |                                                  |    -    |                                                 | `PC += rdest`                    |                                                | `PC>=l` or `PC < 0`              |
| Call (Absolute)    |                                                | Call                       |                                                | `CA adest`       |                                                  |    -    |                                                 | `LR = PC, PC = adest`            |                                                | `PC>=l` or `PC < 0`              |
| Call (Relative)    |                                                | Call                       |                                                | `CR rdest`       |                                                  |    -    |                                                 | `LR = PC, PC += rdest`           |                                                | `PC>=l` or `PC < 0`              |
| Return             |                                                | Return                     |                                                | `RET`            |                                                  |    -    |                                                 | `PC = LR`                        |                                                | `PC>=l` or `PC < 0`              |
| End                |                                                | Stop                       |                                                | `STP`            |                                                  |    -    |                                                 |                                  |                                                |                                  |
| Tabular            |                                                | allocate constants         |                                                | `.word cst, ...` |                                                  |    -    |                                                 |                                  |                                                |                                  |

Notations :

* `Ri  = R[0-9A-F]`
* `Rj  = R[0-9A-F]`
* `Rm  = R[0-7]`
* `Rn  = R[0-7]`
* `Ro  = R[0-7]`
* `op2 = Ri, #[0-9]+, #0x[0-9a-fA-F]+, =[a-zA-Z]+`
* `dest = Ri, [a-zA-Z]+, #[0-9]+, #0x[0-9a-fA-F]+`
* `0 <= adest < 65536`
* `-128 <= rdest < 128`, codé sur un octet signé
* `cst = [0-9]+, 0x[0-9a-fA-F]+`

Après un `#` le nombre doit pouvoir être représenté sur au plus 16 bits.

Registres Spéciaux:
* `RC` est utilisé comme exposant
* `RD` est utilisé comme module
* `RE` est utilisé comme Link Register
* `RF` est utilisé comme Program Counter

### Code exemple

```
abc:                        ;entry point, as first byte of generated bytecode
    MOV     R0, #0x00       ;assign constant value 0 to R0
    MOV     R1, #1          ;assign constant value 1 to R1
    MOV     R2, R1          ;assign R1 to r2
    MOV     R3, =constants  ;assign address of the tabular to R3
    MOVCW   R3              ;read first word from 'constants' tabular
    JR      startLoop       ;jump to relative address startLoop (offset from PC)
loop:
    ADD     R0, R1, R0      ;Add R1 to R0, result in R0. Not updating flags
startLoop:
    SUB     R2, R2, R1      ;subtract R1 (worth 1 here) from R2. Update flags
    JCR     loop            ;relative jump if carry, may be out range of relative offset if body of the loop is too huge
    STP                     ;end of programm

constants:                  ;some constants values
    .word 0x1234, 0x5678, =loop
```

### Détails des instructions

**MOV Rj, op2**

```
Rj = op2
```

**MOV Rj, =label**

```
Rj = @label
```

**AND Ro, Rm, Rn**

```
Ro = Rm & Rn
```

Voir le tableau synthétique pour les conditions d'erreur.

**OR  Ro, Rm, Rn**

```
Ro = Rm | Rn
```

Voir le tableau synthétique pour les conditions d'erreur.

**XOR  Ro, Rm, Rn**

```
Ro = Rm ^ Rn
```

Voir le tableau synthétique pour les conditions d'erreur.

**SRL Ro, Rm, Rn**

```
Ro = Rm >> Rn
```

Voir le tableau synthétique pour les conditions d'erreur.

**SLL Ro, Rm, Rn**

```
Ro = Rm << Rn
```

Voir le tableau synthétique pour les conditions d'erreur.

**BTL Rj, Ri**

```
Rj = bit_len(Ri)
```


**ADD Ro, Rm, Rn**

```
Ro = Rm + Rn
```

**SUB Ro, Rm, Rn**

```
Ro = Rm - Rn
```

Met à jour deux booléens `Z` et `C` :
* `Z = True` si `Rm == Rn`, sinon `Z = False`
* `C = False` si `Rm< Rn`, sinon `C = True`

**MUL Ro, Rm, Rn**

```
Ro = Rm*Rn
```

Met à jour un booléen `Z` :
* `Z = True` si `Rm == 0` ou `Rn == 0`, sinon Z` = False`

**DIV Ro, Rm, Rn**

```
Ro = Rm//Rn = quotient(Rm,Rn)
```

Voir le tableau synthétique pour les conditions d'erreur.

**MOD Rj, Ri**

```
Rj = Ri mod module
```

Voir le tableau synthétique pour les conditions d'erreur.

**POW Rj, Ri**

```
Rj = Ri**exponent mod module
```

Voir le tableau synthétique pour les conditions d'erreur.

**GCD Ro, Rm, Rn**

```
Ro = gcd(Rm,Rn)
```

**INV Rj, Ri**

```
Rj = Ri**(-1) mod module
```

Voir le tableau synthétique pour les conditions d'erreur.

**RND Rj**

```
Rj = random de taille Rj bits (au plus 8192 bits)
```

Voir le tableau synthétique pour les conditions d'erreur.

**CMP Rj, Ri**

Met à jour deux booléens `Z` et `C` :
* `Z = True` si `Rj == Ri`, sinon `Z = False`
* `C = False` si `Rj< Ri`, sinon `C = True`

**MOVCW Rj**

```
Rj = @Rj
```

Lit 1 mot (2 octets) à partir de l'adresse `Rj`.
Le mot à l'adresse `Rj` est le poids fort de la valeur considérée.

Voir le tableau synthétique pour les conditions d'erreur.

**MOVC Rj, Ri**

```
Rj = @Rj
```

`Ri` indique le nombre de mots à lire à partir de l'adresse `Rj`.
Le mot à l'adresse `Rj` est le poids fort de la valeur considérée.

Voir le tableau synthétique pour les conditions d'erreur.

**JZA dest**

```
PC = dest si Z = True
```

Voir le tableau synthétique pour les conditions d'erreur.

**JNZA dest**

```
PC = dest si Z = False
```

Voir le tableau synthétique pour les conditions d'erreur.

**JZR dest**

```
PC += dest si Z = True
```

Voir le tableau synthétique pour les conditions d'erreur.

**JNZR dest**

```
PC += dest si Z = False
```

Voir le tableau synthétique pour les conditions d'erreur.

**JCA dest**

```
PC = dest si C = True
```

Voir le tableau synthétique pour les conditions d'erreur.

**JNCA dest**

```
PC = dest si C = False
```

Voir le tableau synthétique pour les conditions d'erreur.

**JCR dest**

```
PC += dest si C = True
```

Voir le tableau synthétique pour les conditions d'erreur.

**JNCR dest**

```
PC += op2 si C = False
```

Voir le tableau synthétique pour les conditions d'erreur.

**JA dest**

```
PC = dest
```

Voir le tableau synthétique pour les conditions d'erreur.

**JR dest**

```
PC += dest
```

Voir le tableau synthétique pour les conditions d'erreur.

**CA op2**

```
LR = adresse de retour (PC)
PC = dest
```

Voir le tableau synthétique pour les conditions d'erreur.

**CR dest**

```
LR = adresse de retour (PC)
PC += dest
```

Voir le tableau synthétique pour les conditions d'erreur.

**RET**

```
PC = LR
```

Voir le tableau synthétique pour les conditions d'erreur.

**STP**

```
Fin du programme
```

**EDIV Ro, Rm, Rn**

```
Ro = Rm//Rn = quotient(Rm,Rn)
```

Voir le tableau synthétique pour les conditions d'erreur.

**MR Rj**

Met à jour le booléen `Z`:
* `Z = True` si `Rj` est un nombre probablement premier, sinon `Z = False`

**FP Rj, Ri**

Initialise un coprocesseur matériel dédié aux calculs sur l'arithmétique de
Montogmery. La valeur de `Rj` est copiée dans un registre interne désigné
par le nom `FPmodule`. La valeur de `Ri` indique la taille minimale de travail,
en bits. La taille de travail est un multiple de 64 bits, et 3 bits de marge
sont pris par rapport à la taille minimale passée en entrée.
La taille de travail réelle est donc: `WorkingSize = 64*[(Ri+3)//64]`.

À l'initialisation, deux constantes sont calculées. Une constante interne et
la constante `RR` qui vaut `4**WorkingSize mod FPmodule`. `RR` est le carré
modulaire de la constante `R`.

Voir le tableau synthétique pour les conditions d'erreur.

**FPRR Ro, Rm, Rn**

Similaire à la fonction FP, mais où la valeur `RR` est déjà connue, passée
en entrée et n'a donc pas besoin d'être calculée. `Ro` contient la valeur `RR`,
`Rm` contient le module et `Rn` la taille minimale de travail.

Voir le tableau synthétique pour les conditions d'erreur.

**MOVRR Rj**

Copie la valeur `RR` dans le registre `Rj`.

Voir le tableau synthétique pour les conditions d'erreur.

**MM Ro, Rm, Rn**

```
Ro = Rm*Rn/R mod FPmodule
```

Calcule le produit de Montogmery de `Rm` par `Rn`.

Voir le tableau synthétique pour les conditions d'erreur.

**MM1 Rj, Ri**

```
Rj = Ri/R mod FPmodule
```

Calcule le produit de Montogmery de `Ri` par 1.

Voir le tableau synthétique pour les conditions d'erreur.

**MPOW Rj, Ri**

```
Rj = R*(Ri/R)**exposant mod FPmodule
```

Effectue l'exponentiation avec des produits de Montgomery en utilisant
l'exposant stocké dans le registre `RC`.

Voir le tableau synthétique pour les conditions d'erreur.