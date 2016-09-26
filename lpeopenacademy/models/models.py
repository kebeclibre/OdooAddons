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

    course_id = fields.Many2one('lpeopenacademy.course', ondelete='cascade', string='Course', required="True")
    participant_ids = fields.Many2many('res.partner', String='Participants')
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


class Course(models.Model):
    _name = 'lpeopenacademy.course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    responsible_id = fields.Many2one('res.partner', string='Instructor')
    session_ids = fields.One2many('lpeopenacademy.session', 'course_id', string="Sessions")
