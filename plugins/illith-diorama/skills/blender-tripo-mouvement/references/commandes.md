# Capturer, transférer et mesurer

Les exemples utilisent le binaire `blender` dans le PATH. Sur macOS, le binaire de l’application se trouve généralement dans `/Applications/Blender.app/Contents/MacOS/Blender`. Définir `SKILL_DIR` sur le dossier contenant SKILL.md, puis travailler dans un répertoire inscriptible. Ces commandes utilisent Blender en arrière-plan.

## Capturer une prestation

```sh
blender -b --factory-startup -Y source.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/action_humaine.py" -- inventaire
blender -b --factory-startup -Y source.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/action_humaine.py" -- capture --scene "01 · Marche" --rig "Étude · Tripo · armature" --debut 1 --fin 47 --capture marche.json.gz
blender -b --factory-startup -Y cible.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/action_humaine.py" -- transfert --rig "Armature" --capture marche.json.gz --sortie marche-cible.blend --nom "Marche approuvée"
```

L’archive contient les rotations évaluées, les positions du bassin, les repos, les noms et la cadence. Le déplacement des parents de l’armature est inclus par rapport au repère du rig à la première image. Choisir un plan continu, avec échelle uniforme et constante. Reporter le mouvement de racine une seule fois. Pour un cycle sur place, retirer d’abord la trajectoire extérieure sur la copie de travail, puis capturer. Conserver oscillations et rotation du bassin.

Le transfert produit une bibliothèque Blender contenant une Action indépendante. Dans le fichier cible, utiliser **File → Append → marche-cible.blend → Action**, sélectionner l’armature puis choisir l’Action dans l’Action Editor et le slot correspondant dans Blender 4.4+. L’Action utilise des courbes de rotation quaternion. Sur une **copie du rig cible**, sélectionner les os animés en Pose Mode et utiliser **Pose → Rotation Mode → Quaternion (WXYZ)**. Équivalent dans la console Blender, avec l’armature cible active et l’Action assignée :

```python
rig = bpy.context.object
for os_pose in rig.pose.bones:
    os_pose.rotation_mode = 'QUATERNION'
```

Si la même armature lit déjà des clips Euler, garder ce réglage sur une copie dédiée ou convertir et cuire les rotations dans le mode utilisé en production. Rejouer un geste à grande amplitude pour vérifier le slot et le mode. Vérifier le rythme à la cadence cible et le raccord avant affectation à la séquence finale. Le script prend en charge les squelettes FK dont le bassin est la racine et les poses de repos anatomiquement proches. Les clés concernent la translation du bassin et les rotations. Pour les rigs avec contrôleurs, contraintes actives, étirements, translations locales non pelviennes ou poses A/T très différentes, calibrer et cuire la prise avec un outil de transfert dédié. Les mains et la face doivent être vérifiées sur la peau.

Les noms Mixamo avec ou sans un préfixe suivi de deux-points sont reconnus. Pour d’autres conventions, fournir à **chaque** commande son `--noms correspondance.json` avec des paires telles que `{"Hips":"pelvis","LeftUpLeg":"thigh.L", ...}`. Les huit repères requis sont Hips, Head, LeftUpLeg, RightUpLeg, LeftLeg, RightLeg, LeftFoot et RightFoot. Ajouter bras, poignets et doigts à la correspondance pour leurs rotations. Contrôler le nombre d’os effectivement transférés annoncé par l’outil.

## Contrôler les contacts

Exemple de configuration JSON à adapter. Les longueurs sont exprimées en mètres, les résultats en millimètres. Vérifier l’échelle de la scène. Le test de semelle travaille sur un sol horizontal et une topologie constante. Une marche sur tapis, marchepied ou rampe nécessite le niveau de support approprié ou une mesure au raycast sur le support réel.

```json
{
  "scene": "Scene",
  "metres_par_unite": 1,
  "controles": [
    {"nom":"Roues pendant l’absence", "type":"objet_fixe", "objet":"Base du fauteuil", "debut":140, "fin":210, "limites":{"excursion_mm":1,"rotation_deg":0.2}},
    {"nom":"Semelle gauche sur le parquet", "type":"semelle", "rig":"Armature", "groupes":["mixamorig:LeftFoot","mixamorig:LeftToeBase"], "debut":40, "fin":72, "sol_m":0.0, "bande_contact_mm":6, "limites":{"glisse_mediane_mm":2,"penetration_mm":2}}
  ]
}
```

```sh
blender -b --factory-startup -Y plan.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/contacts.py" -- --config controles.json --rapport mesures.json
```

Dupliquer le contrôle de semelle pour le côté droit et séparer chaque coupe. Identifier les groupes sur les vraies chaussures. Un appui repose sur les mêmes sommets déformés près du sol dans deux images consécutives. Sur chaque paire d’images, la mesure prend la médiane des distances horizontales parcourues par les sommets. Un pivot à plat est ainsi détecté même si le pied tourne autour d’un centre fixe. Le rapport donne glisse médiane, pire intervalle, cumul maximal pendant un appui et pénétration. Pour un fauteuil à plusieurs pièces animées, mesurer le châssis, le coussin et les accoudoirs. Une excursion du châssis vide révèle une translation indésirable, même lorsque la chaise finit à son point de départ. Les tolérances de l’exemple sont à adapter à l’échelle. Le script renvoie une erreur sur un dépassement et écrit les mesures avant de sortir.

Pour une collision entre le corps et le mobilier, compléter par un test d’intersection des triangles du personnage déformé et du mobilier aux images de transition. Distinguer les contacts attendus, notamment pantalon contre coussin, des intersections cuisse–accoudoir ou main–plateau. Une paire de boîtes englobantes sert à écarter rapidement les objets éloignés. Une inspection en caméra reste nécessaire pour interpréter les contacts proches.

## Vérifier l’aller-retour sur le donneur

Transférer aussi la capture vers une nouvelle Action du donneur. Rouvrir le fichier donneur dans un processus Blender séparé et vérifier que les quaternions et la position du bassin sont retrouvés aux instants d’origine. Le vérificateur neutralise les parents en mouvement dans cette copie en mémoire, car leur déplacement a déjà été inclus lors de la capture. Il compare les rotations de tous les os capturés et le déplacement du bassin. Les seuils sont modifiables avec `--tolerance-deg` et `--tolerance-mm`.

```sh
blender -b --factory-startup -Y source.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/action_humaine.py" -- transfert --scene "01 · Marche" --rig "Étude · Tripo · armature" --capture marche.json.gz --sortie marche-source.blend --nom "Contrôle marche"
blender -b --factory-startup -Y source.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/verifier_action.py" -- --bibliotheque marche-source.blend --action "Contrôle marche" --capture marche.json.gz --rapport reconstruction.json
```

Les mesures d’appui sur la peau et le contrôle vidéo du nouveau personnage restent à faire séparément après son intégration dans le décor.
