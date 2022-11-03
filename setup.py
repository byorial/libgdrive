setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': 'base',
    'setting_menu': None,
    'menu': {
        'uri': __package__,
        'name': 'GDrive 라이브러리',
        'list': [
            {
                'uri': 'base',
                'name': '설정',
            },
            {
                'uri': 'log',
                'name': '로그',
            },
        ]
    },
    'default_route': 'normal',
}

from plugin import *
P = create_plugin_instance(setting)

from .mod_base import ModuleBase
P.set_module_list([ModuleBase])
