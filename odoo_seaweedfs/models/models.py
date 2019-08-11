# -*- coding: utf-8 -*-

import base64
import tempfile
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError, Warning, UserError, DeferredException
from odoo.addons.odoo_seaweedfs.tools.file import SEAWEEDFS, file_server
from odoo.addons.odoo_seaweedfs.tools import imghdr

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fs_master_url = fields.Char('MASTER File server')
    fs_volume_url = fields.Char('VOLUME File Server')
    public_fs_url = fields.Char('PUBLIC File Server', help="The url for public to get the resources")
    file_storage_option = fields.Selection([('weed', 'SeaweedFS'), ('other', 'Other')])
    file_server_active = fields.Boolean('Active')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        action_id = self.sudo().env.ref('odoo_seaweedfs.create_ir_attachment')

        res.update(
            fs_master_url=ICPSudo.get_param('fs.master.url'),
            fs_volume_url=ICPSudo.get_param('fs.volume.url'),
            public_fs_url=ICPSudo.get_param('public.fs.url'),
            file_storage_option=ICPSudo.get_param('file.storage.option'),
            file_server_active=action_id.active,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('fs.master.url', self.fs_master_url)
        ICPSudo.set_param('fs.volume.url', self.fs_volume_url)
        ICPSudo.set_param('file.storage.option', self.file_storage_option)
        ICPSudo.set_param('public.fs.url', self.public_fs_url)
        action_id = self.sudo().env.ref('odoo_seaweedfs.create_ir_attachment')
        action_id.active = self.file_server_active,
        ICPSudo.set_param('file.server.active', self.file_server_active)


class ImageMixin(models.AbstractModel):
    _name = 'image.mixin'
    _description = "Image Mixin"
    _rec_name = 'fid'

    image = fields.Binary("Image", attachment=True)
    image_url = fields.Char('Image URL', readonly=True)
    internal_image_url = fields.Char('Internal Image URL', readonly=True)
    fid = fields.Char('Image FID')
    shadow_fid = fields.Char('Images FID', related='fid', readonly=True)
    update_trigger = fields.Char('Trigger')

    _sql_constraints = [
        ('fid_unique', 'UNIQUE(fid)', 'You can not have two images with the same fid !')
    ]

    @api.multi
    @file_server
    def unlink(self, **kwargs):
        file_server = kwargs.get('file_server')
        for rec in self:
            if rec.fid and file_server.file_exists(rec.fid):
                res = file_server.del_file(rec.fid)

        return super(ImageMixin, self).unlink()

    @api.multi
    @file_server
    def _store_image(self, **kwargs):
        file_server = kwargs.get('file_server')
        if not file_server:
            return False

        for rec in self:
            fname = rec.name
            if not file_server:
                return False
            datas = rec.image
            if datas:
                fid = rec.fid
                if not fid:
                    fid = file_server.get_fid().get('fid')

                image_url = file_server.public + '/%s' % fid
                internal_image_url = file_server.volume + '/%s' % fid
                val = {
                    'fid': fid,
                    'image_url': image_url,
                    'internal_image_url': internal_image_url
                }
                rec.update(val)
                data = str.encode(datas) if isinstance(datas, str) else datas
                fp = base64.decodebytes(data)
                type = imghdr.type(fp)
                files = {'file': (fname, fp, 'image/%s' % type, {'Expires': '0'})}
                res = file_server.put_file(fid, files)
                return res
            else:
                if rec.fid and file_server.file_exists(rec.fid):
                    res = file_server.del_file(rec.fid)
                    return res
                return True


class FileMixin(models.AbstractModel):
    _name = 'file.mixin'
    _description = "File Mixin"

    file_url = fields.Char('File URL', readonly=True)
    internal_file_url = fields.Char('Internal File URL', readonly=True)
    fid = fields.Char('File FID', readonly=True)
    update_trigger = fields.Char('Trigger')

    _sql_constraints = [
        ('fid_unique', 'UNIQUE(fid)', 'You can not have two files with the same fid !')
    ]

    @api.multi
    @file_server
    def unlink(self, **kwargs):
        file_server = kwargs.get('file_server')
        if not file_server:
            return False

        for rec in self:
            if rec.fid and file_server.file_exists(rec.fid):
                res = file_server.del_file(rec.fid)

        return super(FileMixin, self).unlink()

    @api.multi
    @file_server
    def _store_file(self, **kwargs):
        file_server = kwargs.get('file_server')
        if not file_server:
            return False

        for rec in self:
            fname = rec.datas_fname
            print(fname)
            if not file_server:
                return False
            datas = rec.datas
            if datas:
                fid = rec.fid
                if not fid:
                    fid = file_server.get_fid().get('fid')

                file_url = file_server.public + '/%s' % fid
                internal_file_url = file_server.volume + '/%s' % fid
                val = {
                    'fid': fid,
                    'file_url': file_url,
                    'internal_file_url': internal_file_url
                }
                rec.update(val)
                data = str.encode(datas) if isinstance(datas, str) else datas
                fp = base64.decodebytes(data)
                files = {'file': (fname, fp,rec.mimetype, {'Expires': '0'})}
                res = file_server.put_file(fid, files)
                return res


class IrAttachment(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment','file.mixin']
