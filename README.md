# Script - L'avion de Bernard
Bonjour ! 
On vous met à disposition le script qu'on utilise pour aller chercher les infos de vols, générer les images et les poster sur instagram. 
Faites-en bon usage !

# Aide
Comme on a codé rapidement, le script n'est pas hyper facile à utiliser par tous. Donc vous conseille de regarder le script du début à la fin pour comprendre comment ça marche.

Avant tout :
- Il vous faut python et les librairies listés en haut du script
- Firefox et le geckodriver correspondant (pour automatiser la navigation)

A modifier pour que ça marche chez vous :
- ligne 22 : chemin absolu vers le fichier bernard.py
- ligne 39,40,41 : infos sur l'avion
- ligne 46 : chemin absolu vers le geckodriver
- ligne 50 : le chemin absolu vers votre profil firefox (pour garder les sessions instagram ouvertes avec des cookies)
- ligne 56,57 : identifiants instagram
- ligne 78,79,80,81 : identifiants mail (pour recevoir confirmation du déroulé du script par mail)
- ligne 107 : URL de votre .json de test (optionnel)
- ligne 314 : changer les dimensions pour adapter la taille de l'image de sortie
