# -*- coding: UTF-8 -*-


#######################################################################
#
# autoexec cristalazul
# ----------------------------------------------------------------------------
# Modificación eliminar indigo del sistema. Proveedor: CTA
# ----------------------------------------------------------------------------
#######################################################################

import shutil
import xbmc




addon_path2 = xbmc.translatePath(('special://home/addons/plugin.video.blackghost')).decode('utf-8')
shutil.rmtree(addon_path2, ignore_errors=True)



