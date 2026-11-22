---
name: diorama-decor
description: Assembler des objets Blender de bibliothèque, poser des matériaux PBR, animer la construction du mobilier et éclairer une maquette isométrique.
---

# Construire avec des objets à l’échelle

Choisir les modèles selon leur silhouette dans la caméra, leur licence et l’échelle des personnages. Conserver la fiche auteur et le fichier d’origine. Les [crédits de production](../../docs/credits.md) nomment les fauteuils, le baby-foot, les végétaux, les écrans, les poissons et les textures. Un [poisson GLB](../../examples/reef-fish.glb) permet d’essayer l’import sans inscription.

À l’import, examiner unité, axe vertical, transformations parentales, limites du maillage, UV et images. Placer le bureau par rapport à l’assise et aux mains. Orienter la normale de l’écran vers les yeux de son utilisateur. Mettre toute la table de jeu sous une racine et conserver les pivots locaux des barres, poignées, figurines et balle. Emballer les textures et rouvrir la copie de livraison.

Animer depuis l’axe physique de chaque objet. Le mur croît depuis sa base, le tapis se déroule depuis son bord et le remplissage de l’aquarium fait monter le niveau tout en déplaçant une vague. Les pièces parentes apparaissent avant les accessoires. Vérifier image par image l’ouverture et les intersections entre les deux murs.

Pour les matériaux PBR, lire la couleur en sRGB et les normales/rugosité en données. L’épaisseur du tube, le diffuseur émissif, son recul par rapport au mur et le halo local déterminent le rendu du néon. Décomposer le logo en groupes de lettres, allumer d’abord quelques segments, puis l’aquarium et la liseuse à des temps différents. Contrôler le détail du mur sur une image de taille web. [Matériau émissif Blender](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/emission.html) · [Catalogues et modèles](../../docs/sources.md)
