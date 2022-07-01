# L'avion de Bernard
Bonjour ! 
On vous met à disposition le script qu'on utilise pour aller chercher les infos de vols, générer les images et les poster sur instagram. 
Faites-en bon usage !

# Fonctionnement
Le script va chercher les infos de vol sur l'API OpenSkyNetwork (vous pouvez changer le numéro de l'avion et les dates de recherche), crée une image par vol, et poste l'image sur Instagram. On a aussi codé des hashtags aléatoires, le calcul du CO2 etc... Il envoie le déroulé du script par email à la fin, comme ça pas besoin de surveiller son ordinateur :)

# Aide
Comme on a codé rapidement, le script n'est pas hyper facile à utiliser par tous. Donc on vous conseille de regarder le script du début à la fin pour comprendre comment ça marche.

Avant tout :
- Il vous faut python et les librairies listées en haut du script
- Firefox et le geckodriver correspondant (pour automatiser la navigation)
- Mettre votre instagram en français

A modifier pour que ça marche chez vous :
- ligne 22 : chemin absolu vers le fichier bernard.py
- ligne 39,40,41 : infos sur l'avion
- ligne 46 : chemin absolu vers le geckodriver
- ligne 50 : chemin absolu vers votre profil firefox (pour garder les sessions instagram ouvertes avec des cookies)
- ligne 56,57 : identifiants instagram
- ligne 78,79,80,81 : identifiants mail (pour recevoir confirmation du déroulé du script par mail)
- ligne 107 : URL de votre .json de test (optionnel)
- ligne 314 : changer les dimensions pour adapter la taille de l'image de sortie
