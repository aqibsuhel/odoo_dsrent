FROM odoo:18

USER root

COPY ./ds_limousine /mnt/extra-addons/ds_limousine

RUN chown -R odoo:odoo /mnt/extra-addons/ds_limousine

USER odoo
