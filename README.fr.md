[English](README.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md)

![Bible Smart Display](docs/assets/banner-v2.svg)

# Bible Smart Display

**Un verset biblique chaque jour sur votre bureau.**

Pour un **Turing Smart Screen de 3,5 pouces ou un écran USB similaire**.

Ces appareils sont aussi vendus sous le nom **« IPS secondary screen » (écran secondaire IPS)**, notamment sur AliExpress. Cette appellation ne garantit pas la compatibilité : vérifiez les exigences du protocole Revision A ci-dessous.

[Télécharger pour Windows](https://github.com/dgcarr/bibleSmartDisplay/releases/latest) · [État de la compilation](https://github.com/dgcarr/bibleSmartDisplay/actions/workflows/windows.yml) · [GPL v3](LICENSE)

**Traduction au choix · Texte bleu clair · Luminosité réglable · Restauration hors ligne**

L’application récupère la [référence quotidienne de Bible League](https://www.bibleleague.org/verse-of-the-day/), cherche le passage sur Bible Gateway dans la traduction choisie (**CSB** par défaut), puis l’affiche sur votre écran. La taille du texte s’adapte à l’espace disponible.

> [!IMPORTANT]
> **Vérifiez votre écran :** l’application prend en charge le protocole série USB **Revision A, 3,5 pouces, 480 × 320 pixels**. Des écrans d’apparence similaire peuvent utiliser des protocoles différents. Les autres tailles, les modèles Revision B et les moniteurs HDMI ne sont pas pris en charge. [Identifier votre écran (en anglais)](docs/setup.md#compatible-displays)

## Choisir l’installation

| Système | Installation |
| :--- | :--- |
| Windows 10/11 x64 | Application portable, sans installer Python |
| Linux / Raspberry Pi OS | Code source avec Python 3.10 ou ultérieur |
| macOS | Code source avec Python 3.10 ou ultérieur |

Préparez votre écran, un **câble USB permettant le transfert de données** et une connexion internet. Fermez le logiciel du fabricant avant de commencer.

## Windows : trois étapes

1. Ouvrez la [dernière version](https://github.com/dgcarr/bibleSmartDisplay/releases/latest). Sous **Assets**, téléchargez `bibleSmartDisplay-windows-x64.zip`, et non l’archive du code source.
2. Extrayez le ZIP dans votre dossier, par exemple `Documents\bibleSmartDisplay`, puis branchez l’écran sur son port de données.
3. Double-cliquez sur **`Run-display.cmd`**. L’application actualise l’écran une fois, puis se termine. La console reste ouverte pour afficher les messages.

<details>
<summary><strong>Écran introuvable ? Choisissez son port COM</strong></summary>

Ouvrez PowerShell dans le dossier extrait :

```powershell
.\bibleSmartDisplay.exe --list-ports
.\bibleSmartDisplay.exe --port COM3
```

Remplacez `COM3` par le port de votre écran. Si aucun port n’apparaît, consultez les pilotes ci-dessous.

</details>

<details>
<summary><strong>Essayer sans écran ni connexion internet</strong></summary>

```powershell
.\bibleSmartDisplay.exe --demo --preview-only
```

Ouvrez `%LOCALAPPDATA%\bibleSmartDisplay\preview.png` pour voir l’image de test.

</details>

> [!NOTE]
> Il s’agit d’une application portable en console, pas d’un installateur graphique. L’exécutable n’est pas signé. La compilation Windows et les tests automatiques d’aperçu réussissent ; les essais USB avec un écran physique sous Windows/macOS restent à effectuer. L’affichage physique a été vérifié sous Ubuntu.

## Linux

Installez Python 3.10+, Git, la prise en charge de venv et la police DejaVu Sans. Sous Ubuntu/Debian/Raspberry Pi OS, les paquets sont `python3`, `python3-venv`, `python3-pip`, `git` et `fonts-dejavu-core`.

```sh
git clone https://github.com/dgcarr/bibleSmartDisplay.git
cd bibleSmartDisplay
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python outputs/daily-verse/verse_display.py
```

Si la détection échoue, ajoutez `--list-ports`, puis `--port /dev/ttyACM0` avec votre port réel. [Autorisations du port série (en anglais)](docs/setup.md#linux-including-raspberry-pi-os)

## macOS

Installez [Python 3.10+](https://www.python.org/downloads/macos/). Téléchargez ce dépôt avec **Code → Download ZIP**, extrayez-le et ouvrez Terminal dans le dossier contenant `requirements.txt` :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python outputs/daily-verse/verse_display.py
```

Si la détection échoue, utilisez `--list-ports`, puis `--port /dev/cu.usbmodem1234` en remplaçant l’exemple par votre port réel. [Aide macOS (en anglais)](docs/setup.md#macos)

## Pilotes USB

**Si l’écran apparaît déjà comme un port série utilisable, essayez-le avant d’installer un pilote supplémentaire.**

| Appareil / système | Ressource officielle |
| :--- | :--- |
| Écran Turing/TURZX | [Téléchargements du fabricant](https://www.turzx.com/en/category/download/) : choisissez le modèle exact |
| Périphérique USB CDC sous Windows | [Pilote série intégré de Microsoft](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-driver-installation-based-on-compatible-ids) : installation automatique pour les appareils compatibles |
| Windows, puce CH340/CH341 confirmée | [Pilote WCH pour Windows](https://www.wch.cn/downloads/CH341SER_EXE.html) |
| macOS, puce série WCH prise en charge | [Pilote WCH pour Mac et instructions](https://github.com/WCHSoftGroup/ch34xser_macos) |
| Linux | Les appareils compatibles utilisent généralement les pilotes du noyau |

Les pilotes WCH **ne sont pas des pilotes universels pour tous les écrans**. Sous Windows, ouvrez **Gestionnaire de périphériques → Ports (COM et LPT)**. En présence d’un avertissement, consultez **Propriétés → Détails → Numéros d’identification du matériel** pour choisir le bon pilote. [Guide complet (en anglais)](docs/setup.md#windows-usb-drivers)

## Choisir une traduction

Utilisez un [code de version Bible Gateway](https://www.biblegateway.com/versions/). Par exemple, `LSG` pour Louis Segond :

```powershell
.\bibleSmartDisplay.exe --translation LSG
.\bibleSmartDisplay.exe --translation NIV
```

Sous Linux/macOS :

```sh
.venv/bin/python outputs/daily-verse/verse_display.py --translation LSG
```

CSB reste la traduction par défaut. Vous pouvez demander un code de version textuelle, à condition que le passage existe dans cette version. Les éditions disponibles uniquement en PDF ou en audio ne sont pas prises en charge. Certaines langues nécessitent `--font` avec une police adaptée ; les écritures complexes et les longs passages sans espaces ne sont pas entièrement testés.

Pour conserver votre choix, ajoutez l’option à la tâche planifiée ou modifiez la ligne qui lance le programme dans `Run-display.cmd`. `--cached` restaure la dernière traduction enregistrée ; ajoutez `--translation LSG` pour exiger cette version. Un échec de récupération ne remplace jamais discrètement votre traduction par une autre. Le cache conserve un seul passage.

## Personnaliser l’affichage

Les réglages par défaut sont **un texte bleu clair et une luminosité de 50 %** :

```powershell
.\bibleSmartDisplay.exe --color "#ADD8E6" --brightness 50
```

Sous Linux/macOS, placez les mêmes options après `.venv/bin/python outputs/daily-verse/verse_display.py`.

| Option | Fonction |
| :--- | :--- |
| `--brightness 25` | Régler le rétroéclairage de 0 à 100 |
| `--color "#F5F5DC"` | Utiliser du texte beige |
| `--cached` | Restaurer le dernier passage hors ligne |
| `--preview-only` | Enregistrer un aperçu sans l’envoyer à l’écran |
| `--list-ports` | Lister les périphériques série |

Les options s’appliquent uniquement à l’exécution en cours. Ajoutez-les à votre tâche planifiée pour les réutiliser chaque jour. [Réglages et fichiers enregistrés (en anglais)](docs/setup.md#commands-and-settings)

## Actualiser chaque matin

L’application s’exécute une fois puis se termine. Configurez le planificateur de votre système pour une mise à jour quotidienne :

[Planificateur de tâches Windows (en anglais)](docs/setup.md#windows-task-scheduler) · [Cron sous Linux (en anglais)](docs/setup.md#linux-cron) · [Launchd sous macOS (en anglais)](docs/setup.md#macos-launchd)

L’ordinateur doit fonctionner et l’écran être connecté. Le premier téléchargement nécessite internet ; en cas de panne réseau ultérieure, le passage enregistré dans la même traduction peut être réutilisé. Le cache est remplacé à chaque mise à jour et ne s’accumule pas.

## Besoin d’aide ?

| Problème | Première vérification |
| :--- | :--- |
| Écran introuvable | Câble de données, `--list-ports` et pilotes |
| Port occupé | Fermez le logiciel du fabricant et les autres instances |
| Erreur de communication ou image brouillée | Vérifiez le modèle, la résolution et le protocole |
| Aucun passage enregistré | Lancez une fois avec internet, sans `--cached` |
| La fenêtre se ferme | Utilisez `Run-display.cmd` ou un terminal |

[Guide de dépannage (en anglais)](docs/setup.md#troubleshooting) · [Signaler un problème](https://github.com/dgcarr/bibleSmartDisplay/issues) · [Compiler depuis les sources (en anglais)](docs/setup.md#build-the-windows-executable-yourself)

Indiquez votre système d’exploitation, le modèle de l’écran, ses identifiants matériels et le message d’erreur.

---

### Remerciements et licence

Réalisé à l’aide de la documentation du protocole de [turing-smart-screen-python](https://github.com/mathoudebine/turing-smart-screen-python), par Matthieu Houdebine et les contributeurs. Projet indépendant des fabricants. Logiciel sous **[GPL v3](LICENSE)** ; les fichiers provenant du projet d’origine conservent leurs mentions.

Référence quotidienne : [Bible League](https://www.bibleleague.org/verse-of-the-day/). Texte biblique : [Bible Gateway](https://www.biblegateway.com/). Traduction par défaut : Christian Standard Bible © 2017 Holman Bible Publishers. Les autres traductions appartiennent à leurs titulaires respectifs ; le texte biblique n’est pas couvert par la licence du logiciel.
