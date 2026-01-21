{
    'name': 'DS Limousine Service Management',
    'version': '1.3.0',
    'category': 'Services/Limousine',
    'summary': 'Complete Limousine Service Management with Vehicle Integration',
    'description': """
        Limousine Service Management System
        ====================================

        Features:
        ---------
        * Limousine booking management with detailed service lines
        * Integration with Car Rental fleet for vehicle selection
        * Automatic pricing based on selected vehicles
        * Saudi Arabia cities, regions, branches, and airports (pre-loaded)
        * Service products catalog
        * Customer/contact management with Saudi-specific fields
        * Multi-level location hierarchy (Region → City → Branch)
        * Flight and hotel integration
        * Driver management
        * Detailed service line tracking with 25+ fields per service
        * Automatic calculations for hours, taxes, discounts
        * Guest management
        * Vehicle status tracking (Available → Rented → Available)

        Version 1.3.0 Updates:
        ---------------------
        * Enhanced vehicle integration with Car Rental module
        * Dropdown selection for vehicles with auto-populated details
        * Automatic hourly rate calculation from daily rates
        * Vehicle availability checking
        * 20 pre-loaded vehicles (Sedans, SUVs, Luxury cars)
        * Improved service line form with vehicle details display
        * Manual car model entry for vehicles not in system
    """,
    'author': 'DS Development Team',
    'website': 'https://www.dsrentmanagement.com',
    'depends': [
        'base',
        'mail',
        'product',
        'account',
        'ds_car_rental',  # IMPORTANT: Depends on Car Rental module
    ],
    'data': [
        # Security
        'security/limousine_security.xml',
        'security/ir.model.access.csv',

        # Data - Load in specific order
        'data/sequence_data.xml',
        'data/region_data.xml',
        'data/city_data.xml',
        'data/branch_data.xml',
        'data/airport_data.xml',
        'data/service_product_data.xml',
        #'data/vehicle_data.xml',  # NEW: Pre-loaded vehicles

        # Views
        'views/region_views.xml',
        'views/city_views.xml',
        'views/branch_views.xml',
        'views/airport_views.xml',
        'views/service_product_views.xml',
        'views/contact_views.xml',
        'views/booking_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
}