from flask import request, url_for

def get_nav_links():
    """Return navigation links based on the current request path."""
    navs = {
        "/welcome": [
            {'type': 'link', 'name': 'Home', 'url': url_for('app.welcome'), 'submenu': None},
            {'type': 'dropdown', 'name': 'Load', 'url': '#', 'submenu': [
                {'name': 'Open Design', 'action': "redirectToIndex('openDesign')", 'type': 'button'},
                {'name': 'Load Material', 'action': "document.getElementById('materialFileInput').click();", 'type': 'button'},
            ]},
            {'type': 'link', 'name': 'All Designs', 'url': url_for('app.public_designs'), 'submenu': None},
            {'type': 'link', 'name': 'Help', 'url': url_for('app.help'), 'submenu': None}
        ],
        "/": [
            {'type': 'link', 'name': 'Home', 'url': url_for('app.welcome'), 'submenu': None},
            {'type': 'dropdown', 'name': 'Load', 'url': '#', 'submenu': [
                {'name': 'Open Design', 'action': "openDesign()", 'type': 'button'},
                {'name': 'Load Material', 'action': "document.getElementById('materialFileInput').click();", 'type': 'button'},
            ]},
            {'type': 'button', 'name': 'Save', 'action': 'saveDesign()'},
            {'type': 'dropdown', 'name': 'Downloads', 'url': '#', 'submenu': [
                {'name': 'Graph (JPEG)', 'action': "downloadGraph()", 'type': 'button'},
                {'name': 'Data (CSV)', 'action': "downloadCSV()", 'type': 'button'},
                {'name': 'Data (PDF)', 'action': "downloadPDF()", 'type': 'button'},
                {'name': 'Design (JSON)', 'action': "downloadDesignJSON()", 'type': 'button'},
            ]},
            {'type': 'dropdown', 'name': 'Results', 'url': '#', 'submenu': [
                {'name': 'Show Transmittance', 'action': "showTransmittance()", 'type': 'button'},
                {'name': 'Show Reflectance', 'action': "showReflectance()", 'type': 'button'},
                # {'name': 'Color Chart', 'action': "openColorChart()", 'type': 'button'},
            ]},
            {'type': 'link', 'name': 'All Designs', 'url': url_for('app.public_designs'), 'submenu': None},
            {'type': 'link', 'name': 'Help', 'url': url_for('app.help'), 'submenu': None}
        ],
        "/help": [
            {'type': 'link', 'name': 'Home', 'url': url_for('app.welcome'), 'submenu': None},
            {'type': 'link', 'name': 'Load Design', 'url': url_for('app.load_design'), 'submenu': None},
            {'type': 'link', 'name': 'Help', 'url': url_for('app.help'), 'submenu': None},
        ],
        "/materials": [
            {'type': 'link', 'name': 'Home', 'url': url_for('app.welcome'), 'submenu': None},
            {'type': 'button', 'name': 'Upload Material', 'action': "document.getElementById('materialFileInput').click();"},
            {'type': 'link', 'name': 'Set Up Environment', 'url': url_for('app.welcome'), 'submenu': None},
            {'type': 'link', 'name': 'Help', 'url': url_for('app.help'), 'submenu': None},
            {'type': 'link', 'name': 'Documentation', 'url': "/static/files/Documentation.pdf", 'download': 'Documentation.pdf', 'submenu': None}
        ],
        "/public_designs": [
            {'type': 'link', 'name': 'Home', 'url': url_for('app.welcome'), 'submenu': None},
            {'type': 'link', 'name': 'New Design', 'url': url_for('app.index'), 'submenu': None},
        ],
    }

    return navs[request.path]
