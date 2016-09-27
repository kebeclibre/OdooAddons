# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import timedelta

import random
# from openerp.base import res_partner

# class lpe-openacademy(models.Model):
#     _name = 'lpe-openacademy.lpe-openacademy'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
# Adress Tuto : https://www.odoo.com/documentation/9.0/howtos/backend.html


class Session(models.Model):
    _name = 'lpeopenacademy.session'
    _inherit = ['mail.thread']

    
    participant_ids = fields.Many2many('res.partner', string='Participants')
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    #duration = fields.Float(compute='_compute_duration', inverse="_compute_end_date", digits=(6, 2), help="Duration in days")
    end_date = fields.Date(compute='_compute_end_date', inverse="_compute_duration", string='End Date', store='True')
    seats = fields.Integer(string="Number of seats")
    occupied_seats = fields.Float(compute='_compute_occupied', string="Percentage Occupied")
    available_seats = fields.Integer(compute='_compute_available', string="Available Seats")
    active = fields.Boolean(default=True)
    color = fields.Integer()

    name = fields.Char(compute='_compute_name', string='Session name', store="True")

    # def _read_group_course_id(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
    #     course_obj = self.pool.get('lpeopenacademy.course')
    #     course_ids = course_obj._search(cr, uid, domain, access_rights_uid=access_rights_uid, context=context)
    #     # import pdb;pdb.set_trace()
    #     #courses = self.pool.get('lpeopenacademy.course').name_get(cr, access_rights_uid, context=context)
    #     courses = course_obj.name_get(cr, access_rights_uid, course_ids, context=context)
    #     #courses = self.env['lpeopenacademy.course'].search([]).name_get()
    #     fold = {}
    #     for c_id in course_ids:
    #         fold[c_id] = True
    #     return courses, fold

    @api.multi
    def _read_group_course_id(self,domain, read_group_order=None, access_rights_uid=None):
        courses = self.env['lpeopenacademy.course'].search([]).name_get()
        return courses, None

    _group_by_full = {
    #'course_id': _read_group_course_id
    'course_id' : _read_group_course_id,
    }

    course_id = fields.Many2one('lpeopenacademy.course', ondelete='cascade', string='Course', required="True")


    @api.depends('course_id')   
    def _compute_name(self):
        for r in self:
            if r.course_id:
                append =  r.course_id.name
            else:
                append = "undefined_course"
            r.name = str(random.randint(1, 1e6)) + '_' + append

    @api.depends('seats', 'participant_ids')
    def _compute_available(self):
        for r in self:
            r.available_seats = r.seats - len(r.participant_ids)

    @api.depends('seats', 'participant_ids')
    def _compute_occupied(self):
        for r in self:
            if not r.seats:
                r.occupied_seats = 0.0
            else:
                r.occupied_seats = 100.0 * len(r.participant_ids) / r.seats

    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue
            start = fields.Datetime.from_string(r.start_date)
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = start + duration

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue
            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date - start_date).days + 1

    @api.onchange('participant_ids')
    def _on_change_participant_ids(self):
        for r in self:
            followers = r.message_follower_ids.mapped('partner_id')
            participants = r.participant_ids
            r.message_subscribe(self, partner_ids=participants-followers)
            r.message_unsubscribe(self, partner_ids=followers-participants)

            # if diff in participants:
            #     r.message_subscribe(self, partner_ids=diff)
            # else:
            #   lowers - part)




class Course(models.Model):
    _name = 'lpeopenacademy.course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    responsible_id = fields.Many2one('res.partner', string='Instructor')
    session_ids = fields.One2many('lpeopenacademy.session', 'course_id', string="Sessions")
