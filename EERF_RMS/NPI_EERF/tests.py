from django.test import TestCase

# Create your tests here.
sorted_leader = [u'FATP OTA Testing', u'FATP OTA FA', u'Pre-OTA', u'Field', u'OTA Chambers', u'EMC/ESD',
                 u'EE System', u'OSD', u'Motion sensor', u'Desense', u'BBHW', u'MLB CoEx & Regulatory',
                 u'FATP CoEx & Regulatory', u'RFHW', u'MLB EE', u'MLB WiPAS', u'RF EPM WDPPM', u'AP',
                 u'FATP WiPAS', u'FATP Data', u'Inventory', u'MLB Data', u'MLB RF Stations', u'EE Validation']
new_dict = {u'FATP OTA FA': [3, 0, 0, 3], u'EE System': [2, 0, 0, 2], u'MLB CoEx & Regulatory': [1, 0, 0, 1],
            u'Desense': [1, 0, 0, 1], u'EMC/ESD': [2, 0, 1, 1], u'MLB RF Stations': [4, 1, 2, 2],
            u'AP': [2, 0, 0, 2], u'FATP Data': [2, 0, 0, 2], u'MLB WiPAS': [5, 0, 1, 4],
            u'MLB Data': [3, 0, 1, 2], u'RF EPM WDPPM': [4, 0, 3, 1], u'RFHW': [6, 0, 0, 6],
            u'EE Validation': [5, 0, 1, 4], u'BBHW': [1, 0, 1, 0]}
akeys = new_dict.keys()
akeys.sort_by(sorted_leader)
print new_dict
