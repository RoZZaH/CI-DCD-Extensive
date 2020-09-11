from flask_assets import Bundle

bundles = {
    "home_css" : Bundle(
        "./css/libs/intlTelInput.css",
        "./css/libs/normalize.css",
        "./css/libs/tags.css",
        "./css/main.scss",
        filters= "libsass", #"cssmin",
        depends= "./css/*.scss",
        output="gen/home.%(version)s.css"
    ),
    "form_css" : Bundle(
        "./css/libs/intlTelInput.css",
        "./css/libs/normalize.css",
        "./css/libs/tags.css",
        "./css/form.scss",
        filters= "libsass", #"cssmin",
        depends= "./css/*.scss",
        output="gen/form.%(version)s.css"
    ),
    "org_band_js": Bundle(
        "./js/libs/jquery.min.js", #v3.3.1
        "./js/libs/tags.js",
        "./js/libs/autofill.js",
        "./js/libs/intlTelInput.min.js",
        "./js/hometown.js",
        "./js/formlets.js",
        "./js/genre_tags.js",
        #filters= "jsmin",
        #output="gen/home.%(version)s.js"
    )
}

