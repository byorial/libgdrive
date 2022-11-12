from .setup import *
from .libgdrive import LibGdrive

name = 'base'

class ModuleBase(PluginModuleBase):
    db_default = {
        f'{name}_db_version' : '1',
        f'{name}_use_rclone_conf' : 'true',
        f'{name}_rclone_conf_path' : '',
    }

    remote_names = None
    remotes = None

    def __init__(self, P):
        super(ModuleBase, self).__init__(P, name=name)

    def process_menu(self, page, req):
        arg = P.ModelSetting.to_dict()
        try:
            arg['remote_names'] = '|'.join(self.remote_names) if self.remote_names else '|'.join(self.get_remote_names(P.ModelSetting.get(f'{name}_rclone_conf_path')))
        except:
            pass
        try:
            return render_template(f'{__package__}_{name}.html', arg=arg)
        except Exception as e:
            P.logger.error(f'Exception: {str(e)}')
            P.logger.error(traceback.format_exc())
            return render_template('sample.html', title=f'{__package__}/{name}/{page}')

    def process_command(self, command, arg1, arg2, arg3, req):
        if command == 'load_conf':
            conf_path = arg1
            remote_names = self.get_remote_names(conf_path)
            if not self.remote_names: self.remote_names = remote_names
            return jsonify({'remote_names':remote_names})
        elif command == 'auth_test':
            remote_name = arg1;
            ret = self.auth_test(remote_name)
            return jsonify(ret)
        return jsonify('')

    def auth_test(self, remote_name):
        try:
            if not self.remotes: 
                remotes = self.get_remotes(P.ModelSetting.get(f'{name}_rclone_conf_path'))
                self.remotes = remotes

            if remote_name in self.remotes:
                remote = self.remotes[remote_name]

            service = LibGdrive.auth_by_rclone_remote(remote)
            if service: ret = {'ret':'success', 'msg':f'{remote_name} 인증 성공'}
            else: ret = {'ret':'failed', 'msg':f'{remote_name} 인증 실패'}
            return ret
        except Exception as e:
            P.logger.error(f'Exception: {str(e)}')
            P.logger.error(traceback.format_exc())
            return None

    def get_remotes(self, path=None):
        import json
        from flaskfarm.lib.support.base.sub_process import SupportSubprocess
        if not path: path = P.ModelSetting.get(f'{name}_rclone_conf_path')
        command = ['rclone', '--config', path, 'config', 'dump']
        ret = SupportSubprocess.execute_command_return(command, format='json')
        #P.logger.info(f'ret: {ret}')
        for k, v in ret['log'].items():
            if 'token' in v: v['token'] = json.loads(v['token'])
        #self.remotes = ret['log']
        return ret['log']

    def get_remote_names(self, path):
        if not self.remotes: remotes = self.get_remotes(path)
        else: remotes = self.remotes
        remote_names = list(x for x in remotes.keys())
        #P.logger.error(f'remote_names={remote_names}')
        return remote_names

