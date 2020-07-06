from dominate import tags
from dominate.util import raw
from flask_nav import Nav, register_renderer
from flask_nav.elements import Navbar, Subgroup, Text, Link, View, RawTag, Separator, NavigationItem
from flask_nav.renderers import Renderer

nav = Nav()



class UserGreeting(View):
    def __init__(self, text, endpoint, **kwargs):
        self.text = text
        self.endpoint = endpoint
        self.url_for_kwargs = kwargs

    # @property
    def text(self):
        return tags.div('{} ({})'.format(self.text, self.get_url()))

class SuperGroup(NavigationItem):
    def __init__(self, title, items):
        self.title = title
        self.items = items
    
# class SG2(NavigationItem):
#     def __init__(self, title, *items):
#         self.title = title
#         self.items = items

topbar = Navbar('title',
    View('Home', 'public.home'),
    View('Tours', 'manage.manage_bands_home'),
    View('Register', 'user.register'),
    UserGreeting('Sam', 'user.login'),
    # Separator(),
    # RawTag(content='<li>'),
    SuperGroup(title=View('Tours', 'public.home'), 
    items=(
        Text('Some desc text'),
        Link('a yahoo link', 'https://mail.yahoo.com/'),
        View('Manage', 'manage.manage_bands_home')
    )
    ),
    # Subgroup('',
    #     Text('Some desc text'),
    #     Link('a yahoo link', 'https://mail.yahoo.com/'),
    #     View('Manage', 'bands.manage_bands')
    # ),
    # RawTag(content='</li>'),
)






class JustDivRenderer(Renderer):
    def visit_Navbar(self, node):
        sub = []
        for item in node.items:
            sub.append(self.visit(item))

        return tags.div('Navigation:', *sub)

    def visit_View(self, node):
        return tags.div('{} ({})'.format(node.title.text, node.title.get_url()))

    def visit_Subgroup(self, node):
        # almost the same as visit_Navbar, but written a bit more concise
        return tags.div(node.title,
                        *[self.visit(item) for item in node.items])



        

class JustLiRenderer(Renderer):
    def visit_Navbar(self, node):
        nav_tag = tags.nav(_class='navbar navbar-inverse navbar-fixed-top')
        ul = nav_tag.add(tags.ul())

        # sub = []
        for item in node.items:
            ul.add(self.visit(item))

        return nav_tag #.add(*sub)

    def visit_View(self, node):
        li = tags.li(_class='testclass')
        if node.active:
            li['class'] = 'active'
        a = li.add(tags.a(node.text, href=node.get_url(), _class='dd'))
        return li


    def visit_Text(self, node):
        return tags.li(node.text, _class='teXtclass')
    
    
    def visit_Link(self, node):
        li = tags.li(_class='extLink')
        a = li.add(tags.a(node.text, href=node.get_url()))
        return li


    def visit_SuperGroup(self, node):
        li = tags.li(_class="subNav")
        a = li.add(tags.a(node.title.text, href=node.title.get_url()))
        ul = tags.ul(*[self.visit(item) for item in node.items])
        # ul = a.append(ul)
        ul2 = li.add(ul)
        return li
        
        return 


    def visit_Separator(self, node):
        return tags.li('---')


    def visit_Subgroup(self, node):
        # almost the same as visit_Navbar, but written a bit more concise
        # lis = tags.li(node.title)
        ul = tags.ul(*[self.visit(item) for item in node.items])
        return ul

    def visit_RawTag(self, node):
        return raw(node.content)


secondary_in = Navbar('',
    View('Manage Bands', 'manage.manage_bands_home'),
    View('Settings', 'user.account'),
    View('Log Out', 'user.logout'),
)

secondary_out = Navbar('',
    View('Register', 'user.register'),
    View('Login', 'user.login'),
)

nav.register_element('gns', topbar)
nav.register_element('sns_in', secondary_in)
nav.register_element('sns_out', secondary_out)

def initialise_nav(app):
    register_renderer(app, 'just_div', JustDivRenderer)
    register_renderer(app, 'just_li', JustLiRenderer)
    nav.init_app(app)