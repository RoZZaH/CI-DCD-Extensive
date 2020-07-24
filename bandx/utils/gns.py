from flask import request
from dominate import tags
from dominate.util import raw
from flask_nav import Nav, register_renderer
from flask_nav.elements import Navbar, Subgroup, Text, Link, RawTag, Separator, NavigationItem
from flask_nav.elements import View as _View
from flask_nav.renderers import Renderer

nav = Nav()


class View(_View):
    pass



class SuperGroup(NavigationItem):
    def __init__(self, title, items):
        self.title = title
        self.items = items

class Alpha(_View):
    def __init__(self, text, endpoint, **kwargs):
        self.text = text
        self.endpoint = endpoint
        self.url_for_kwargs = kwargs

    @property
    def active(self):
        return request.path[:5] == self.get_url()


topbar = Navbar('title',
    SuperGroup(
    View('Bands', 'public.results'),
    items=(
        View('Bands A-Z', 'public.a2z', initial='a'),
        View('Bands by Location', 'public.by_location') )
    ),
    View('Search', 'public.search'),
)

mobile_first_in = Navbar('title',
    SuperGroup(
    View('Bands', 'public.results'),
    items=(
        Alpha('Bands A-Z', 'public.a2z'),
        View('Bands by Location', 'public.by_location') )
    ),
    Subgroup('Manage',
        View('Bands', 'manage.manage_bands_home')),
    View('Search', 'public.search'),
    View('Settings', 'user.account'),
    View('Logout', 'user.logout')
)


mobile_first_out = Navbar('title',
    SuperGroup(
    View('Bands', 'public.results'),
    items=(
        Alpha('Bands A-Z', 'public.a2z'),
        View('Bands by Location', 'public.by_location') )
    ),
    View('Search', 'public.search'),
    View('Register', 'user.register'),
    View('Sign In', 'user.login'),
)


class GnsRenderer(Renderer):
    def visit_Navbar(self, node):
        nav_tag = tags.nav(_class="primary-nav")
        ul = nav_tag.add(tags.ul(_class="level1"))

        # sub = []
        for item in node.items:
            ul.add(self.visit(item))

        return nav_tag #.add(*sub)

    def visit_View(self, node):
        li = tags.li(_class='testclass')
        if node.active:
            li['class'] = 'active'
        a = li.add(tags.a(node.text, href=node.get_url() ))
        return li


    def visit_Text(self, node):
        return tags.li(node.text, _class='textOnly')
    
    
    def visit_Link(self, node):
        li = tags.li(_class='extLink')
        a = li.add(tags.a(node.text, href=node.get_url()))
        return li


    def visit_SuperGroup(self, node):
        li = tags.li()
        # if node.title.get_url() == "/":
        if node.title.active:      
            li['class'] = 'active'
        #attrs = vars(node)
        # print(', '.join("%s: %s" % item for item in attrs.items()))
        a = li.add(tags.a(node.title.text, href=node.title.get_url()))
        ul = tags.ul(*[self.visit(item) for item in node.items], _class="level2")
        # ul = a.append(ul)
        ul2 = li.add(ul)
        return li
        

    def visit_Separator(self, node):
        return tags.li('---')


    def visit_Subgroup(self, node):
        # almost the same as visit_Navbar, but written a bit more concise
        # lis = tags.li(node.title)
        ul = tags.ul(*[self.visit(item) for item in node.items])
        return ul

    def visit_RawTag(self, node):
        return raw(node.content)



class JustLiRenderer(Renderer):
    def visit_Navbar(self, node):
        nav_tag = tags.nav(_class="some-class navbar")
        ul = nav_tag.add(tags.ul())
        # sub = []
        for item in node.items:
            ul.add(self.visit(item))

        return nav_tag #.add(*sub)

    def visit_View(self, node):
        li = tags.li()
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
        li = tags.li(_class="subNav")
        if node.title.active:
            li['class'] = 'active'
        a = li.add(tags.a(node.title.text, href=node.title.get_url()))
        ul = tags.ul(*[self.visit(item) for item in node.items])
        # ul = a.append(ul)
        ul2 = li.add(ul)
        return li
        

    def visit_Separator(self, node):
        return tags.li('---')


    def visit_Subgroup(self, node):
        # almost the same as visit_Navbar, but written a bit more concise
        li = tags.li(node.title, _class="subNav") #_class="some-class navbar"
        ul2 = tags.ul(*[self.visit(item) for item in node.items]) #_class="subgrouper"
        lis2 = li.add(ul2)
        return li

    def visit_RawTag(self, node):
        return raw(node.content)



secondary_in = Navbar('',
    View('Manage Bands', 'manage.manage_bands_home'),
    View('Settings', 'user.account'),
    View('Log Out', 'user.logout'),
    View('PhoneTest', 'public.form_phone')
)

secondary_out = Navbar('',
    View('Register', 'user.register'),
    View('Login', 'user.login'),
    View('PhoneTest', 'public.form_phone')
)

nav.register_element('gns', topbar)
nav.register_element('sns_in', secondary_in)
nav.register_element('sns_out', secondary_out)
nav.register_element('mob_in', mobile_first_in)
nav.register_element('mob_out', mobile_first_out)

def initialise_nav(app):
    register_renderer(app, 'just_li', JustLiRenderer)
    register_renderer(app, 'just_gns', GnsRenderer)
    # register_renderer(app, 'just_gns', GnsRenderer)
    nav.init_app(app)



# class UserGreeting(View):
#     def __init__(self, text, endpoint, **kwargs):
#         self.text = text
#         self.endpoint = endpoint
#         self.url_for_kwargs = kwargs

#     # @property
#     def text(self):
#         return tags.div('{} ({})'.format(self.text, self.get_url()))

# class JustDivRenderer(Renderer):
#     def visit_Navbar(self, node):
#         sub = []
#         for item in node.items:
#             sub.append(self.visit(item))

#         return tags.div('Navigation:', *sub)

#     def visit_View(self, node):
#         return tags.div('{} ({})'.format(node.title.text, node.title.get_url()))

#     def visit_Subgroup(self, node):
#         # almost the same as visit_Navbar, but written a bit more concise
#         return tags.div(node.title,
#                         *[self.visit(item) for item in node.items])


# https://www.solodev.com/blog/web-design/converting-horizontal-navigation-into-mobile-dropdown-menus.stml
	# <select name="sectional_nav" id="sectional_nav" class="form-control hidden-md-up" onchange="window.location.href=this.value">
	#   <option value="0">Navigate to...</option>
	#   <option value="https://www.solodev.com/pricing/">Pricing</option>
	#   <option value="https://www.solodev.com/product/create.stml">Product</option>
	#   <option value="https://www.solodev.com/resources/">Resources</option>
	#   <option value="https://www.solodev.com/customers/">Customers</option>
	#   <option value="https://www.solodev.com/blog/">Blog</option>
	# </select>