from flask import request, current_app
from dominate import tags
from dominate.util import raw
from flask_nav import Nav, register_renderer
from flask_nav.elements import Navbar, Subgroup, Text, Link, RawTag, Separator, NavigationItem
from flask_nav.elements import View as _View
from flask_nav.renderers import Renderer

nav = Nav()

class View(_View):
    def __init__(self, text, endpoint, parent=None, **kwargs):
        self.text = text
        self.endpoint = endpoint
        self.parent = parent
        self.url_for_kwargs = kwargs


class SuperGroup(NavigationItem):
    def __init__(self, title, items):
        self.title = title
        self.items = items


class Alpha(_View):
    def __init__(self, text, endpoint, parent=None, **kwargs):
        self.text = text
        self.endpoint = endpoint
        self.parent = parent
        self.url_for_kwargs = kwargs

    @property
    def active(self):
        return request.path[:5] == self.get_url()


mobile_first_in = Navbar('title',
    View('Home', 'public.results'),
    SuperGroup(
    View('Bands', 'public.results'),
    items=(
        Alpha('Bands A-Z', 'public.a2z', 'bands'),
        View('Bands by Location', 'public.by_location', 'bands'),
        View('Bands by Genre', 'public.by_genre', 'bands') )
    ),
    SuperGroup(
    View('Manage', 'manage.redirector'),
    items=(
        View('Bands', 'manage.manage_bands_home', 'manage'), )
    ),
    View('Search', 'public.search'),
    View('Settings', 'user.account'),
    View('Logout', 'user.logout')
)


mobile_first_out = Navbar('title',
    View('Home', 'public.results'),
    SuperGroup(
    View('Bands', 'public.results'),
    items=(
        Alpha('Bands A-Z', 'public.a2z', 'bands'),
        View('Bands by Location', 'public.by_location', 'bands'),
        View('Bands by Genre', 'public.by_genre', 'bands') )
    ),
    View('Search', 'public.search'),
    View('Register', 'user.register'),
    View('Sign In', 'user.login'),
)

def sanitise_for_css(nodetext):
    return nodetext.strip().replace(' ', '-').lower()

class JustLiRenderer(Renderer):
    def visit_Navbar(self, node):
        ul = tags.ul(_id="gns")
        for item in node.items:
            ul.add(self.visit(item))
        return ul

    def visit_View(self, node):
        li = tags.li(_id = ( node.parent+'-' if node.parent else '' )+sanitise_for_css(node.text))
        if node.parent:
            li['class'] = 'child'
        if node.active and node.parent:
            li['class'] = 'child active'
        if node.active:
            li['class'] = 'active'
        a = li.add(tags.a(node.text, href=node.get_url() ))
        return li


    def visit_VText(self, node):
        li = tags.li()
        if node.active:      
            li['class'] = 'active'
        a = li.add(tags.a(node.text, href=node.get_url() ))
        return li
    
    
    def visit_Link(self, node):
        li = tags.li(_class='extLink')
        a = li.add(tags.a(node.text, href=node.get_url()))
        return li


    def visit_SuperGroup(self, node):
        li = tags.li(_id=sanitise_for_css(node.title.text), _class="parent")
        if node.title.active:
            li['class'] = 'parent active'
        a = li.add(tags.a(node.title.text, href=node.title.get_url()))        
        ul = tags.ul(*[self.visit(item) for item in node.items])
        ul2 = li.add(ul)
        return li
        

    def visit_Separator(self, node):
        return tags.li('---')


    def visit_Subgroup(self, node):
        li = tags.li(node.title, _class="nested")
        ul2 = tags.ul(*[self.visit(item) for item in node.items])
        lis2 = li.add(ul2)
        return li

    def visit_RawTag(self, node):
        return raw(node.content)


nav.register_element('mob_in', mobile_first_in)
nav.register_element('mob_out', mobile_first_out)

def initialise_nav(app):
    register_renderer(app, 'just_li', JustLiRenderer)
    nav.init_app(app)
