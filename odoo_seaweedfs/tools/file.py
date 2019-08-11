# -*- coding: utf-8 -*-

import requests
import logging
from decorator import decorator
from odoo.exceptions import ValidationError, Warning, UserError, DeferredException

_logger = logging.getLogger(__name__)


def file_server(func):
    def _func(func, self, *args, **kwargs):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        option = ICPSudo.get_param('file.storage.option')
        active = ICPSudo.get_param('file.server.active')

        if not active:
            kwargs['file_server'] = False
            return func(self, *args, **kwargs)

        if not option:
            _logger.info('Please set file storage option！')
            kwargs['file_server'] = False
            return func(self, *args, **kwargs)

        elif option == 'weed':
            master = ICPSudo.get_param('fs.master.url')
            volume = ICPSudo.get_param('fs.volume.url')
            public = ICPSudo.get_param('public.fs.url')

            if not (master and volume and public):
                _logger.info('Please set MASTER and VOLUME file server URL！')
                kwargs['file_server'] = False
                return func(self, *args, **kwargs)

            server = SEAWEEDFS(master, volume, public)
            kwargs['file_server'] = server
            return func(self, *args, **kwargs)
        else:
            _logger.info('%s file storage option need to be realized yet!', option)
            kwargs['file_server'] = False
            return func(self, *args, **kwargs)

    return decorator(_func, func)


class SEAWEEDFS(object):
    """
    定义SEAWEEDFS工具类
    """
    def __init__(self, master, volume, public):
        self.master = master
        self.volume = volume
        self.public = public

    def get_fid(self):
        """
        获取fid
        :return:
        """
        try:
            res = requests.post(self.master+'/dir/assign')
            return res.json()
        except Exception as e:
            _logger.warning(e)
            return {'error_msg': "%s" % e}

    def put_file(self,fid, files):
        """
        文件创建和更新都是这个方法
        :param fid:
        :param files: {'file': ('report', base64.decodebytes(s), 'image/png', {'Expires': '0'})}
        :return:
        """
        try:
            res = requests.put(self.volume+'/'+fid,files=files)
            return res.json()
        except Exception as e:
            _logger.warning(e)
            return {'error_msg': "%s" % e}

    def del_file(self, fid):
        """
        文件删除方法
        :param fid:
        :return:
        """
        try:
            res = requests.delete(self.volume+'/'+fid)
            return res
        except Exception as e:
            _logger.warning(e)
            return {'error_msg': "%s" % e}

    def set_replication_strategy(self, option):
        """
        Rack-Aware and Data Center-Aware Replication
        SeaweedFS applies the replication strategy at a volume level. So, when you are getting a file id, you can specify the replication strategy. For example:
        curl -X POST http://localhost:9333/dir/assign?replication=001

        The replication parameter options are:

        000: no replication
        001: replicate once on the same rack
        010: replicate once on a different rack, but same data center
        100: replicate once on a different data center
        200: replicate twice on two different data center
        110: replicate once on a different rack, and once on a different data center

        :param option:
        :return:
        """
        try:
            res = requests.post(self.master + '/dir/assign'+'?replication=%s' % option)
            return res
        except Exception as e:
            _logger.warning(e)
            return {'error_msg': "%s" % e}

    def server_status(self):
        """
        文件服务器状态
        :return:
        """
        try:
            res = requests.post(self.master + '/dir/status?pretty=y')
            return res.json()
        except Exception as e:
            _logger.warning(e)
            return {'error_msg': "%s" % e}

    def check_url(self, fid):
        res = requests.head(self.volume + '/' + fid)
        if res.status_code == 200:
            return True
        return False

    def file_exists(self, fid):
        res = self.check_url(fid)
        if res:
            try:
                size = res.headers.get("content-length")
                if size:
                    return True
            except Exception as e:
                _logger.warning('check file if exists error message: %s-%s' % (fid, e))
                return False
        return False



