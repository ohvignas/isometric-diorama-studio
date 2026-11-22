# Du fichier vierge au film et à sa boucle

Les commandes suivantes partent du dossier `plugins/isometric-diorama-studio` d’un clone. Python 3.10+, Blender et FFmpeg avec libx264/libvpx sont nécessaires pour suivre tout l’exercice. Les dossiers de sortie doivent être nouveaux. Le template est entièrement local.

```sh
python3 scripts/diorama.py doctor
python3 scripts/diorama.py starter work/atelier.blend
python3 scripts/diorama.py inspect work/atelier.blend --report work/inventaire.json
python3 scripts/diorama.py render work/atelier.blend work/images --first 1 --last 144 --scale 50 --samples 8
python3 scripts/diorama.py encode work/images work/web --first 1 --last 144 --fps 24 --loop-frames 72
```

Ouvrir `work/web/film.mp4`, puis `work/web/boucle.mp4`. À 24 images/s, l’introduction complète dure six secondes et le plan de travail répétable en dure trois. Les WebM contiennent le canal alpha. L’option `--apple` produit aussi `film.alpha.mp4` et `boucle.alpha.mp4` avec VideoToolbox sur macOS. L’option `--background 0xf4f1ec` choisit le fond de lecture H.264. Le rendu final de ce template est en 1280 × 720 à 100 %. La caméra et la résolution se règlent dans le fichier Blender.

## Ajouter un acteur

```sh
python3 scripts/diorama.py inspect exemples-personnels/personnage.glb --report work/acteur.json
python3 scripts/diorama.py import work/atelier.blend exemples-personnels/personnage.glb work/atelier-avec-acteur.blend --name Conceptrice --position 1 0 0
```

La nouvelle racine positionne l’ensemble du modèle. Le rapport donne les armatures, leurs os, les Actions, les dimensions des images et leur disponibilité. Le fichier `examples/reef-fish.glb`, déjà converti en PNG et compatible Blender, permet d’essayer ces deux commandes sans compte Tripo.

## Rejouer le contrôle du mouvement

```sh
SKILL_DIR=skills/blender-tripo-mouvement
blender -b --factory-startup -Y examples/atelier.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/action_humaine.py" -- capture --scene Atelier --rig Mannequin --debut 73 --fin 96 --capture work/clavier.json.gz
blender -b --factory-startup -Y examples/atelier.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/action_humaine.py" -- transfert --scene Atelier --rig Mannequin --capture work/clavier.json.gz --sortie work/action.blend --nom Clavier
blender -b --factory-startup -Y examples/atelier.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/verifier_action.py" -- --capture work/clavier.json.gz --bibliotheque work/action.blend --action Clavier --rapport work/aller-retour.json
blender -b --factory-startup -Y examples/atelier.blend --python-exit-code 5 -P "$SKILL_DIR/scripts/contacts.py" -- --config examples/contacts.json --rapport work/contacts.json
```

Le mannequin original est articulé en FK avec des volumes rigides rattachés aux os. Le dernier contrôle mesure l’immobilité du bureau. Pour mesurer une semelle sur un humanoïde déformable, choisir ses groupes de sommets de pied et la hauteur réelle du sol selon le [schéma des contrôles](../skills/blender-tripo-mouvement/references/commandes.md).

## Sur la page d’accueil

La commande `encode` place un [lecteur](../templates/hero.html), son poster (WebP avec `cwebp`, PNG sinon) et ses sondes de transparence dans le dossier des exports. Depuis le dossier du plugin, lancer `python3 -m http.server 8000 --bind 127.0.0.1 --directory work/web` et ouvrir `http://127.0.0.1:8000`. Le lecteur vérifie deux pixels connus de la sonde avant de choisir le codec, prépare la boucle vers la fin du film et reprend l’introduction après rechargement. Avec la réduction des animations, le poster reste visible jusqu’au clic. Pour une intégration de production, prévoir les versions mobiles et les réponses HTTP partielles. Mesurer les octets transférés et le LCP sur le site réel.
