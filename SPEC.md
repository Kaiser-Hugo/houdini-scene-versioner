# Houdini Scene Versioner — Cahier des charges (V1)

## 1. Objectif

Outil Houdini qui sauvegarde la scène `.hip` courante en nouvelle version numérotée selon une convention de nommage imposée, sans jamais écraser une version existante. Chaque version est accompagnée de métadonnées (qui, quand, pourquoi) et l'utilisateur peut consulter l'historique et rouvrir n'importe quelle version.

**Pourquoi ne pas utiliser simplement `File > Save with Increment` ?**
Houdini incrémente le nom du fichier, mais ne gère ni commentaire, ni métadonnées, ni historique consultable, ni convention de nommage. L'outil prend le contrôle complet du calcul de version (au lieu de `hou.hipFile.saveAndIncrementFileName()`) pour garantir qu'aucune version existante ne soit écrasée.

## 2. Convention de nommage

```
<shot>_<task>_v<###>.hip
```

| Élément  | Règle                                   | Exemple  |
|----------|-----------------------------------------|----------|
| `shot`   | minuscules, lettres et chiffres         | `sh010`  |
| `task`   | minuscules, lettres et chiffres         | `fx`     |
| version  | `v` + 3 chiffres (padding identique au cache tool) | `v004` |

Exemple complet : `sh010_fx_v004.hip`

- Les versions d'une même scène (même `shot` + `task`) sont dans le même dossier.
- Un nom qui ne respecte pas la convention est considéré comme **non versionné**.

## 3. Fonctionnalités

### F1 — Version up
- Lire le nom de la scène ouverte et en extraire `shot`, `task`, version.
- Sauvegarder la scène sous la version suivante.
- Scène non versionnée (`untitled.hip`, nom libre) : demander `shot` et `task` (avec validation), puis créer `v001`.

### F2 — Sécurité
- Ne jamais écraser un fichier existant.
- La prochaine version = **plus haute version présente sur le disque + 1** (et non version ouverte + 1).
  - Exemple : `v003` ouverte, `v005` existe → création de `v006`.

### F3 — Commentaire
- Un commentaire est demandé à chaque version up. *(À trancher pendant le dev : obligatoire ou facultatif.)*

### F4 — Métadonnées
- Un fichier JSON par version, à côté du `.hip` : `sh010_fx_v004.json`.
- Choisi pour éviter les conflits d'écriture entre plusieurs sessions Houdini.
- Champs :
  - `shot`, `task`, `version`
  - `user`
  - `date` (ISO 8601)
  - `comment`
  - `houdini_version`
  - `source_version` (version à partir de laquelle on a fait le version up, `null` si première version)
  - `frame_range` (début, fin)
- Une version sans JSON (ex. créée à la main) reste listée, avec des métadonnées vides.

### F5 — Historique (panneau PySide)
- Lister toutes les versions de la scène courante dans un tableau : version, date, utilisateur, commentaire.
- Ouvrir la version sélectionnée.
- Si la scène actuelle a des changements non sauvés : proposer *Sauver en nouvelle version / Ignorer / Annuler*.

## 4. Interface

- **Version up** : shelf tool + boîtes de dialogue `hou.ui` (commentaire, saisie shot/task).
- **Historique** : fenêtre PySide (tableau + bouton Ouvrir).
  - Objectif pédagogique : apprendre PySide, très demandé dans les offres de pipeline TD.
  - Vérifier la version de PySide livrée avec Houdini 22 avant de commencer.

## 5. Contraintes techniques

- Houdini 22, Python 3, aucune dépendance externe.
- Distribution via un **package JSON** Houdini.
- **Séparation stricte** :
  - `core` (module pur, n'importe **jamais** `hou`) : parsing/formatage des noms, calcul de la prochaine version, lecture/écriture des JSON, listing des versions.
  - couche Houdini : appels `hou` (sauvegarde, ouverture, dialogues).
  - couche UI : fenêtre PySide.
- Le module `core` est testé avec `pytest` depuis PyCharm, sans Houdini.
- Chemins gérés avec `pathlib` (compatibilité Linux / Windows).

## 6. Hors périmètre V1

- Distinction work / publish
- Verrouillage multi-utilisateur
- Base de données
- Lien avec le cache tool (nommer les caches d'après la version de la scène)

## 7. Critères d'acceptation

- [ ] `sh010_fx_v003.hip` + version up → `sh010_fx_v004.hip` + `sh010_fx_v004.json` créés
- [ ] `v003` ouverte, `v005` existe → `v006` créée, aucun fichier écrasé
- [ ] `untitled.hip` → saisie shot/task → `<shot>_<task>_v001.hip`
- [ ] saisie invalide (`SH 010`, `fx-sim`) refusée avec un message clair
- [ ] historique affiche toutes les versions, y compris celles sans JSON
- [ ] ouverture d'une version avec changements non sauvés → choix proposé
- [ ] tests `pytest` du module `core` verts

## 8. Jalons

1. Module `core` : parsing/formatage + prochaine version + tests
2. Version up dans Houdini (shelf tool, `hou.ui`)
3. Métadonnées JSON + commentaire
4. Fenêtre PySide d'historique + ouverture de version
5. Package, README (avec la section « pourquoi pas Save with Increment »), démo vidéo
