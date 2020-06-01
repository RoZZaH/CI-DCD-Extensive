from flask_assets import Bundle

bundles = {
    "home_css" : Bundle(
        "normalize.css",
        "main.scss",
        "tags.css",
        filters= "libsass", #"cssmin",
        depends= "*.scss",
        output="gen/home.%(version)s.css"
    ),
    "org_band_js": Bundle(
        "tags.js",
        "autofill.js",
        "hometown.js",
        "formlets.js",
        "genre_tags.js",
        #filters= "jsmin",
        #output="gen/home.%(version)s.js"
    )
}

