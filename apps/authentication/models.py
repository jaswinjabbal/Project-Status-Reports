# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
 
# Added below classes per mySQL schema

from apps import db

# Table: electronic_parts_categories
class ElectronicPartCategory(db.Model):
    __tablename__ = 'electronic_parts_categories'

    id = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(255), nullable=True)
    description = db.Column('Description', db.String(255), nullable=True)

    def __repr__(self):
        return f'<Category {self.name}>'

# Table: electronic_parts_manufacturers
class ElectronicPartManufacturer(db.Model):
    __tablename__ = 'electronic_parts_manufacturers'

    id = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(255), nullable=True)
    url = db.Column('URL', db.String(255), nullable=True)
    street_address = db.Column('Street Address', db.String(255), nullable=True)
    city = db.Column('City', db.String(255), nullable=True)
    state = db.Column('State', db.String(255), nullable=True)
    zip = db.Column('Zip', db.String(255), nullable=True)
    contact = db.Column('Contact', db.String(255), nullable=True)
    approved = db.Column('Approved', db.String(255), nullable=True)
    phone = db.Column('Phone', db.String(255), nullable=True)
    fax = db.Column('Fax', db.String(255), nullable=True)
    notes = db.Column('Notes', db.String(255), nullable=True)
    other = db.Column('Other', db.String(255), nullable=True)

    def __repr__(self):
        return f'<Manufacturer {self.name}>'

# Table: electronic_parts_projects
class ElectronicPartProject(db.Model):
    __tablename__ = 'electronic_parts_projects'

    id = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(255), nullable=True)
    description = db.Column('Description', db.String(255), nullable=True)
    charge_number = db.Column('Charge Number', db.String(255), nullable=True)
    project_lead = db.Column('Project Lead', db.String(255), nullable=True)
    notes = db.Column('Notes', db.String(255), nullable=True)

    def __repr__(self):
        return f'<Project {self.name}>'

# Table: electronic_parts_vendors
class ElectronicPartVendor(db.Model):
    __tablename__ = 'electronic_parts_vendors'

    id = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Name', db.String(255), nullable=True)
    url = db.Column('URL', db.String(255), nullable=True)
    street_address = db.Column('Street Address', db.String(255), nullable=True)
    city = db.Column('City', db.String(255), nullable=True)
    state = db.Column('State', db.String(255), nullable=True)
    zip = db.Column('Zip', db.String(255), nullable=True)
    contact = db.Column('Contact', db.String(255), nullable=True)
    approved = db.Column('Approved', db.String(255), nullable=True)
    phone = db.Column('Phone', db.String(255), nullable=True)
    fax = db.Column('Fax', db.String(255), nullable=True)
    notes = db.Column('Notes', db.String(255), nullable=True)
    other = db.Column('Other', db.String(255), nullable=True)

    def __repr__(self):
        return f'<Vendor {self.name}>'

# Table: electronics_parts
class ElectronicPart(db.Model):
    __tablename__ = 'electronics_parts'

    id = db.Column('ID', db.Integer, primary_key=True)
    part_description = db.Column('Part Description', db.Text, nullable=True)
    manufacturer = db.Column('Manufacturer', db.String(255), nullable=True)
    manufacturer_part_number = db.Column('Manufacturer Part Number', db.String(255), nullable=True)
    supplier_1 = db.Column('Supplier 1', db.String(255), nullable=True)
    supplier_part_number_1 = db.Column('Supplier Part Number 1', db.String(255), nullable=True)
    part_category = db.Column('Part Category', db.String(255), nullable=True)
    rohs_compliant = db.Column('RoHS Compliant', db.Boolean, nullable=False)
    cost_1pc = db.Column('Cost 1pc', db.Float, nullable=True)
    cost_100pc = db.Column('Cost 100pc', db.Float, nullable=True)
    cost_1000pc = db.Column('Cost 1000pc', db.Float, nullable=True)
    library_ref = db.Column('Library Ref', db.String(50), nullable=True)
    library_path = db.Column('Library Path', db.String(255), nullable=True)
    primary_vendor_stock = db.Column('Primary Vendor Stock', db.Integer, nullable=True)

    def __repr__(self):
        return f'<ElectronicPart {self.part_description}>'
