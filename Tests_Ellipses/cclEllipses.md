## __Conclusion__

### Fichier ```canny.ipynb``` :

Influence de la valeur de seuils sur la transformation de Canny.

### Fichier ```fitEllipse.py``` :

Voir : https://docs.opencv.org/4.5.3/dd/d49/tutorial_py_contour_features.html

Le fit est graphiquement parfait pour les fichiers propres. L'erreur dans estimation de l'excentricité
est probablement due aux dimensions de l'image (pas parfaitement carrée).

Par contre pour les fichiers avec du bruit, OpenCV n'arrive pas à déterminer les contours et ce, peut importe
le seuil (threshold) rentré. C'est sûrement dû au fait que le bruit est très important ici. Il faut donc trouver
un moyen de le supprimer.

### Fichier ```circle.py``` :

Voir : https://docs.opencv.org/master/da/d53/tutorial_py_houghcircles.html

Détection de cercles