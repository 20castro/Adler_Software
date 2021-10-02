# Adler Software

__Les path utilisés dans Tests_Ellipses ne sont pas absolus__ : ils sont pour l'instant écrit pour OSX et à exécuter depuis le répertoire principal. Il faut donc les adapter.

Le fichier ```Tests_Ellipses/header.py``` est à modifier.
Si l'import de ```cv2``` ne vous pose pas de problème, enlever

```
import sys
sys.path.append(...)
```

Sinon, mettre le bon path.