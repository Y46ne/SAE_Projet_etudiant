from .user import User
from .assure import Assure
from .assureur import Assureur
from .bien import Bien, impacte
from .justificatif import Justificatif

# Les fichiers suivants ne sont pas dans le contexte, mais sont importés ailleurs.
# Assurez-vous qu'ils existent dans le dossier monApp/database/
from .logement import Logement
from .piece import Piece
from .sinistre import Sinistre