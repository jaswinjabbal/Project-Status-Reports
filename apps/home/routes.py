# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from jinja2 import TemplateNotFound


@blueprint.route('/home')
@login_required
def index():

    return render_template('home/homepage.html', segment='home')


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


# Added below routes per page requirements

from apps.authentication.models import *
from apps import db

@blueprint.route('/db')
@login_required
def show_db():
    # Query the data
    # This is where we perform CRUD operations
    results = ElectronicPart.query.all()

    # Prepare data for rendering
    columns = ElectronicPart.__table__.columns.keys()
    data = [[getattr(row, col) for col in columns] for row in results]

    return render_template('db.html', data=data, columns=columns)

'''
@blueprint.route('/parts_table')
def parts_table():
    parts = ElectronicPart.query.all()  # Fetch all parts from the database
    return render_template('parts_table.html', parts=parts)


@blueprint.route('/add_part', methods=['GET', 'POST'])
def add_part():
    if request.method == 'POST':
        # Retrieve form data
        part_number = request.form.get('partNumber')
        description = request.form.get('description')
        category = request.form.get('category')
        manufacturer = request.form.get('manufacturer')
        vendor = request.form.get('vendor')
        cost = request.form.get('cost')

        # Ensure fields are not empty
        if not part_number or not cost:
            flash("Part Number and Cost are required fields.")
            return redirect(url_for('add_part'))

        # Add part to the database
        try:
            new_part = ElectronicPart(
                part_number=part_number,
                description=description,
                category=category,
                manufacturer=manufacturer,
                vendor=vendor,
                cost=cost
            )
            db.session.add(new_part)
            db.session.commit()
            flash("Part added successfully!")
            return redirect(url_for('view_parts'))  # Redirect to parts table
        except Exception as e:
            db.session.rollback()
            flash("Failed to add part: " + str(e))
            return redirect(url_for('add_part'))

    # Render the form page if GET request
    return render_template('add_part.html')

@blueprint.route('/view_parts')
def view_parts():
    parts = ElectronicPart.query.all()  # Fetch all parts from the database
    return render_template('parts_table.html', parts=parts)  # Display parts in a table

@blueprint.route('/vendor_update', methods=['GET']) ####################
def vendor_update():
    part_number = request.form.get('partNumber')
    vendor_name = request.form.get('vendorName')
    # Placeholder logic for "Digikey API" interaction
    updated_parts = [
        {"partNumber": "ABC123", "description": "Sample Part 1", "vendor": vendor_name, "updatedAt": "Placeholder Date"},
        {"partNumber": "XYZ789", "description": "Sample Part 2", "vendor": vendor_name, "updatedAt": "Placeholder Date"},
        {"partNumber": "MNO456", "description": "Sample Part 3", "vendor": vendor_name, "updatedAt": "Placeholder Date"},
    ]
    return render_template('update_vendor.html', updated_parts=updated_parts)

''''''
@blueprint.route('/export_part', methods=['GET', 'POST'])
def export_part():
    if request.method == 'POST':
        export_method = request.form['export_method']
        part_number = request.form['part_number']

        # Example logic
        if export_method == 'database':
            flash(f"Part {part_number} exported to the database!", "success")
            return redirect(url_for('view_db'))
        elif export_method == 'mail':
            flash(f"Part {part_number} sent via email!", "info")
            return redirect(url_for('export_part'))

    return render_template('export_part.html')
'''
'''
@blueprint.route('/db')
def db_view():
    parts = ElectronicPart.query.all()  # Fetch all parts from the database
    return render_template('db.html', parts=parts)
'''
'''
@blueprint.route('/import_part', methods=['GET', 'POST'])
def import_part():
    if request.method == 'POST':
        file = request.files['file']
        # Example for parsing CSV
        if file:
            import csv
            reader = csv.DictReader(file)
            for row in reader:
                part = ElectronicPart(
                    name=row['name'],
                    description=row.get('description'),
                    quantity=row.get('quantity', 0),
                    category=row.get('category')
                )
                db.session.add(part)
            db.session.commit()
            flash('Parts imported successfully!')
            log = ImportLog(source='CSV', details=f"Imported {file.filename}")
            db.session.add(log)
            db.session.commit()
        return redirect(url_for('view_parts'))
    return render_template('import_part.html')
'''
'''
if __name__ == '__main__':
    with blueprint.app_context():
        db.create_all()
    blueprint.run(debug=True)

'''