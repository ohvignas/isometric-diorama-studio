---
name: tripo-personnage
description: Préparer un personnage Tripo Smart Mesh P2.0, identifier le portefeuille, estimer la génération, segmenter, rigger et contrôler ses textures dans Blender.
---

# Construire un seul pilote jusqu’au GLB vérifié

Identifier le compte Studio ou développeur, la région et le budget de ce projet. Une vue entière debout et de face permet de juger silhouette et proportions. Garder les autres vues du même personnage pour les contrôles. Séparer les accessoires que la main devra saisir. Commencer par le sujet le plus difficile à déformer, par exemple des cheveux longs au contact du col.

Avec le CLI API, lancer le plan local ci-dessous. Vérifier le modèle normalisé, les ajustements et les postes non chiffrés. En Studio, relever les coûts affichés pour P2.0, segmentation équilibrée, rig humanoïde et texture demandée. L’autorisation portant sur un autre projet reste attachée à ce projet.

```sh
tripo make personnage.png --model P2.0 --dry-run --json
```

Après validation du compte et du coût, soumettre le pilote. Conserver un identifiant par étape. Une attente interrompue se reprend en consultant le même identifiant. Le preflight initial couvre la géométrie. Pour le **CLI 0.11.2**, la segmentation automatique équilibrée se demande avec `tripo mesh segment "$MODEL_ID" --model v2.0-20260430 -p segmentation_granularity=balanced`. Exécuter `tripo anim check "$RIG_INPUT_ID"`, relire le résultat, puis `tripo anim rig "$RIG_INPUT_ID" --rig-type biped --spec mixamo --out-format glb` sur le modèle éligible. Une tâche de vérification a son propre ID. Garder les fichiers intermédiaires du maillage et du rig.

Pour une retexture demandée, vérifier la commande `tripo model texture --help`. Préparer séparément `tripo model texture "$MODEL_ID" --texture-quality detailed -p pbr=true --dry-run --json` si le projet demande du PBR. Les sorties de rig et de texture peuvent être distinctes. Sur géométrie et UV identiques, rattacher les matériaux à la copie **riggée**. Si la topologie ou les UV changent, transférer les poids et refaire les poses de test. Relever les dimensions réelles des atlas dans Blender avant d’annoncer 4K.

Importer via DCC Bridge ou GLB. Avec `scripts/diorama.py inspect`, vérifier la présence réelle d’os, d’Actions et d’images. Tester coudes à 90°, doigts, rotation de tête, bassin en position assise, col et cheveux. Garder le pilote validé comme étalon du trio. [Connexion et comptes](../../docs/connexion.md) · [Génération P2.0](https://www.tripo3d.ai/tutorials/mesh-game-character-p-2) · [Traitement du rig](https://www.tripo3d.ai/product-doc/module-post-processing/rigging-animation)
