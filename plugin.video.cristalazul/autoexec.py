# -*- coding: UTF-8 -*-
#######################################################################
# ----------------------------------------------------------------------------
# Modificación eliminar indigo del sistema. Proveedor: CTA
# ----------------------------------------------------------------------------
#######################################################################


import shutil

import xbmc



addon_path = xbmc.translatePath(('special://home/addons/plugin.program.indigo')).decode('utf-8')
addon_path2 = xbmc.translatePath(('special://home/addons/plugin.video.blackghost')).decode('utf-8')



shutil.rmtree(addon_path, ignore_errors=True

shutil.rmtree(addon_path2, ignore_errors=True)

