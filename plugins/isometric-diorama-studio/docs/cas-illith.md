# Comment le coworking Illith a été réalisé

Le film livré contient 2 157 images à 24 i/s. Dans la scène de production, la plage va de 101 à 2257 inclus. Le temps vidéo d’une image Blender se calcule avec `(image - 101) / 24`. La boucle reprend les images 2186 à 2257, soit 72 images et trois secondes. Le film et la boucle de visionnage figurent dans la [vitrine](https://github.com/ohvignas/isometric-diorama-studio/tree/main/showcase).

| Passage | Méthode retenue et contrôle |
| --- | --- |
| Construction | Caméra orthographique fixe, légèrement décalée à gauche. Le parquet paraît par rangées. Le mur portant les LED grandit depuis sa base. Les tapis se déroulent, le niveau d’eau monte avec un front de vague. Contrôler les pivots du bas et la progression dans la caméra finale. |
| Éclairage | Départ plus sombre, allumage irrégulier de groupes de lettres de l’enseigne rose, puis des appliques d’aquarium et de la liseuse. Le diffuseur lumineux et l’éclairage du mur ont deux rôles distincts. |
| Arrivée | La conceptrice part de l’allée pendant la construction. À 5,5 s, sa main atteint la poignée et elle ouvre la porte vers l’intérieur. Vérifier la distance main–poignée sur plusieurs images et le passage entre le battant et le chambranle. |
| Rencontre | Un collègue se lève pour la saluer. Trois secondes de conversation avec pictogrammes. La pointe de chaque bulle doit désigner l’orateur en projection caméra. Sur le salut, vérifier la déformation du col, du cou et du visage. |
| Travail et jeu | Les deux collègues masculins jouent au baby-foot. Les mains suivent les poignées et les yeux la balle, puis le visage opposé. Le collègue bouclé reçoit la bulle Claude et revient à son ordinateur. |
| Aquarium, lecture et café | Le collègue auburn nourrit les poissons. La conceptrice va chercher un livre après cette action et s’installe au fauteuil. L’auburn montre le travail à son collègue puis passe au café. Utiliser des points de prise sur le livre, la tasse, le coussin et les sièges. |
| Retour aux bureaux | Les écrans, mains et regards continuent de vivre. Le dernier cycle est livré dans un deuxième fichier. Au rechargement de la page, la construction repart du début. |

La marche finale reprend l’Action `walk` de Xbot, corrigée aux appuis sur la première figurine. La base CMU 07_01 apparaît dans les études préparatoires. Les prises CMU 141_16 et 13_05 ont servi au salut et au lever. Le trio possède trois atlas couleur distincts de 4096 × 4096. Les textures du parquet et de l’enduit sont en 2K. [Étude de mouvement](../skills/blender-tripo-mouvement/references/coworking-illith.md) · [Crédits des décors](credits.md)

## Sortie pour le web

Pour le hero, le film complet et sa boucle ont été livrés en 720p et 1080p avec alpha, avec une version 2560 × 1440 en réserve. La version de lecture H.264 possède un fond. Le projet a été contrôlé dans Chrome et avec le décodeur HEVC Apple. Lors du changement de livraison de 4K vers 1440p, les 1 136 premières images ont été réduites depuis les rendus UHD. La suite a réutilisé les mouvements approuvés en 1080p sur des décors recalculés en 1440p.

Les [fichiers de démonstration](https://github.com/ohvignas/isometric-diorama-studio/tree/main/showcase) comprennent le film, le poster et la boucle du coworking. Le [fichier Blender éditable](../examples/atelier.blend) est un nouvel exercice reproductible. Il tient dans le dépôt et utilise un mannequin original et des matériaux créés sur place.

La [scène Blender de production](https://github.com/ohvignas/isometric-diorama-studio/releases/download/v1.1.0/Coworking-Illith-source.blend) contient le coworking complet avec les trois personnages. La [visite illustrée](https://github.com/ohvignas/isometric-diorama-studio/tree/main/showcase/scene) donne les images à explorer.
