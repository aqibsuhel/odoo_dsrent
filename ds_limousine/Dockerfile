FROM odoo:18

# Copy the module (. means current folder = ds_limousine)
COPY . /mnt/extra-addons/ds_limousine

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy Odoo config
COPY odoo.conf /etc/odoo/odoo.conf

EXPOSE 8069

CMD ["odoo", "--config=/etc/odoo/odoo.conf"]
COPY odoo.conf /etc/odoo/odoo.conf
