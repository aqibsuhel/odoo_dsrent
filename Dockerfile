FROM odoo:18

COPY ./ds_limousine /mnt/extra-addons/ds_limousine
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

EXPOSE 8069
COPY odoo.conf /etc/odoo/odoo.conf
